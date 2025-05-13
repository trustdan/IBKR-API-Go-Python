import { writable } from 'svelte/store';
import { GetStatus } from '../wailsjs/go/main/App';

export interface ConnectionStatus {
  connected: boolean;
  lastConnected?: Date;
  error?: string;
}

export interface ServiceStatus {
  name: string;
  running: boolean;
  health: 'healthy' | 'unhealthy' | 'unknown';
  lastChecked: Date;
  message?: string;
}

export interface StatusInfo {
  ibkr: ConnectionStatus;
  services: ServiceStatus[];
  activePositions: number;
  tradingActive: boolean;
  isTradingHours: boolean;
  lastUpdated: Date;
}

// Create a writable store with an initial state
export const statusStore = writable<StatusInfo>({
  ibkr: {
    connected: false
  },
  services: [],
  activePositions: 0,
  tradingActive: false,
  isTradingHours: false,
  lastUpdated: new Date()
});

// Function to update the status by calling the backend
export async function updateStatus(): Promise<void> {
  try {
    // Call the real backend function
    const status = await GetStatus();

    // Convert string dates to Date objects
    if (status.ibkr.lastConnected) {
      status.ibkr.lastConnected = new Date(status.ibkr.lastConnected);
    }

    if (status.services) {
      status.services.forEach(service => {
        if (service.lastChecked) {
          service.lastChecked = new Date(service.lastChecked);
        }
      });
    }

    if (status.lastUpdated) {
      status.lastUpdated = new Date(status.lastUpdated);
    }

    // Update the store with the status from the backend
    statusStore.set(status);
  } catch (error) {
    console.error("Failed to update status:", error);
  }
}

// Helper function to determine if current time is within trading hours
function isWithinTradingHours(): boolean {
  const now = new Date();
  const hour = now.getHours();
  const day = now.getDay();

  // Assume trading hours are 9:30 AM to 4:00 PM Eastern, Monday to Friday
  return day >= 1 && day <= 5 && hour >= 9 && hour < 16;
}

// Set up polling interval for status updates
export function startStatusPolling(intervalMs: number = 5000): () => void {
  const interval = setInterval(updateStatus, intervalMs);

  // Return a cleanup function
  return () => clearInterval(interval);
}
