import { House, Room, Device, User, ActivityLog } from "../types";
const genId = () => Math.random().toString(36).substr(2, 9);

// --- SEED DATA ---
const user: User = { id: "u1", username: "admin", email: "admin@smarthome.com" };
const house: House = { id: "h1", name: "MyHome", location: "Ha Noi" };

const room1: Room = { id: "r1", homeId: "h1", name: "Living Room" };
const room2: Room = { id: "r2", homeId: "h1", name: "Bedroom" };

const devices: Device[] = [
  // Room 1: Camera + Light
  { id: "d1", roomId: "r1", name: "Main Camera", type: "CAMERA", status: "ON", streamUrl: "", humanDetectionEnabled: false },
  { id: "d2", roomId: "r1", name: "Ceiling Light", type: "LIGHT", status: "OFF" },
  // Room 2: Fan + Light + Sensor
  { id: "d3", roomId: "r2", name: "Stand Fan", type: "FAN", status: "OFF", speed: 0 },
  { id: "d4", roomId: "r2", name: "Night Light", type: "LIGHT", status: "ON" },
  { 
    id: "d5", 
    roomId: "r2", 
    name: "Climate Sensor", 
    type: "SENSOR", 
    status: "ON", 
    temperature: 24.5, 
    humidity: 62 
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
