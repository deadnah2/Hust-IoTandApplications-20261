from typing import List
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.api import deps
from app.models.user import User
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceCommand, NewDeviceInLAN
from app.services.device import DeviceService
from app.services.camera import CameraStream
from app.services.activity_log import ActivityLogService
from app.api.utils import device_to_response
import asyncio
import cv2

logger = logging.getLogger(__name__)
router = APIRouter()
DEVICE_OFFLINE_SECONDS = 7

# Global dict để lưu các camera stream đang chạy
active_camera_streams = {}

# GET specific endpoints BEFORE generic ones
@router.get("/lan", response_model=List[DeviceResponse])
async def get_new_devices_in_lan(
    bssid: str,
):
    devices = await DeviceService.get_new_devices_in_lan(bssid)
    logger.info(f"🔍 Found {len(devices)} devices in LAN with BSSID: {bssid}")
    for device in devices:
        logger.info(f"  - Device: {device.name} ({device.type}) - MAC: {device.controllerMAC}")
    return [device_to_response(device) for device in devices]

@router.get("/unassigned", response_model=List[DeviceResponse])
async def get_unassigned_devices(
    current_user: User = Depends(deps.get_current_user)
):
    """Get all devices not assigned to any room"""
    devices = await Device.find(Device.roomId == None).to_list()
    return [device_to_response(device) for device in devices]


# Generic endpoints AFTER specific ones
# for testing
@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_in: DeviceCreate,
    current_user: User = Depends(deps.get_current_user)
):
    device = await DeviceService.create_device(device_in)
    if not device:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to add device to this room"
        )
    return device_to_response(device)

@router.get("/", response_model=List[DeviceResponse])
async def read_devices(
    roomId: str,
    current_user: User = Depends(deps.get_current_user)
):
    devices = await DeviceService.get_devices_by_room(roomId, current_user)
    return [device_to_response(device) for device in devices]

# Camera stream - phải đặt TRƯỚC /{device_id} để tránh conflict
@router.get("/camera-stream")
async def camera_stream(
    device_id: str,
    current_user: User = Depends(deps.get_current_user_from_query)
):
    device = await DeviceService.get_device_by_id(device_id, current_user)
    if not device or not device.streamUrl:
        raise HTTPException(
            status_code=404,
            detail="Device not found or no stream URL"
        )

    # Khởi tạo CameraStream với deviceId
    stream = CameraStream(
        device.streamUrl, 
        deviceId=device_id,
        humanDetectionMode=device.humanDetectionEnabled or False
    )
    stream.start()
    
    # Lưu stream vào dict
    active_camera_streams[device_id] = stream
    
    # Background task để cập nhật FPS vào database mỗi 2 giây
    async def update_fps_task():
        while device_id in active_camera_streams:
            try:
                fps = stream.get_fps()
                if fps > 0:
                    # Cập nhật fps vào database
                    from beanie import PydanticObjectId
                    device_obj = await Device.get(PydanticObjectId(device_id))
                    if device_obj:
                        await device_obj.update({"$set": {"fps": fps}})
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error updating FPS: {e}")
                break
    
    # Chạy background task
    asyncio.create_task(update_fps_task())

    async def generate():
        try:
            while stream.running:
                frame = stream.get_processed_frame()
                if frame is not None:
                    # JPEG quality 70 để giảm kích thước, tăng tốc độ encode
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    if ret:
                        try:
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
                            # Client đã ngắt kết nối
                            logger.info(f"Client disconnected from camera stream: {device_id} - {e}")
                            break
                        except Exception as e:
                            logger.error(f"Stream error: {e}")
                            break
                
                await asyncio.sleep(0.05)  
        except asyncio.CancelledError:
            # Request bị cancel (client disconnect)
            logger.info(f"Stream cancelled for device: {device_id}")
        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}")
        finally:
            stream.stop()
            # Xóa stream khỏi dict
            if device_id in active_camera_streams:
                del active_camera_streams[device_id]
            logger.info(f"✅ Camera stream stopped and cleaned up for device: {device_id}")

    return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/{device_id}", response_model=DeviceResponse)
async def read_device(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    device = await DeviceService.get_device_by_id(device_id, current_user)
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    return device_to_response(device)

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_in: DeviceUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    # Lấy device trước để check roomId cũ
    old_device = await DeviceService.get_device_by_id(device_id, current_user)
    if not old_device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    old_room_id = old_device.roomId
    
    device = await DeviceService.update_device(device_id, device_in, current_user)
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    
    # Ghi log nếu add device vào room (roomId từ None → có giá trị)
    if device_in.roomId and device.roomId and old_room_id is None:
        from app.services.room import RoomService
        room = await RoomService.get_room_by_id(str(device.roomId), current_user)
        if room:
            await ActivityLogService.create_log(
                action="ADD_DEVICE",
                message=f"Added device {device.name} to room {room.name}",
                userId=str(current_user.id),
                homeId=str(room.homeId)
            )
    
    return device_to_response(device)

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # Lấy thông tin device trước khi xóa
    device = await DeviceService.get_device_by_id(device_id, current_user)
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    
    device_name = device.name
    room_id = device.roomId
    
    success = await DeviceService.delete_device(device_id, current_user)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    
    # Ghi log nếu device có trong room
    if room_id:
        from app.services.room import RoomService
        room = await RoomService.get_room_by_id(str(room_id), current_user)
        if room:
            await ActivityLogService.create_log(
                action="REMOVE_DEVICE",
                message=f"Removed device {device_name} from room {room.name}",
                userId=str(current_user.id),
                homeId=str(room.homeId)
            )
    
    return {"message": "Device deleted successfully"}

@router.post("/{device_id}/command")
async def send_command(
    device_id: str,
    command: DeviceCommand,
    current_user: User = Depends(deps.get_current_user)
):
    logger.info(f"📤 Device command: {device_id} - Action: {command.action}")
    success = await DeviceService.send_command(device_id, command, current_user)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    logger.info(f"✅ Command executed successfully for device: {device_id}")
    return {"message": "Command sent successfully"}