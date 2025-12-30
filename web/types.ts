export interface User {
  id: string;
  username: string;
  email?: string;
}

export interface House {
  id: string;
  name: string;
  location?: string;
  ownerUserId?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface Room {
  id: string;
  homeId: string;
  name: string;
  createdAt?: string;
  updatedAt?: string;
}

export type DeviceType = "LIGHT" | "FAN" | "CAMERA" | "SENSOR";
export type DeviceState = "ON" | "OFF";

export interface Device {
  id: string;
  roomId: string | null;
  name: string;
  custom_name?: string;
  controllerMAC?: string;
  bssid?: string;
  type: DeviceType;
  state: DeviceState;
  isOnline?: boolean;
  speed?: number; // 0-3 for FAN
  streamUrl?: string; // For CAMERA
  humanDetectionEnabled?: boolean; // For CAMERA
  temperature?: number; // For SENSOR (°C)
  humidity?: number; // For SENSOR (%)
  lastSeen?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface ActivityLog {
  id: string;
  timestamp: string;
  message: string;
  type: "INFO" | "WARNING" | "ERROR";
}

export interface AuthResponse {
  id_token: string;
  refresh_token?: string;
  user: User;
}

// Zod Schemas for Forms
import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters"),
  password: z.string().min(4, "Password must be at least 4 characters"),
});

export const registerSchema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(4),
});

export const createHomeSchema = z.object({
  name: z.string().min(1, "Home name is required"),
  location: z.string().optional(),
});

export const createRoomSchema = z.object({
  name: z.string().min(1, "Room name is required"),
});

export const createDeviceSchema = z.object({
  name: z.string().min(1, "Device name is required"),
  type: z.enum(["LIGHT", "FAN", "CAMERA", "SENSOR"]),
  bssid: z.string().min(1, "BSSID is required"),
  controllerMAC: z.string().optional(),
});
