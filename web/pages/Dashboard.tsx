import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Typography, Button, Tabs, Tab, Box, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Alert, CircularProgress,
  List, ListItemButton, ListItemText, ListItemIcon, Radio
} from "@mui/material";
import { Add, Refresh } from "@mui/icons-material";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "../services/api";
import { Layout } from "../components/Layout";
import { DeviceCard } from "../components/DeviceCard";
import { CameraViewerDialog } from "../components/CameraViewerDialog";
import { RecordingsDialog } from "../components/RecordingsDialog";
import { createHomeSchema, createRoomSchema, Device, Room } from "../types";

// --- Sub-components for Tabs ---

const DevicesTab = ({
    devices, isLoading, onToggle, onSpeed, onDelete, onViewCamera, onToggleDetection, onShowRecordings
}: {
    devices: Device[], isLoading: boolean, onToggle: any, onSpeed: any, onDelete: any, onViewCamera: any, onToggleDetection: any, onShowRecordings: any
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
                    onToggleDetection={onToggleDetection}
                    onShowRecordings={onShowRecordings}
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
    const [selectedHomeId, setSelectedHomeId] = useState<string | null>(null);
    const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
    const [tabIndex, setTabIndex] = useState(0);
    const [addRoomForHomeId, setAddRoomForHomeId] = useState<string | null>(null);

    // Dialog States
    const [isAddHomeOpen, setAddHomeOpen] = useState(false);
    const [isAddRoomOpen, setAddRoomOpen] = useState(false);
    const [isAddDeviceOpen, setAddDeviceOpen] = useState(false);
    const [isCameraViewerOpen, setCameraViewerOpen] = useState(false);
    const [activeCameraId, setActiveCameraId] = useState<string | null>(null);
    const [recordingsTarget, setRecordingsTarget] = useState<Device | null>(null);
    const [lanBssid, setLanBssid] = useState("");
    const [lanDevices, setLanDevices] = useState<Device[]>([]);
    const [selectedLanDeviceId, setSelectedLanDeviceId] = useState<string | null>(null);
    const [hasSearchedLan, setHasSearchedLan] = useState(false);

    const resetAddDeviceDialog = () => {
        setLanBssid("");
        setLanDevices([]);
        setSelectedLanDeviceId(null);
        setHasSearchedLan(false);
    };

    // Queries
    const { data: houses = [] } = useQuery({ queryKey: ['houses'], queryFn: api.homes.list });

    // Auto-select first home when houses load
    useEffect(() => {
        if (!selectedHomeId && houses.length > 0) {
            setSelectedHomeId(houses[0].id);
        }
    }, [houses, selectedHomeId]);

    // Query rooms for ALL houses (to display in sidebar)
    const roomsQueries = useQuery({
        queryKey: ['allRooms', houses.map(h => h.id)],
        queryFn: async () => {
            const results: Record<string, Room[]> = {};
            await Promise.all(
                houses.map(async (house) => {
                    const rooms = await api.rooms.list(house.id);
                    results[house.id] = rooms;
                })
            );
            return results;
        },
        enabled: houses.length > 0
    });

    const roomsByHome = roomsQueries.data || {};

    // Get rooms for selected home
    const currentRooms = selectedHomeId ? (roomsByHome[selectedHomeId] || []) : [];

    // Auto-select first room when home changes
    useEffect(() => {
        if (selectedHomeId && currentRooms.length > 0 && !currentRooms.find(r => r.id === selectedRoomId)) {
            setSelectedRoomId(currentRooms[0].id);
        } else if (currentRooms.length === 0) {
            setSelectedRoomId(null);
        }
    }, [selectedHomeId, currentRooms, selectedRoomId]);

    const { data: devices = [], isLoading: devicesLoading } = useQuery({
        queryKey: ['devices', selectedRoomId],
        queryFn: () => selectedRoomId ? api.devices.list(selectedRoomId) : Promise.resolve([]),
        enabled: !!selectedRoomId,
        refetchInterval: 2000,
        refetchIntervalInBackground: true
    });

    // Mutations
    const addHomeMutation = useMutation({
        mutationFn: (data: { name: string; location?: string }) => api.homes.create(data),
        onSuccess: (newHome) => {
            queryClient.invalidateQueries({ queryKey: ['houses'] });
            setSelectedHomeId(newHome.id);
            setAddHomeOpen(false);
            resetHome();
        }
    });

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
        mutationFn: (data: { homeId: string; name: string }) => api.rooms.create(data),
        onSuccess: (newRoom) => {
            queryClient.invalidateQueries({ queryKey: ['allRooms'] });
            setSelectedRoomId(newRoom.id);
            setAddRoomOpen(false);
            resetRoom();
        }
    });

    const discoverDevicesMutation = useMutation({
        mutationFn: (bssid: string) => api.devices.discover(bssid),
        onSuccess: (foundDevices) => {
            setLanDevices(foundDevices);
            setSelectedLanDeviceId(foundDevices[0]?.id ?? null);
            setHasSearchedLan(true);
        }
    });

    const assignDeviceMutation = useMutation({
        mutationFn: (data: { deviceId: string; roomId: string }) =>
            api.devices.assignToRoom(data.deviceId, data.roomId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] });
            setAddDeviceOpen(false);
            resetAddDeviceDialog();
        }
    });

    // Forms
    const { register: regHome, handleSubmit: subHome, reset: resetHome } = useForm({ resolver: zodResolver(createHomeSchema) });
    const { register: regRoom, handleSubmit: subRoom, reset: resetRoom } = useForm({ resolver: zodResolver(createRoomSchema) });

    // Handlers
    const handleSelectHome = (homeId: string) => {
        setSelectedHomeId(homeId);
    };

    const handleSelectRoom = (homeId: string, roomId: string) => {
        setSelectedHomeId(homeId);
        setSelectedRoomId(roomId);
    };

    const handleAddRoom = (homeId: string) => {
        setAddRoomForHomeId(homeId);
        resetRoom();
        setAddRoomOpen(true);
    };

    const handleOpenAddDevice = () => {
        resetAddDeviceDialog();
        setAddDeviceOpen(true);
    };

    const handleDiscoverDevices = () => {
        const bssid = lanBssid.trim();
        if (!bssid) {
            return;
        }
        setLanDevices([]);
        setSelectedLanDeviceId(null);
        setHasSearchedLan(false);
        discoverDevicesMutation.mutate(bssid);
    };

    const handleAssignDevice = () => {
        if (!selectedRoomId || !selectedLanDeviceId) {
            return;
        }
        assignDeviceMutation.mutate({ deviceId: selectedLanDeviceId, roomId: selectedRoomId });
    };

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

    const selectedRoom = currentRooms.find(r => r.id === selectedRoomId);
    const selectedRoomName = selectedRoom?.name || "Select a Room";
    const selectedHome = houses.find(h => h.id === selectedHomeId);
    const roomCameras = devices.filter(d => d.type === "CAMERA");

    // Empty state when no home
    if (houses.length === 0) {
        return (
            <Layout
                houses={houses}
                roomsByHome={roomsByHome}
                selectedHomeId={selectedHomeId}
                selectedRoomId={selectedRoomId}
                onSelectHome={handleSelectHome}
                onSelectRoom={handleSelectRoom}
                onAddHome={() => { resetHome(); setAddHomeOpen(true); }}
                onAddRoom={handleAddRoom}
            >
                <Box className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                    <Typography variant="h5" className="text-slate-600 mb-2">
                        Welcome to Smart Home! 🏠
                    </Typography>
                    <Typography variant="body1" className="text-slate-400 mb-6">
                        Create your first home to get started
                    </Typography>
                    <Button 
                        variant="contained" 
                        size="large"
                        startIcon={<Add />}
                        onClick={() => { resetHome(); setAddHomeOpen(true); }}
                    >
                        Create Your First Home
                    </Button>
                </Box>

                {/* Add Home Dialog */}
                <Dialog open={isAddHomeOpen} onClose={() => setAddHomeOpen(false)}>
                    <form onSubmit={subHome((d: any) => addHomeMutation.mutate(d))}>
                        <DialogTitle>Create New Home</DialogTitle>
                        <DialogContent className="flex flex-col gap-4 min-w-[350px] pt-4">
                            <TextField 
                                autoFocus 
                                label="Home Name" 
                                fullWidth 
                                variant="outlined" 
                                placeholder="e.g., My Home, Beach House..."
                                {...regHome("name")} 
                            />
                            <TextField 
                                label="Location (Optional)" 
                                fullWidth 
                                variant="outlined" 
                                placeholder="e.g., Ha Noi, District 1..."
                                {...regHome("location")} 
                            />
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setAddHomeOpen(false)}>Cancel</Button>
                            <Button type="submit" variant="contained" disabled={addHomeMutation.isPending}>
                                {addHomeMutation.isPending ? "Creating..." : "Create"}
                            </Button>
                        </DialogActions>
                    </form>
                </Dialog>
            </Layout>
        );
    }

    return (
        <Layout
            houses={houses}
            roomsByHome={roomsByHome}
            selectedHomeId={selectedHomeId}
            selectedRoomId={selectedRoomId}
            onSelectHome={handleSelectHome}
            onSelectRoom={handleSelectRoom}
            onAddHome={() => { resetHome(); setAddHomeOpen(true); }}
            onAddRoom={handleAddRoom}
        >
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <Typography variant="h4" className="font-bold text-slate-800">
                        {selectedRoomId ? selectedRoomName : (selectedHome?.name || "Select a Home")}
                    </Typography>
                    <Typography variant="body2" className="text-slate-500">
                        {selectedRoomId 
                            ? `${devices.length} Connected Devices` 
                            : (selectedHome ? `${currentRooms.length} Rooms` : "No home selected")
                        }
                    </Typography>
                </div>
                {selectedRoomId && (
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={handleOpenAddDevice}
                    >
                        Add Device
                    </Button>
                )}
            </div>

            {!selectedRoomId && selectedHomeId && (
                <Alert severity="info" className="mb-4">
                    Select a room from the sidebar or create a new one to manage devices.
                </Alert>
            )}

            {selectedRoomId && (
                <>
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
                            onToggleDetection={handleDetection}
                            onShowRecordings={handleShowRecordings}
                        />
                    )}

                    {tabIndex === 1 && <ActivityTab />}
                </>
            )}

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

            {/* Add Home Dialog */}
            <Dialog open={isAddHomeOpen} onClose={() => setAddHomeOpen(false)}>
                <form onSubmit={subHome((d: any) => addHomeMutation.mutate(d))}>
                    <DialogTitle>Create New Home</DialogTitle>
                    <DialogContent className="flex flex-col gap-4 min-w-[350px] pt-4">
                        <TextField 
                            autoFocus 
                            label="Home Name" 
                            fullWidth 
                            variant="outlined" 
                            placeholder="e.g., My Home, Beach House..."
                            {...regHome("name")} 
                        />
                        <TextField 
                            label="Location (Optional)" 
                            fullWidth 
                            variant="outlined" 
                            placeholder="e.g., Ha Noi, District 1..."
                            {...regHome("location")} 
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setAddHomeOpen(false)}>Cancel</Button>
                        <Button type="submit" variant="contained" disabled={addHomeMutation.isPending}>
                            {addHomeMutation.isPending ? "Creating..." : "Create"}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>

            {/* Add Room Dialog */}
            <Dialog open={isAddRoomOpen} onClose={() => setAddRoomOpen(false)}>
                <form onSubmit={subRoom((d: any) => addRoomMutation.mutate({ homeId: addRoomForHomeId!, name: d.name }))}>
                    <DialogTitle>Add New Room</DialogTitle>
                    <DialogContent>
                        <TextField autoFocus margin="dense" label="Room Name" fullWidth variant="outlined" {...regRoom("name")} />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setAddRoomOpen(false)}>Cancel</Button>
                        <Button type="submit" variant="contained" disabled={addRoomMutation.isPending}>
                            {addRoomMutation.isPending ? "Creating..." : "Create"}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>

            {/* Add Device Dialog */}
            <Dialog
                open={isAddDeviceOpen}
                onClose={() => { setAddDeviceOpen(false); resetAddDeviceDialog(); }}
            >
                <DialogTitle>Add Device</DialogTitle>
                <DialogContent className="flex flex-col gap-4 min-w-[360px] pt-4">
                    <TextField 
                        autoFocus
                        label="WiFi BSSID" 
                        fullWidth 
                        variant="outlined" 
                        placeholder="AA:BB:CC:DD:EE:FF"
                        value={lanBssid}
                        onChange={(e) => setLanBssid(e.target.value)}
                        helperText="Enter the BSSID of the WiFi the device is connected to."
                    />
                    <Button
                        variant="outlined"
                        onClick={handleDiscoverDevices}
                        disabled={!lanBssid.trim() || discoverDevicesMutation.isPending}
                    >
                        {discoverDevicesMutation.isPending ? "Searching..." : "Search Devices"}
                    </Button>
                    {discoverDevicesMutation.isPending && (
                        <Box className="flex justify-center py-2">
                            <CircularProgress size={24} />
                        </Box>
                    )}
                    {hasSearchedLan && !discoverDevicesMutation.isPending && lanDevices.length === 0 && (
                        <Alert severity="info">
                            No devices found. Make sure the device is online and registered on this WiFi.
                        </Alert>
                    )}
                    {lanDevices.length > 0 && (
                        <List dense className="border border-slate-200 rounded-md">
                            {lanDevices.map((device) => (
                                <ListItemButton
                                    key={device.id}
                                    selected={selectedLanDeviceId === device.id}
                                    onClick={() => setSelectedLanDeviceId(device.id)}
                                >
                                    <ListItemIcon>
                                        <Radio checked={selectedLanDeviceId === device.id} />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={device.name}
                                        secondary={`${device.type} - ${device.controllerMAC || "Unknown MAC"}`}
                                    />
                                </ListItemButton>
                            ))}
                        </List>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => { setAddDeviceOpen(false); resetAddDeviceDialog(); }}>Cancel</Button>
                    <Button
                        variant="contained"
                        onClick={handleAssignDevice}
                        disabled={!selectedLanDeviceId || assignDeviceMutation.isPending}
                    >
                        {assignDeviceMutation.isPending ? "Adding..." : "Add Device"}
                    </Button>
                </DialogActions>
            </Dialog>
        </Layout>
    );
};
