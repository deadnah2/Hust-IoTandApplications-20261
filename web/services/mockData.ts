import { House, Room, Device, User, ActivityLog } from "../types";
const genId = () => Math.random().toString(36).substr(2, 9);

// --- SEED DATA ---
const user: User = { id: "u1", username: "admin", email: "admin@smarthome.com" };
const house: House = { id: "h1", name: "MyHome", location: "Ha Noi" };

const room1: Room = { id: "r1", homeId: "h1", name: "Living Room" };
const room2: Room = { id: "r2", homeId: "h1", name: "Bedroom" };

const devices: Device[] = [
  // Room 1: Camera + Light
  { id: "d1", roomId: "r1", name: "Main Camera", type: "CAMERA", state: "ON", streamUrl: "", humanDetectionEnabled: false, bssid: "32:c5:1b:f7:65:fa", controllerMAC: "CAM_0001", cameraResolution: "QVGA", fps: 15.0 },
  { id: "d2", roomId: "r1", name: "Ceiling Light", type: "LIGHT", state: "OFF", bssid: "32:c5:1b:f7:65:fa", controllerMAC: "LIGHT_0001" },
  // Room 2: Fan + Light + Sensor
  { id: "d3", roomId: "r2", name: "Stand Fan", type: "FAN", state: "OFF", speed: 1, bssid: "32:c5:1b:f7:65:fa", controllerMAC: "FAN_0001" },
  { id: "d4", roomId: "r2", name: "Night Light", type: "LIGHT", state: "ON", bssid: "32:c5:1b:f7:65:fa", controllerMAC: "LIGHT_0002" },
  { 
    id: "d5", 
    roomId: "r2", 
    name: "Climate Sensor", 
    type: "SENSOR", 
    state: "ON", 
    temperature: 24.5, 
    humidity: 62,
    bssid: "32:c5:1b:f7:65:fa",
    controllerMAC: "SENSOR_0001"
  },
  // Unassigned devices discovered in LAN
  {
    id: "d6",
    roomId: null,
    name: "New Fan",
    type: "FAN",
    state: "OFF",
    speed: 1,
    bssid: "32:c5:1b:f7:65:fa",
    controllerMAC: "FAN_0110"
  },
  {
    id: "d7",
    roomId: null,
    name: "Temp Sensor",
    type: "SENSOR",
    state: "ON",
    temperature: 26.1,
    humidity: 58,
    bssid: "32:c5:1b:f7:65:fa",
    controllerMAC: "SENSOR_0110"
  },
];

let activityLogs: ActivityLog[] = [
  { id: genId(), timestamp: new Date().toISOString(), message: "System initialized", type: "INFO" }
];

// --- MOCK DB ---
export const MockDB = {
  user,
  houses: [house],
  rooms: [room1, room2],
  devices,
  logs: activityLogs,

  addLog: (msg: string, type: "INFO" | "WARNING" | "ERROR" = "INFO") => {
    const newLog: ActivityLog = {
      id: genId(),
      timestamp: new Date().toISOString(),
      message: msg,
      type
    };
    MockDB.logs = [newLog, ...MockDB.logs].slice(0, 50); // Keep last 50
  },

  delay: (ms = 400) => new Promise((resolve) => setTimeout(resolve, ms)),
};
