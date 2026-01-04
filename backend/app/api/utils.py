from datetime import datetime
from app.models.home import Home
from app.models.room import Room
from app.models.device import Device
from app.schemas.home import HomeResponse
from app.schemas.room import RoomResponse
from app.schemas.device import DeviceResponse

DEVICE_OFFLINE_SECONDS = 7

# Cache để track trạng thái trước đó (tránh log duplicate)
_device_online_cache: dict[str, bool] = {}
_device_state_cache: dict[str, str] = {}   # Track FAN state (ON/OFF)
_device_speed_cache: dict[str, int] = {}   # Track FAN speed
_temp_alert_cache: dict[str, bool] = {}    # Track temperature alert đã gửi chưa

def home_to_response(home: Home) -> HomeResponse:
    return HomeResponse(
        id=str(home.id),
        name=home.name,
        location=home.location,
        bssid=home.bssid,
        ownerUserId=str(home.ownerUserId),
        createdAt=home.createdAt,
        updatedAt=home.updatedAt
    )


def room_to_response(room: Room) -> RoomResponse:
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        homeId=str(room.homeId),
        bssid=room.bssid,
        createdAt=room.createdAt,
        updatedAt=room.updatedAt
    )

def device_to_response(device: Device) -> DeviceResponse:
    # Xác định trạng thái online dựa trên lastSeen
    is_online = None
    device_id = str(device.id)
    device_type = str(device.type).strip().upper()
    
    if device_type in ("SENSOR", "FAN"):
        if device.lastSeen is None:
            is_online = False
        else:
            delta = datetime.now() - device.lastSeen
            is_online = delta.total_seconds() <= DEVICE_OFFLINE_SECONDS
        
        # Check và log thay đổi online/offline
        was_online = _device_online_cache.get(device_id)
        
        # Chỉ log nếu có thay đổi VÀ device đã được assign vào room
        if was_online is not None and was_online != is_online and device.roomId:
            # Schedule async log (vì function này là sync)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(_log_online_status_change(device, is_online))
            except:
                pass  # Ignore nếu không có event loop
        
        # Update cache
        _device_online_cache[device_id] = is_online
    
    # === LOG FAN state/speed changes ===
    if device_type == "FAN" and device.roomId:
        import asyncio
        
        old_state = _device_state_cache.get(device_id)
        old_speed = _device_speed_cache.get(device_id)
        
        state_changed = old_state is not None and old_state != device.state
        speed_changed = old_speed is not None and old_speed != device.speed
        
        # Log state change (ON/OFF)
        if state_changed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(_log_fan_state_change(device, device.state))
            except:
                pass
        
        # Log speed change - CHỈ khi KHÔNG có state change (tránh log thừa khi turn on/off)
        if speed_changed and not state_changed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(_log_fan_speed_change(device, device.speed))
            except:
                pass
        
        # Update cache
        _device_state_cache[device_id] = device.state
        _device_speed_cache[device_id] = device.speed

    # === CHECK SENSOR TEMPERATURE ALERT ===
    temperature_alert = False
    
    if device_type == "SENSOR" and device.roomId and is_online:
        import asyncio
        
        # Check temperature threshold
        if device.temperatureThreshold is not None and device.temperature is not None:
            if device.temperature > device.temperatureThreshold:
                temperature_alert = True
                # Chỉ log nếu chưa alert trước đó
                was_temp_alert = _temp_alert_cache.get(device_id, False)
                if not was_temp_alert:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(_log_temperature_alert(device))
                    except:
                        pass
            _temp_alert_cache[device_id] = temperature_alert

    return DeviceResponse(
        id=str(device.id),
        roomId=str(device.roomId) if device.roomId else None,
        name=device.name,
        custom_name=device.custom_name,
        controllerMAC=device.controllerMAC,
        bssid=device.bssid,
        type=device.type,
        state=device.state,
        speed=device.speed,
        humanDetectionEnabled=device.humanDetectionEnabled,
        temperature=device.temperature,
        humidity=device.humidity,
        temperatureThreshold=device.temperatureThreshold,
        temperatureAlert=temperature_alert,
        lastSeen=device.lastSeen,
        isOnline=is_online,
        cameraResolution=device.cameraResolution,
        fps=device.fps,
        createdAt=device.createdAt,
        updatedAt=device.updatedAt
    )


async def _log_online_status_change(device: Device, is_online: bool):
    """Helper async function để ghi log online/offline"""
    from app.services.activity_log import ActivityLogService
    
    room = await Room.get(device.roomId)
    if room:
        if is_online:
            await ActivityLogService.create_log(
                action="DEVICE_ONLINE",
                message=f"{device.name} is back online",
                userId=None,
                homeId=str(room.homeId)
            )
        else:
            await ActivityLogService.create_log(
                action="DEVICE_OFFLINE", 
                message=f"{device.name} went offline",
                userId=None,
                homeId=str(room.homeId)
            )


async def _log_fan_state_change(device: Device, new_state: str):
    """Log FAN ON/OFF"""
    from app.services.activity_log import ActivityLogService
    
    room = await Room.get(device.roomId)
    if room:
        action = "FAN_ON" if new_state == "ON" else "FAN_OFF"
        message = f"{device.name} turned {'on' if new_state == 'ON' else 'off'}"
        await ActivityLogService.create_log(
            action=action,
            message=message,
            userId=None,
            homeId=str(room.homeId)
        )


async def _log_fan_speed_change(device: Device, new_speed: int):
    """Log FAN speed change"""
    from app.services.activity_log import ActivityLogService
    
    room = await Room.get(device.roomId)
    if room:
        await ActivityLogService.create_log(
            action="FAN_SET_SPEED",
            message=f"{device.name} speed set to {new_speed}",
            userId=None,
            homeId=str(room.homeId)
        )


async def _log_temperature_alert(device: Device):
    """Log temperature alert khi vượt ngưỡng"""
    from app.services.activity_log import ActivityLogService
    from app.models.activity_log import LogType
    
    room = await Room.get(device.roomId)
    if room:
        await ActivityLogService.create_log(
            action="TEMPERATURE_ALERT",
            message=f"⚠️ {device.name}: Temperature {device.temperature:.1f}°C exceeds threshold {device.temperatureThreshold:.1f}°C",
            userId=None,
            homeId=str(room.homeId),
            log_type=LogType.WARNING
        )