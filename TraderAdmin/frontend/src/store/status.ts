import { writable } from 'svelte/store';
import type { StatusInfo } from '../types';

// Interface for container status
interface Container {
  name: string;
  state: string;
}

// Interface for status store
interface StatusState {
  ibkrConnected: boolean;
  ibkrError?: string;
  containers: Container[];
}

// Initialize with default values
export const status = writable<StatusInfo>({
  ibkrConnected: false,
  containers: []
});

// Poll the backend for status updates
export function initStatusPolling() {
  // Poll every 5 seconds
  const statusTimer = setInterval(async () => {
    try {
      // Call the Go backend method
      const currentStatus = await window.go.main.App.GetStatus();
      status.set(currentStatus);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  }, 5000);

  // Return a cleanup function
  return () => {
    clearInterval(statusTimer);
  };
}
