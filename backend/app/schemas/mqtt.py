from pydantic import BaseModel, Field
from typing import Optional

# Gói tin ESP32 gửi đến server để cung cấp thông tin thiết bị
class DeviceInfoMessage(BaseModel):
    name: str = Field(..., min_length=1, description="Tên thiết bị")
    controllerMAC: str = Field(..., regex=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", description="MAC address của controller")
    bssid: str = Field(..., description="BSSID của WiFi")
    type: str = Field(..., description="Loại thiết bị (ví dụ: 'sensor', 'actuator')")
    state: str = Field(..., description="Trạng thái thiết bị (ví dụ: 'online', 'offline')")

# Gói tin ESP32 gửi đến server để cung cấp dữ liệu
class DeviceDataMessage(BaseModel):
    name: str = Field(..., min_length=1, description="Tên thiết bị")
    value: str = Field(..., description="Giá trị dữ liệu (có thể là string, số, JSON tùy thiết bị)")
    state: str = Field(..., description="Trạng thái thiết bị")

# Gói tin server gửi đến ESP32 để điều khiển thiết bị
class DeviceCommandMessage(BaseModel):
    name: str = Field(..., min_length=1, description="Tên thiết bị")
    command: str = Field(..., description="Lệnh điều khiển (ví dụ: 'on', 'off', 'set_value')")
    value: Optional[str] = Field(None, description="Giá trị kèm theo lệnh (tùy chọn)")