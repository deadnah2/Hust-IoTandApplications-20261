import React from "react";
import { Card, CardContent, Typography, Switch, Slider, Box, IconButton, Menu, MenuItem, Button, Tooltip, TextField, Chip } from "@mui/material";
import { 
  MoreVert, 
  Lightbulb, 
  Videocam, 
  WindPower, 
  FiberManualRecord, 
  Security, 
  Thermostat, 
  WaterDrop,
  Warning
} from "@mui/icons-material";
import { Device } from "../types";
import { api } from "../services/api";
import { USE_MOCK, USE_MOCK_DEVICES } from "../constants";

interface DeviceCardProps {
  device: Device;
  onToggle: (id: string, state: boolean) => void;
  onSpeedChange: (id: string, speed: number) => void;
  onDelete: (id: string) => void;
  onViewCamera?: (id: string) => void;
  onToggleDetection?: (id: string, enabled: boolean) => void;
  onShowRecordings?: (device: Device) => void;
  onSetThreshold?: (id: string, tempThreshold: number | null) => void;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({
  device, onToggle, onSpeedChange, onDelete, onViewCamera, onToggleDetection, onShowRecordings, onSetThreshold
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [tempThreshold, setTempThreshold] = React.useState<string>(
    device.temperatureThreshold?.toString() ?? ""
  );
  const open = Boolean(anchorEl);
  const formatValue = (value?: number, suffix = "") => {
    if (typeof value !== "number" || !Number.isFinite(value)) return `--${suffix}`;
    return `${value.toFixed(2)}${suffix}`;
  };
  const isDeviceOffline = device.isOnline === false;
  const isSensorOffline = device.type === "SENSOR" && isDeviceOffline;
  const isFanOffline = device.type === "FAN" && isDeviceOffline;
  const sensorTemp = isSensorOffline ? undefined : device.temperature;
  const sensorHumidity = isSensorOffline ? undefined : device.humidity;

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDelete = () => {
    onDelete(device.id);
    handleClose();
  };

  const Icon = () => {
    if (device.type === "LIGHT") return <Lightbulb color={device.state === "ON" ? "warning" : "disabled"} />;
    if (device.type === "FAN") return <WindPower color={device.state === "ON" ? "info" : "disabled"} className={device.state === "ON" && !isDeviceOffline ? "animate-spin" : ""} />;
    if (device.type === "CAMERA") return <Videocam color="error" />;
    return <Thermostat color="primary" />;
  };

  return (
    <Card className="rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 h-full flex flex-col border border-transparent hover:border-blue-100">
      <CardContent className="flex-grow">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-full ${device.state === 'ON' ? 'bg-blue-50' : 'bg-gray-100'}`}>
              <Icon />
            </div>
            <div>
              <Typography variant="h6" className="text-sm font-bold leading-tight">
                {device.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {device.type}
              </Typography>
            </div>
          </div>
          <IconButton size="small" onClick={handleMenuClick}>
            <MoreVert fontSize="small" />
          </IconButton>
          <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
            <MenuItem onClick={handleClose}>Edit Name</MenuItem>
            <MenuItem onClick={handleDelete} className="text-red-600">Delete</MenuItem>
          </Menu>
        </div>

        {/* Controls */}
        <Box className="mt-2">
          {device.type === "LIGHT" && (
            <div className="flex justify-between items-center bg-gray-50 p-2 rounded-lg">
              <span className="text-sm font-medium text-gray-600">Power</span>
              <Switch
                checked={device.state === "ON"}
                onChange={(e) => onToggle(device.id, e.target.checked)}
                color="warning"
              />
            </div>
          )}

          {device.type === "FAN" && (
            <div className="flex flex-col gap-3">
              <div className="flex justify-between items-center bg-gray-50 p-2 rounded-lg">
                <span className="text-sm font-medium text-gray-600">Power</span>
                <Switch
                checked={device.state === "ON"}
                  onChange={(e) => onToggle(device.id, e.target.checked)}
                  color="info"
                  disabled={isFanOffline}
                />
              </div>
              {/* Chỉ hiện speed slider khi FAN đang ON */}
              {device.state === "ON" && !isFanOffline && (
                <div className="px-2">
                   <Typography variant="caption" className="text-gray-500">Speed: {device.speed}</Typography>
                   <Slider
                      value={device.speed || 1}
                      min={1}
                      max={3}
                      step={1}
                      marks
                      onChange={(_, val) => onSpeedChange(device.id, val as number)}
                      size="small"
                    />
                </div>
              )}
              {isFanOffline && (
                <Typography variant="caption" className="text-center block text-red-500">
                  No data (offline)
                </Typography>
              )}
            </div>
          )}

          {device.type === "CAMERA" && (
            <div className="space-y-3">
              <div className="w-full h-32 bg-black rounded-lg flex items-center justify-center relative overflow-hidden group border border-slate-200">
                 {/* Placeholder image instead of live stream to prevent auto-streaming */}
                 <div className="absolute inset-0 flex items-center justify-center bg-slate-800">
                    <Videocam className="text-slate-600 text-4xl" />
                 </div>
                 
                 <div className="absolute top-2 left-2 flex gap-1">
                   {device.state === 'ON' && (
                     <Tooltip title="Recording">
                       <FiberManualRecord className="text-red-600 text-[10px] animate-pulse" fontSize="small" />
                     </Tooltip>
                   )}
                   {device.humanDetectionEnabled && (
                     <Tooltip title="Detection Active">
                       <Security className="text-blue-600 text-[10px]" fontSize="small" />
                     </Tooltip>
                   )}
                 </div>

                 <div className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                        variant="contained"
                        size="small"
                        startIcon={<Videocam />}
                        onClick={() => onViewCamera && onViewCamera(device.id)}
                    >
                        View Live
                    </Button>
                 </div>
              </div>
              
              <Typography variant="caption" className="text-center block text-slate-400">
                 {device.state === 'ON' ? 'Recording' : 'Idle'} • {device.humanDetectionEnabled ? 'Detection On' : 'Detection Off'}
              </Typography>
            </div>
          )}

          {device.type === "SENSOR" && (
            <div className="mt-2">
              {/* Alert badge */}
              {device.temperatureAlert && (
                <div className="flex gap-1 mb-2 flex-wrap">
                  <Chip 
                    icon={<Warning className="text-orange-600" />} 
                    label={`Temp > ${device.temperatureThreshold}°C`}
                    size="small" 
                    color="warning"
                    className="animate-pulse"
                  />
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-2">
                <Box className={`p-3 rounded-xl flex flex-col items-center justify-center border ${
                  isSensorOffline ? "bg-gray-50 border-gray-200" : 
                  device.temperatureAlert ? "bg-red-50 border-red-300 animate-pulse" : 
                  "bg-orange-50 border-orange-100"
                }`}>
                  <Thermostat className={isSensorOffline ? "text-gray-400 mb-1" : device.temperatureAlert ? "text-red-500 mb-1" : "text-orange-500 mb-1"} fontSize="small" />
                  <Typography variant="h6" className={isSensorOffline ? "font-bold text-gray-500 leading-none" : device.temperatureAlert ? "font-bold text-red-700 leading-none" : "font-bold text-orange-700 leading-none"}>
                    {formatValue(sensorTemp, "°C")}
                  </Typography>
                  <Typography variant="caption" className={isSensorOffline ? "text-gray-500 mt-1" : device.temperatureAlert ? "text-red-600 mt-1" : "text-orange-600 mt-1"}>Temp</Typography>
                </Box>
                <Box className={`p-3 rounded-xl flex flex-col items-center justify-center border ${
                  isSensorOffline ? "bg-gray-50 border-gray-200" : "bg-blue-50 border-blue-100"
                }`}>
                  <WaterDrop className={isSensorOffline ? "text-gray-400 mb-1" : "text-blue-500 mb-1"} fontSize="small" />
                  <Typography variant="h6" className={isSensorOffline ? "font-bold text-gray-500 leading-none" : "font-bold text-blue-700 leading-none"}>
                    {formatValue(sensorHumidity, "%")}
                  </Typography>
                  <Typography variant="caption" className={isSensorOffline ? "text-gray-500 mt-1" : "text-blue-600 mt-1"}>Humidity</Typography>
                </Box>
              </div>
              
              {/* Threshold settings */}
              {!isSensorOffline && (
                <div className="mt-3 p-2 bg-gray-50 rounded-lg">
                  <Typography variant="caption" className="text-gray-600 font-medium block mb-2">
                    ⚠️ Temperature Alert Threshold
                  </Typography>
                  <TextField
                    size="small"
                    label="Temp (°C)"
                    type="number"
                    value={tempThreshold}
                    onChange={(e) => setTempThreshold(e.target.value)}
                    onBlur={() => {
                      if (onSetThreshold) {
                        const temp = tempThreshold ? parseFloat(tempThreshold) : null;
                        onSetThreshold(device.id, temp);
                      }
                    }}
                    inputProps={{ step: 0.5, min: 0, max: 100 }}
                    fullWidth
                  />
                </div>
              )}
              
              {isSensorOffline && (
                <Typography variant="caption" className="text-center block text-red-500 mt-2">
                  No data (offline)
                </Typography>
              )}
            </div>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
