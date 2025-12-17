export interface User {
  id: string;
  login: string;
  email?: string;
}

export interface House {
  id: string;
  name: string;
  location?: string;
}

export interface Room {
  id: string;
  homeId: string;
  name: string;
}

export type DeviceType = "LIGHT" | "FAN" | "CAMERA";
export type DeviceStatus = "ON" | "OFF";

export interface Device {
  id: string;
  roomId: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  speed?: number; // 0-3 for FAN
  streamUrl?: string; // For CAMERA
  humanDetectionEnabled?: boolean; // For CAMERA
}

export interface ActivityLog {
  id: string;
  timestamp: string;
  message: string;
  type: "INFO" | "WARNING" | "ERROR";
}

export interface AuthResponse {
  id_token: string;
  user: User;
}

// Zod Schemas for Forms
import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters"),
  password: z.string().min(4, "Password must be at least 4 characters"),
});

export const registerSchema = z.object({
  login: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(4),
});

export const createRoomSchema = z.object({
  name: z.string().min(1, "Room name is required"),
});

export const createDeviceSchema = z.object({
  name: z.string().min(1, "Device name is required"),
  type: z.enum(["LIGHT", "FAN", "CAMERA"]),
});
