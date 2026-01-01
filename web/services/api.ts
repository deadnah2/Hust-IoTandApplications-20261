import axios from "axios";
import { USE_MOCK, USE_MOCK_DEVICES, API_BASE_URL } from "../constants";
import { MockDB } from "./mockData";
import { House, Room, Device, User, ActivityLog, AuthResponse } from "../types";

// Axios Client
const client = axios.create({
  baseURL: API_BASE_URL,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("id_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- HELPER TO SIMULATE LATENCY ---
const mockCall = async <T,>(data: T): Promise<T> => {
  await MockDB.delay();
  return data;
};

// --- API METHODS ---

console.log("🔧 API Config:", { USE_MOCK, USE_MOCK_DEVICES, API_BASE_URL });

export const api = {
  auth: {
    login: async (creds: { username: string; password: string }): Promise<AuthResponse> => {
      console.log("🔐 Login attempt, USE_MOCK:", USE_MOCK);
      if (USE_MOCK) {
        await MockDB.delay();
        if (creds.username === "admin" && creds.password === "admin") {
           MockDB.addLog(`User ${creds.username} logged in`);
           return { id_token: "mock-jwt-token", user: MockDB.user };
        }
        throw new Error("Invalid credentials (try admin/admin)");
      }
      const data = (await client.post("/authenticate", creds)).data;
      return {
        id_token: data.access_token,
        refresh_token: data.refresh_token,
        user: data.user,
      };
    },
    register: async (data: { username: string; email?: string; password: string }) => {
      if (USE_MOCK) return mockCall({});
      return (await client.post("/register", data)).data;
    },
    getAccount: async (): Promise<User> => {
      if (USE_MOCK) return mockCall(MockDB.user);
      return (await client.get("/me")).data;
    },
  },

  homes: {
    list: async (): Promise<House[]> => {
      if (USE_MOCK) return mockCall(MockDB.houses);
      return (await client.get("/homes")).data;
    },
    create: async (data: Partial<House>): Promise<House> => {
      if (USE_MOCK) {
        const newHouse = { ...data, id: Math.random().toString() } as House;
        MockDB.houses.push(newHouse);
        MockDB.addLog(`New house created: ${newHouse.name}`);
        return mockCall(newHouse);
      }
      return (await client.post("/homes", data)).data;
    },
    delete: async (id: string) => {
      if (USE_MOCK) {
        MockDB.houses = MockDB.houses.filter(h => h.id !== id);
        MockDB.rooms = MockDB.rooms.filter(r => r.homeId !== id);
        MockDB.addLog(`Home deleted: ${id}`, "WARNING");
        return mockCall(true);
      }
      return (await client.delete(`/homes/${id}`)).data;
    }
  },

  rooms: {
    list: async (homeId: string): Promise<Room[]> => {
      if (USE_MOCK) return mockCall(MockDB.rooms.filter(r => r.homeId === homeId));
      return (await client.get(`/rooms?homeId=${homeId}`)).data;
    },
    create: async (data: Partial<Room>): Promise<Room> => {
      if (USE_MOCK) {
        const newRoom = { ...data, id: Math.random().toString() } as Room;
        MockDB.rooms.push(newRoom);
        MockDB.addLog(`Room added: ${newRoom.name}`);
        return mockCall(newRoom);
      }
      return (await client.post("/rooms", data)).data;
    },
    delete: async (id: string) => {
      if (USE_MOCK) {
        MockDB.rooms = MockDB.rooms.filter(r => r.id !== id);
        MockDB.addLog(`Room deleted: ${id}`, "WARNING");
        return mockCall(true);
      }
      return (await client.delete(`/rooms/${id}`)).data;
    }
  },

  devices: {
    list: async (roomId: string): Promise<Device[]> => {
      if (USE_MOCK || USE_MOCK_DEVICES) return mockCall(MockDB.devices.filter(d => d.roomId === roomId));
      return (await client.get(`/devices/?roomId=${roomId}`)).data;
    },
    discover: async (bssid: string): Promise<Device[]> => {
      if (USE_MOCK || USE_MOCK_DEVICES) {
        return mockCall(MockDB.devices.filter(d => d.roomId == null && d.bssid === bssid));
      }
      return (await client.get(`/devices/lan?bssid=${encodeURIComponent(bssid)}`)).data;
    },
    assignToRoom: async (id: string, roomId: string): Promise<Device> => {
      if (USE_MOCK || USE_MOCK_DEVICES) {
        const dev = MockDB.devices.find(d => d.id === id);
        if (dev) {
          dev.roomId = roomId;
          MockDB.addLog(`Device assigned to room: ${dev.name}`);
        }
        return mockCall(dev as Device);
      }
      return (await client.put(`/devices/${id}`, { roomId })).data;
    },
    create: async (data: Partial<Device> & { roomId?: string; bssid: string }): Promise<Device> => {
      if (USE_MOCK || USE_MOCK_DEVICES) {
        const newDevice = { 
          ...data, 
          id: Math.random().toString(), 
          state: "ON", 
          speed: 0 
        } as Device;
        
        if (data.type === "SENSOR") {
          newDevice.temperature = 25 + Math.floor(Math.random() * 5);
          newDevice.humidity = 50 + Math.floor(Math.random() * 20);
        }

        MockDB.devices.push(newDevice);
        MockDB.addLog(`Device installed: ${newDevice.name}`);
        return mockCall(newDevice);
      }
      return (await client.post("/devices", data)).data;
    },
    delete: async (id: string) => {
       if (USE_MOCK || USE_MOCK_DEVICES) {
        const dev = MockDB.devices.find(d => d.id === id);
        if (dev) {
          dev.roomId = null;
          MockDB.addLog(`Device unassigned: ${dev.name}`, "WARNING");
        }
        return mockCall(true);
       }
       return (await client.delete(`/devices/${id}`)).data;
    },
    control: async (id: string, command: { action: "ON" | "OFF" | "SET_SPEED", speed?: number }) => {
      if (USE_MOCK || USE_MOCK_DEVICES) {
        const dev = MockDB.devices.find(d => d.id === id);
        if (dev) {
          if (command.action === "ON") dev.state = "ON";
          if (command.action === "OFF") dev.state = "OFF";
          if (command.action === "SET_SPEED" && typeof command.speed === "number") {
             dev.speed = command.speed;
             // Auto turn on if speed > 0
             if(dev.speed > 0) dev.state = "ON";
          }
          MockDB.addLog(`Device ${dev.name} action: ${command.action} ${command.speed ?? ''}`);
        }
        return mockCall(dev);
      }
      return (await client.post(`/devices/${id}/command`, command)).data;
    },
    toggleHumanDetection: async (id: string, enabled: boolean) => {
      if (USE_MOCK || USE_MOCK_DEVICES) {
         const dev = MockDB.devices.find(d => d.id === id);
         if (dev && dev.type === "CAMERA") {
            dev.humanDetectionEnabled = enabled;
            MockDB.addLog(`Camera ${dev.name} human detection: ${enabled}`);
         }
         return mockCall(dev);
      }
      // BE chưa có endpoint riêng cho human detection, dùng update
      return (await client.put(`/devices/${id}`, { humanDetectionEnabled: enabled })).data;
    }
  },

  logs: {
     list: async (): Promise<ActivityLog[]> => {
        if(USE_MOCK || USE_MOCK_DEVICES) return mockCall(MockDB.logs);
        return []; // Logs usually websocket or specific endpoint
     }
  }
};
