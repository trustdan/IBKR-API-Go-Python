import { writable, derived } from 'svelte/store';
import { apiCall } from '../lib/api';
// import { GetStatus } from '../../wailsjs/go/main/App';

// Container state type
export type ContainerState = 'running' | 'paused' | 'stopped' | 'error';

// Container interface
export interface Container {
  name: string;
  state: ContainerState;
  error?: string;
}

// Status interface
export interface Status {
  ibkrConnected: boolean;
  ibkrError: string | null;
  containers: Container[];
  lastUpdated: Date | null;
  updating: boolean;
}

// Initialize status store
export const statusStore = writable<Status>({
  ibkrConnected: false,
  ibkrError: null,
  containers: [],
  lastUpdated: null,
  updating: false,
});

// Derive system health from status
export const systemHealth = derived(
  statusStore,
  $status => {
    // IBKR connection is critical
    if (!$status.ibkrConnected) {
      return 'error';
    }

    // Check container status
    if ($status.containers.some(c => c.state === 'error')) {
      return 'error';
    }

    if ($status.containers.some(c => c.state === 'stopped' || c.state === 'paused')) {
      return 'degraded';
    }

    return 'healthy';
  }
);

// Status polling interval
let pollTimer: number;

/**
 * Start polling for status updates
 * @param interval Polling interval in milliseconds
 * @returns Cleanup function
 */
export function startStatusPolling(interval: number = 5000): () => void {
  // Clear any existing timer
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  // Initial fetch
  updateStatus();

  // Set up polling
  pollTimer = window.setInterval(updateStatus, interval);

  // Return cleanup function
  return () => {
    clearInterval(pollTimer);
  };
}

/**
 * Update status from backend
 */
export async function updateStatus(): Promise<void> {
  statusStore.update(s => ({ ...s, updating: true }));

  try {
    // Uncomment when backend endpoint is ready
    // const status = await apiCall(() => GetStatus());

    // For now, simulate a status update with mock data
    const mockStatus = {
      ibkrConnected: Math.random() > 0.2, // 80% chance of being connected
      ibkrError: Math.random() > 0.8 ? 'Failed to connect to TWS' : null,
      containers: [
        {
          name: 'orchestrator',
          state: Math.random() > 0.1 ? 'running' : 'stopped',
          error: Math.random() > 0.9 ? 'Failed to start' : undefined
        },
        {
          name: 'scanner',
          state: Math.random() > 0.1 ? 'running' : 'paused',
          error: Math.random() > 0.9 ? 'Connection timeout' : undefined
        }
      ] as Container[]
    };

    statusStore.set({
      ...mockStatus,
      lastUpdated: new Date(),
      updating: false,
    });
  } catch (err) {
    console.error('Failed to update status:', err);
    statusStore.update(s => ({
      ...s,
      updating: false,
      lastUpdated: new Date(),
    }));
  }
}
