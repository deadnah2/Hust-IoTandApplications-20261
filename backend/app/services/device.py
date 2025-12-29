from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceCommand
from app.services.room import RoomService

class DeviceService:
    @staticmethod
    async def get_device_by_name_and_controller_mac(name: str, controller_mac: str) -> Optional[Device]:
        device = await Device.find_one(
            Device.name == name,
            Device.controllerMAC == controller_mac
        )
        return device

    @staticmethod
    async def create_device(device_in: DeviceCreate) -> Optional[Device]:
        # Verify room ownership if roomId is provided
        # if device_in.roomId:
        #     room = await RoomService.get_room_by_id(device_in.roomId, user)
        #     if not room:
        #         return None  # User doesn't have access to the room

        device_data = device_in.model_dump()
        if device_in.roomId:
            device_data["roomId"] = PydanticObjectId(device_in.roomId)

        device = Device(**device_data)
        await device.create()
        return device

    @staticmethod
    async def get_new_devices_in_lan(bssid: str) -> List[Device]:
        devices = await Device.find(Device.bssid == bssid, Device.roomId == None).to_list()
        return devices

    @staticmethod
    async def get_devices_by_room(room_id: str, user: User) -> List[Device]:
        room = await RoomService.get_room_by_id(room_id, user)
        if not room:
            return []

        devices = await Device.find(Device.roomId == PydanticObjectId(room_id)).to_list()
        return devices

    @staticmethod
    async def get_device_by_id(device_id: str, user: User) -> Optional[Device]:
        device = await Device.get(PydanticObjectId(device_id))
        if device and device.roomId:
            # Verify user has access to the room
            room = await RoomService.get_room_by_id(str(device.roomId), user)
            if room:
                return device
        elif device and not device.roomId:
            # Device not assigned to any room, allow access
            return device
        return None

    @staticmethod
    async def update_device(device_id: str, device_in: DeviceUpdate, user: User) -> Optional[Device]:
        device = await DeviceService.get_device_by_id(device_id, user)
        if not device:
            return None

        update_data = device_in.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow()

        if "roomId" in update_data and update_data["roomId"]:
            # Verify new room ownership
            room = await RoomService.get_room_by_id(update_data["roomId"], user)
            if not room:
                return None
            update_data["roomId"] = PydanticObjectId(update_data["roomId"])

        await device.update({"$set": update_data})
        for key, value in update_data.items():
            setattr(device, key, value)
        return device

    @staticmethod
    async def delete_device(device_id: str, user: User) -> bool:
        device = await DeviceService.get_device_by_id(device_id, user)
        if not device:
            return False

        # Instead of deleting the device, just remove it from the room
        update_data = {"roomId": None, "updatedAt": datetime.utcnow()}
        await device.update({"$set": update_data})
        setattr(device, "roomId", None)
        setattr(device, "updatedAt", update_data["updatedAt"])
        return True

    @staticmethod
    async def send_command(device_id: str, command: DeviceCommand, user: User) -> bool:
        device = await DeviceService.get_device_by_id(device_id, user)
        if not device:
            return False

        # TODO: Publish command to MQTT topic for the device
        # For now, just return True
        return True