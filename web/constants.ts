// Ensure we don't crash if import.meta.env is undefined (e.g. running without Vite build step)
// Casting to any to avoid TS errors if types are missing
const env = (import.meta as any).env || {};

// Default to false (Real Mode) - set to 'true' in .env to use mock data
export const USE_MOCK = env.VITE_USE_MOCK === 'true';
export const USE_MOCK_DEVICES = env.VITE_USE_MOCK_DEVICES === 'true';
export const API_BASE_URL = env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const ROUTES = {
  LOGIN: '/login',
  APP: '/app',
};
