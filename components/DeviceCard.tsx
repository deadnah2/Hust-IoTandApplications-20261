import React from "react";
import { Card, CardContent, Typography, Switch, Slider, Box, IconButton, Menu, MenuItem, Button } from "@mui/material";
import { MoreVert, Lightbulb, Videocam, WindPower } from "@mui/icons-material";
import { Device } from "../types";

interface DeviceCardProps {
  device: Device;
  onToggle: (id: string, state: boolean) => void;
  onSpeedChange: (id: string, speed: number) => void;
  onDelete: (id: string) => void;
  onViewCamera?: (id: string) => void;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({ device, onToggle, onSpeedChange, onDelete, onViewCamera }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

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
    if (device.type === "LIGHT") return <Lightbulb color={device.status === "ON" ? "warning" : "disabled"} />;
    if (device.type === "FAN") return <WindPower color={device.status === "ON" ? "info" : "disabled"} className={device.status === "ON" ? "animate-spin" : ""} />;
    return <Videocam color="error" />;
  };

  return (
    <Card className="rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 h-full">
      <CardContent>
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-full ${device.status === 'ON' ? 'bg-blue-50' : 'bg-gray-100'}`}>
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
                checked={device.status === "ON"}
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
                  checked={device.status === "ON"}
                  onChange={(e) => onToggle(device.id, e.target.checked)}
                  color="info"
                />
              </div>
              <div className="px-2">
                 <Typography variant="caption" className="text-gray-500">Speed: {device.speed}</Typography>
                 <Slider
                    disabled={device.status === "OFF"}
                    value={device.speed || 0}
                    min={0}
                    max={3}
                    step={1}
                    marks
                    onChange={(_, val) => onSpeedChange(device.id, val as number)}
                    size="small"
                  />
              </div>
            </div>
          )}

          {device.type === "CAMERA" && (
            <div className="space-y-2">
              <div className="w-full h-32 bg-black rounded-lg flex items-center justify-center relative overflow-hidden group">
                 <img src="https://picsum.photos/400/300" alt="cam" className="opacity-50 object-cover w-full h-full" />
                 <div className="absolute inset-0 flex items-center justify-center">
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
              <div className="flex items-center justify-between px-1">
                 <Typography variant="caption" color={device.status === "ON" ? "success.main" : "text.secondary"}>
                    {device.status === "ON" ? "● Recording" : "○ Idle"}
                 </Typography>
                 <Switch
                    size="small"
                    checked={device.status === "ON"}
                    onChange={(e) => onToggle(device.id, e.target.checked)}
                 />
              </div>
            </div>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
