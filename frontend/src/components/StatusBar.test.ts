import { render, screen } from '@testing-library/svelte';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import StatusBar from './StatusBar.svelte';
import { statusStore } from '../stores/statusStore';
import { get } from 'svelte/store';

// Mock the statusStore to prevent actual API calls
vi.mock('../stores/statusStore', () => {
  const mockDate = new Date('2023-01-01T12:00:00Z');

  // Create a mock store with initial data
  const mockStatusData = {
    ibkr: {
      connected: true,
      lastConnected: mockDate,
      error: ''
    },
    services: [
      {
        name: 'Orchestrator',
        running: true,
        health: 'healthy',
        lastChecked: mockDate,
        message: ''
      },
      {
        name: 'Scanner',
        running: false,
        health: 'unhealthy',
        lastChecked: mockDate,
        message: 'Connection error'
      }
    ],
    activePositions: 3,
    tradingActive: true,
    isTradingHours: true,
    lastUpdated: mockDate
  };

  // Return our mock implementation
  return {
    statusStore: {
      subscribe: vi.fn((callback) => {
        callback(mockStatusData);
        return () => {}; // Return unsubscribe function
      }),
      set: vi.fn()
    },
    updateStatus: vi.fn().mockResolvedValue(undefined),
    startStatusPolling: vi.fn().mockReturnValue(() => {})
  };
});

describe('StatusBar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the status bar with correct initial state', () => {
    render(StatusBar);

    // Check for IBKR connection status
    expect(screen.getByText('IBKR:')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();

    // Check for service statuses
    expect(screen.getByText('Services:')).toBeInTheDocument();
    expect(screen.getByText('Orchestrator')).toBeInTheDocument();
    expect(screen.getByText('Scanner')).toBeInTheDocument();

    // Check for positions count
    expect(screen.getByText('Positions:')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();

    // Check trading status
    expect(screen.getByText('Trading:')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();

    // Check trading hours indicator
    expect(screen.getByText('Trading Hours:')).toBeInTheDocument();

    // Check last updated
    expect(screen.getByText('Last Updated:')).toBeInTheDocument();
  });

  it('should start status polling on mount', () => {
    render(StatusBar);
    expect(updateStatus).toHaveBeenCalledTimes(1);
    expect(startStatusPolling).toHaveBeenCalledWith(5000);
  });
});
