import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Typography, Button, Tabs, Tab, Box, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Select, MenuItem,
  FormControl, InputLabel, Alert, CircularProgress
} from "@mui/material";
import { Add, Refresh } from "@mui/icons-material";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "../services/api";
import { Layout } from "../components/Layout";
import { DeviceCard } from "../components/DeviceCard";
import { CameraViewerDialog } from "../components/CameraViewerDialog";
import { RecordingsDialog } from "../components/RecordingsDialog";
import { createRoomSchema, createDeviceSchema, Device } from "../types";

// --- Sub-components for Tabs ---

const DevicesTab = ({
    devices, isLoading, onToggle, onSpeed, onDelete, onViewCamera
}: {
    devices: Device[], isLoading: boolean, onToggle: any, onSpeed: any, onDelete: any, onViewCamera: any
}) => {
    if (isLoading) return <Box className="flex justify-center p-10"><CircularProgress /></Box>;
    if (devices.length === 0) return <Alert severity="info">No devices in this room. Add one!</Alert>;

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {devices.map(d => (
                <DeviceCard
                    key={d.id}
                    device={d}
                    onToggle={onToggle}
                    onSpeedChange={onSpeed}
                    onDelete={onDelete}
                    onViewCamera={onViewCamera}
                />
            ))}
        </div>
    );
};

const ActivityTab = () => {
    const { data: logs } = useQuery({ queryKey: ['logs'], queryFn: api.logs.list, refetchInterval: 2000 });

    return (
        <div className="bg-white rounded-lg shadow p-4">
             <div className="flex items-center justify-between mb-4">
                <Typography variant="h6">Activity Log</Typography>
                <Refresh className="text-gray-400 cursor-pointer" />
             </div>
             <div className="space-y-4 max-h-[500px] overflow-y-auto">
                {logs?.map((log) => (
                    <div key={log.id} className="flex gap-4 border-b pb-2">
                        <div className="text-xs text-gray-500 w-32 shrink-0">
                            {new Date(log.timestamp).toLocaleString()}
                        </div>
                        <div className="flex-1">
                            <Typography variant="body2" className={log.type === 'WARNING' ? 'text-orange-600' : 'text-gray-800'}>
                                {log.message}
                            </Typography>
                        </div>
                    </div>
                ))}
                {(!logs || logs.length === 0) && <Typography className="text-gray-400 italic">No activity recorded.</Typography>}
             </div>
        </div>
    );
};

// --- Main Dashboard ---

