import axios from "axios";
import { USE_MOCK, API_BASE_URL } from "../constants";
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

export const api = {
  auth: {
    login: async (creds: { username: string; password: string }): Promise<AuthResponse> => {
      if (USE_MOCK) {
        await MockDB.delay();
        if (creds.username === "admin" && creds.password === "admin") {
           MockDB.addLog(`User ${creds.username} logged in`);
           return { id_token: "mock-jwt-token", user: MockDB.user };
        }
        throw new Error("Invalid credentials (try admin/admin)");
      }
      return (await client.post("/api/authenticate", creds)).data;
    },
    register: async (data: any) => {
      if (USE_MOCK) return mockCall({});
      return (await client.post("/api/register", data)).data;
    },
    getAccount: async (): Promise<User> => {
      if (USE_MOCK) return mockCall(MockDB.user);
      return (await client.get("/api/account")).data;
    },
  },

  homes: {
    list: async (): Promise<House[]> => {
      if (USE_MOCK) return mockCall(MockDB.houses);
      return (await client.get("/api/homes")).data;
    },
    create: async (data: Partial<House>): Promise<House> => {
      if (USE_MOCK) {
        const newHouse = { ...data, id: Math.random().toString() } as House;
        MockDB.houses.push(newHouse);
        MockDB.addLog(`New house created: ${newHouse.name}`);
        return mockCall(newHouse);
      }
      return (await client.post("/api/homes", data)).data;
    }
  },

  rooms: {
    list: async (homeId: string): Promise<Room[]> => {
      if (USE_MOCK) return mockCall(MockDB.rooms.filter(r => r.homeId === homeId));
      return (await client.get(`/api/rooms?homeId=${homeId}`)).data;
    },
    create: async (data: Partial<Room>): Promise<Room> => {
      if (USE_MOCK) {
        const newRoom = { ...data, id: Math.random().toString() } as Room;
        MockDB.rooms.push(newRoom);
        MockDB.addLog(`Room added: ${newRoom.name}`);
        return mockCall(newRoom);
      }
      return (await client.post("/api/rooms", data)).data;
    },
    delete: async (id: string) => {
      if (USE_MOCK) {
        MockDB.rooms = MockDB.rooms.filter(r => r.id !== id);
        MockDB.addLog(`Room deleted: ${id}`, "WARNING");
        return mockCall(true);
      }
      return (await client.delete(`/api/rooms/${id}`)).data;
    }
  },

  devices: {
    list: async (roomId: string): Promise<Device[]> => {
      if (USE_MOCK) return mockCall(MockDB.devices.filter(d => d.roomId === roomId));
      return (await client.get(`/api/devices?roomId=${roomId}`)).data;
    },
    create: async (data: Partial<Device>): Promise<Device> => {
      if (USE_MOCK) {
        const newDevice = { 
          ...data, 
          id: Math.random().toString(), 
          status: "ON", 
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
      return (await client.post("/api/devices", data)).data;
    },
    delete: async (id: string) => {
       if (USE_MOCK) {
        MockDB.devices = MockDB.devices.filter(d => d.id !== id);
        MockDB.addLog(`Device removed: ${id}`, "WARNING");
        return mockCall(true);
       }
       return (await client.delete(`/api/devices/${id}`)).data;
    },
    control: async (id: string, command: { action: "ON" | "OFF" | "SET_SPEED", speed?: number }) => {
      if (USE_MOCK) {
        const dev = MockDB.devices.find(d => d.id === id);
        if (dev) {
          if (command.action === "ON") dev.status = "ON";
          if (command.action === "OFF") dev.status = "OFF";
          if (command.action === "SET_SPEED" && typeof command.speed === "number") {
             dev.speed = command.speed;
             // Auto turn on if speed > 0
             if(dev.speed > 0) dev.status = "ON";
          }
          MockDB.addLog(`Device ${dev.name} action: ${command.action} ${command.speed ?? ''}`);
        }
        return mockCall(dev);
      }
      return (await client.post(`/api/devices/${id}/command`, command)).data;
    },
    toggleHumanDetection: async (id: string, enabled: boolean) => {
      if (USE_MOCK) {
         const dev = MockDB.devices.find(d => d.id === id);
         if (dev && dev.type === "CAMERA") {
            dev.humanDetectionEnabled = enabled;
            MockDB.addLog(`Camera ${dev.name} human detection: ${enabled}`);
         }
         return mockCall(dev);
      }
      return (await client.post(`/api/cameras/${id}/human-detection`, { enabled })).data;
    }
  },

  logs: {
     list: async (): Promise<ActivityLog[]> => {
        if(USE_MOCK) return mockCall(MockDB.logs);
        return []; // Logs usually websocket or specific endpoint
     }
  }
};