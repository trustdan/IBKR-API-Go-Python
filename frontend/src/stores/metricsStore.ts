// @ts-ignore - Svelte types may not be properly configured in the project
import { writable, get } from 'svelte/store';
import type { Configuration } from './configStore'; // Import the type
import { GetLatestMetrics } from '../wailsjs/go/main/App';

// Declare the global window interface to extend it with Wails properties
declare global {
  interface Window {
    go: {
      main: {
        App: {
          // Methods from metricsStore.ts
          GetLatestMetrics: () => Promise<AllMetrics>;
          TestAlertNotification: (channelType: string, message: string) => Promise<void>;
          // Methods from configStore.ts
          GetConfig: () => Promise<Configuration>;
          UpdateConfig: (config: Configuration) => Promise<void>;
          SaveConfigurationAndRestart: (config: Configuration) => Promise<void>;
          PauseTradingServices: () => Promise<void>;
          ResumeTradingServices: () => Promise<void>;
        }
      }
    }
  }
}

// Types for metrics data
export interface Position {
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPl: number;
  strategy: string;
  openTime: string;
}

export interface PortfolioMetrics {
  timestamp: Date;
  equity: number;
  realizedPnlToday: number;
  unrealizedPnl: number;
  openPositionsCount: number;
  buyingPower: number;
}

export interface TradeStatsToday {
  executedCount: number;
  winCount: number;
  lossCount: number;
  winRate: number;
  avgWinAmount: number;
  avgLossAmount: number;
}

export interface SystemHealthMetrics {
  avgOrderLatencyMs: number;
  apiErrorCount: number;
  lastDataSync: Date;
}

export interface AllMetrics {
  portfolio: PortfolioMetrics;
  trades: TradeStatsToday;
  system: SystemHealthMetrics;
  openPositions: Position[];
}

// Default/initial state
const initialMetrics: AllMetrics = {
  portfolio: {
    timestamp: new Date(),
    equity: 0,
    realizedPnlToday: 0,
    unrealizedPnl: 0,
    openPositionsCount: 0,
    buyingPower: 0
  },
  trades: {
    executedCount: 0,
    winCount: 0,
    lossCount: 0,
    winRate: 0,
    avgWinAmount: 0,
    avgLossAmount: 0
  },
  system: {
    avgOrderLatencyMs: 0,
    apiErrorCount: 0,
    lastDataSync: new Date()
  },
  openPositions: []
};

// Create the store
export const metricsStore = writable<AllMetrics | null>(null);

// Flag to track if polling is active
let pollingActive = false;
let pollingInterval: number | null = null;

// Function to fetch the latest metrics
export async function updateMetrics(): Promise<void> {
  try {
    // Call the real backend function
    const metrics = await GetLatestMetrics();

    // Convert any string dates to Date objects
    if (metrics.portfolio && metrics.portfolio.timestamp) {
      metrics.portfolio.timestamp = new Date(metrics.portfolio.timestamp);
    }

    if (metrics.system && metrics.system.lastDataSync) {
      metrics.system.lastDataSync = new Date(metrics.system.lastDataSync);
    }

    metricsStore.set(metrics);
  } catch (error) {
    console.error("Failed to fetch metrics:", error);
  }
}

// Start polling for metrics updates
export function startMetricsPolling(intervalMs: number = 10000): () => void {
  const interval = setInterval(updateMetrics, intervalMs);

  // Return cleanup function
  return () => clearInterval(interval);
}

// Test alert notification
export async function testAlertNotification(channelType: string, message: string = "This is a test alert from TraderAdmin."): Promise<boolean> {
  try {
    await window.go.main.App.TestAlertNotification(channelType, message);
    return true;
  } catch (error) {
    console.error(`Failed to send test ${channelType} alert:`, error);
    throw error;
  }
}
