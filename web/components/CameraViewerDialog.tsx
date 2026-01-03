import React, { useState, useEffect } from "react";
import {
  Dialog, DialogContent, Typography, Box, IconButton, List,
  ListItemText, ListItemButton, Button, Chip
} from "@mui/material";
import { Close, Videocam, FiberManualRecord, Security, History as HistoryIcon } from "@mui/icons-material";
import { Device } from "../types";
import { api } from "../services/api";
import { USE_MOCK, USE_MOCK_DEVICES } from "../constants";

interface CameraViewerDialogProps {
  open: boolean;
  onClose: () => void;
  cameras: Device[];
  initialCameraId: string | null;
  onToggleRecording: (id: string, enabled: boolean) => void;
  onToggleDetection: (id: string, enabled: boolean) => void;
  onShowRecordings: (device: Device) => void;
}

export const CameraViewerDialog: React.FC<CameraViewerDialogProps> = ({
  open, onClose, cameras, initialCameraId, onToggleRecording, onToggleDetection, onShowRecordings
}) => {
  const [activeCamId, setActiveCamId] = useState<string | null>(initialCameraId);
  const [streamKey, setStreamKey] = useState(0); // Key để force re-render image

  useEffect(() => {
    if (initialCameraId) setActiveCamId(initialCameraId);
  }, [initialCameraId]);

  // Force unmount image khi dialog đóng hoặc đổi camera
  useEffect(() => {
    if (open) {
      setStreamKey(prev => prev + 1);
    }
  }, [open, activeCamId]);

  const activeCamera = cameras.find(c => c.id === activeCamId) || cameras[0];

  if (!activeCamera) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth scroll="body">
      <Box className="flex justify-between items-center p-3 bg-slate-900 text-white">
        <Typography variant="h6" className="font-bold flex items-center gap-2">
          <Videocam /> Camera Viewer
        </Typography>
        <IconButton onClick={onClose} color="inherit">
          <Close />
        </IconButton>
      </Box>

      <DialogContent className="p-0 flex flex-col md:flex-row bg-slate-900 min-h-[500px]">
        {/* Sidebar: Camera List */}
        <Box className="w-full md:w-64 bg-slate-800 border-r border-slate-700">
          <Typography variant="overline" className="px-4 py-2 block text-slate-400 font-bold">
            Available Cameras
          </Typography>
          <List className="p-0">
            {cameras.map(c => (
              <ListItemButton
                key={c.id}
                selected={activeCamera.id === c.id}
                onClick={() => setActiveCamId(c.id)}
                sx={{
                  "&.Mui-selected": { bgcolor: "rgba(37, 99, 235, 0.2)" },
                  "&.Mui-selected:hover": { bgcolor: "rgba(37, 99, 235, 0.3)" },
                }}
              >
                <ListItemText
                  primary={<Typography className="text-white text-sm">{c.name}</Typography>}
                  secondary={
                    <Box className="flex items-center gap-1">
                      <FiberManualRecord sx={{ fontSize: 8, color: c.state === 'ON' ? '#ef4444' : '#64748b' }} />
                      <Typography variant="caption" className="text-slate-500">
                        {c.state === 'ON' ? 'Recording' : 'Idle'}
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            ))}
          </List>
        </Box>

        {/* Viewport */}
        <Box className="flex-1 flex flex-col bg-black relative">
          <Box className="flex-1 relative overflow-hidden flex items-center justify-center">
            {open && (
              <img
                key={streamKey} // Force unmount/remount khi streamKey thay đổi
                src={
                  USE_MOCK || USE_MOCK_DEVICES
                    ? `https://picsum.photos/1280/720?random=${activeCamera.id}`
                    : api.devices.getCameraStreamUrl(activeCamera.id)
                }
                alt="Live"
                className="w-full h-full object-contain opacity-90"
              />
            )}
            <Box className="absolute top-4 left-4 flex gap-2">
              <Chip
                label="LIVE"
                color="error"
                size="small"
                className="font-bold animate-pulse"
              />
              {activeCamera.state === 'ON' && (
                <Chip
                  icon={<FiberManualRecord className="animate-pulse" />}
                  label="REC"
                  variant="outlined"
                  size="small"
                  sx={{ color: 'white', borderColor: 'red' }}
                />
              )}
            </Box>
            <Box className="absolute top-4 right-4 bg-black/50 px-2 py-1 rounded text-white text-xs">
              {new Date().toLocaleTimeString()}
            </Box>
          </Box>

          {/* Controls Overlay Footer */}
          <Box className="bg-slate-800/80 backdrop-blur p-4 flex flex-wrap justify-between items-center gap-4">
            <Box>
              <Typography className="text-white font-bold">{activeCamera.name}</Typography>
              <Typography variant="caption" className="text-slate-400">
                {activeCamera.cameraResolution || 'Unknown'} • {activeCamera.fps ? `${activeCamera.fps.toFixed(1)}fps` : 'N/A'}
              </Typography>
            </Box>

            <Box className="flex gap-2">
              <Button
                variant={activeCamera.state === "ON" ? "contained" : "outlined"}
                color={activeCamera.state === "ON" ? "error" : "inherit"}
                size="small"
                startIcon={<FiberManualRecord />}
                onClick={() => onToggleRecording(activeCamera.id, activeCamera.state !== "ON")}
                sx={{ color: activeCamera.state === "ON" ? "white" : "white" }}
              >
                {activeCamera.state === "ON" ? "Stop Recording" : "Start Recording"}
              </Button>

              <Button
                variant={activeCamera.humanDetectionEnabled ? "contained" : "outlined"}
                color={activeCamera.humanDetectionEnabled ? "primary" : "inherit"}
                size="small"
                startIcon={<Security />}
                onClick={() => onToggleDetection(activeCamera.id, !activeCamera.humanDetectionEnabled)}
                sx={{ color: activeCamera.humanDetectionEnabled ? "white" : "white" }}
              >
                Detection: {activeCamera.humanDetectionEnabled ? "ON" : "OFF"}
              </Button>

              <Button
                variant="outlined"
                color="inherit"
                size="small"
                startIcon={<HistoryIcon />}
                onClick={() => onShowRecordings(activeCamera)}
                sx={{ color: "white" }}
              >
                Recordings
              </Button>
            </Box>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
};