export const Dashboard = () => {
    const queryClient = useQueryClient();
    const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
    const [tabIndex, setTabIndex] = useState(0);

    // Dialog States
    const [isAddRoomOpen, setAddRoomOpen] = useState(false);
    const [isAddDeviceOpen, setAddDeviceOpen] = useState(false);
    const [isCameraViewerOpen, setCameraViewerOpen] = useState(false);
    const [activeCameraId, setActiveCameraId] = useState<string | null>(null);
    const [recordingsTarget, setRecordingsTarget] = useState<Device | null>(null);

    // Queries
    const { data: houses = [] } = useQuery({ queryKey: ['houses'], queryFn: api.homes.list });
    const activeHomeId = houses[0]?.id;

    const { data: rooms = [] } = useQuery({
        queryKey: ['rooms', activeHomeId],
        queryFn: () => activeHomeId ? api.rooms.list(activeHomeId) : Promise.resolve([]),
        enabled: !!activeHomeId
    });

    // Auto-select first room
    useEffect(() => {
        if (!selectedRoomId && rooms.length > 0) {
            setSelectedRoomId(rooms[0].id);
        }
    }, [rooms, selectedRoomId]);

    const { data: devices = [], isLoading: devicesLoading } = useQuery({
        queryKey: ['devices', selectedRoomId],
        queryFn: () => selectedRoomId ? api.devices.list(selectedRoomId) : Promise.resolve([]),
        enabled: !!selectedRoomId
    });

    // Mutations
    const toggleMutation = useMutation({
        mutationFn: (vars: { id: string, state: boolean }) =>
            api.devices.control(vars.id, { action: vars.state ? "ON" : "OFF" }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['devices'] })
    });

    const speedMutation = useMutation({
        mutationFn: (vars: { id: string, speed: number }) =>
            api.devices.control(vars.id, { action: "SET_SPEED", speed: vars.speed }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['devices'] })
    });

    const detectionMutation = useMutation({
        mutationFn: (vars: { id: string, enabled: boolean }) =>
            api.devices.toggleHumanDetection(vars.id, vars.enabled),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['devices'] })
    });

    const deleteDeviceMutation = useMutation({
        mutationFn: api.devices.delete,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['devices'] })
    });

    const addRoomMutation = useMutation({
        mutationFn: (name: string) => api.rooms.create({ homeId: activeHomeId, name }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['rooms'] });
            setAddRoomOpen(false);
        }
    });

    const addDeviceMutation = useMutation({
        mutationFn: (data: any) => api.devices.create({ ...data, roomId: selectedRoomId }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] });
            setAddDeviceOpen(false);
        }
    });

    // Forms
    const { register: regRoom, handleSubmit: subRoom, reset: resetRoom } = useForm({ resolver: zodResolver(createRoomSchema) });
    const { register: regDev, handleSubmit: subDev, reset: resetDev } = useForm({ resolver: zodResolver(createDeviceSchema) });

    const handleToggle = (id: string, state: boolean) => toggleMutation.mutate({ id, state });
    const handleSpeed = (id: string, speed: number) => speedMutation.mutate({ id, speed });
    const handleDetection = (id: string, enabled: boolean) => detectionMutation.mutate({ id, enabled });
    const handleDelete = (id: string) => deleteDeviceMutation.mutate(id);

    const handleViewCamera = (id: string) => {
        setActiveCameraId(id);
        setCameraViewerOpen(true);
    };

    const handleShowRecordings = (device: Device) => {
        setRecordingsTarget(device);
    };

    const selectedRoomName = rooms.find(r => r.id === selectedRoomId)?.name || "Select a Room";
    const roomCameras = devices.filter(d => d.type === "CAMERA");

    return (
        <Layout
            houses={houses}
            rooms={rooms}
            selectedRoomId={selectedRoomId}
            onSelectRoom={setSelectedRoomId}
            onAddRoom={() => { resetRoom(); setAddRoomOpen(true); }}
        >
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <Typography variant="h4" className="font-bold text-slate-800">{selectedRoomName}</Typography>
                    <Typography variant="body2" className="text-slate-500">
                        {devices.length} Connected Devices
                    </Typography>
                </div>
                {selectedRoomId && (
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={() => { resetDev(); setAddDeviceOpen(true); }}
                    >
                        Add Device
                    </Button>
                )}
            </div>

            <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
                <Tabs value={tabIndex} onChange={(_, v) => setTabIndex(v)}>
                    <Tab label="Devices" />
                    <Tab label="Activity" />
                </Tabs>
            </Box>

            {tabIndex === 0 && (
                <DevicesTab
                    devices={devices}
                    isLoading={devicesLoading}
                    onToggle={handleToggle}
                    onSpeed={handleSpeed}
                    onDelete={handleDelete}
                    onViewCamera={handleViewCamera}
                />
            )}

            {tabIndex === 1 && <ActivityTab />}

            {/* --- Modals & Overlays --- */}

            <CameraViewerDialog
                open={isCameraViewerOpen}
                onClose={() => setCameraViewerOpen(false)}
                cameras={roomCameras}
                initialCameraId={activeCameraId}
                onToggleRecording={handleToggle}
                onToggleDetection={handleDetection}
                onShowRecordings={handleShowRecordings}
            />

            <RecordingsDialog
              open={!!recordingsTarget}
              onClose={() => setRecordingsTarget(null)}
              deviceName={recordingsTarget?.name || ""}
            />

            <Dialog open={isAddRoomOpen} onClose={() => setAddRoomOpen(false)}>
                <form onSubmit={subRoom((d: any) => addRoomMutation.mutate(d.name))}>
                    <DialogTitle>Add New Room</DialogTitle>
                    <DialogContent>
                        <TextField autoFocus margin="dense" label="Room Name" fullWidth variant="outlined" {...regRoom("name")} />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setAddRoomOpen(false)}>Cancel</Button>
                        <Button type="submit" variant="contained">Create</Button>
                    </DialogActions>
                </form>
            </Dialog>

            <Dialog open={isAddDeviceOpen} onClose={() => setAddDeviceOpen(false)}>
                <form onSubmit={subDev((d) => addDeviceMutation.mutate(d))}>
                    <DialogTitle>Add Device</DialogTitle>
                    <DialogContent className="flex flex-col gap-4 min-w-[300px] pt-4">
                        <TextField label="Device Name" fullWidth variant="outlined" {...regDev("name")} />
                        <FormControl fullWidth>
                            <InputLabel>Type</InputLabel>
                            <Select label="Type" defaultValue="LIGHT" {...regDev("type")}>
                                <MenuItem value="LIGHT">Light</MenuItem>
                                <MenuItem value="FAN">Fan</MenuItem>
                                <MenuItem value="CAMERA">Camera</MenuItem>
                            </Select>
                        </FormControl>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setAddDeviceOpen(false)}>Cancel</Button>
                        <Button type="submit" variant="contained">Add</Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Layout>
    );
};
