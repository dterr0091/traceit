/**
 * Application configuration
 */

// API base URL - can be overridden by environment variables
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Other config constants can be added here
export const DEFAULT_TIMEOUT = 60000; // 60 seconds 