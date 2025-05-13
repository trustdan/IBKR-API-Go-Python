import { vi } from 'vitest'
import '@testing-library/jest-dom'

// Mock the wailsjs runtime
vi.mock('../wailsjs/runtime', () => ({
  WindowSetTitle: vi.fn(),
  EventsOn: vi.fn(),
  EventsOff: vi.fn(),
  EventsEmit: vi.fn(),
  LogDebug: vi.fn(),
  LogError: vi.fn(),
  LogFatal: vi.fn(),
  LogInfo: vi.fn(),
  LogWarning: vi.fn(),
}))

// Mock backend app API
vi.mock('../wailsjs/go/main/App', () => ({
  GetConfigSchema: vi.fn().mockResolvedValue('{}'),
  LoadConfig: vi.fn().mockResolvedValue({}),
  SaveConfig: vi.fn().mockResolvedValue(null),
  GetStatus: vi.fn().mockResolvedValue({
    ibkr: { connected: true },
    services: [],
    activePositions: 0,
    tradingActive: false,
    isTradingHours: true,
    lastUpdated: new Date().toISOString(),
  }),
  GetLatestMetrics: vi.fn().mockResolvedValue({
    portfolio: {
      timestamp: new Date().toISOString(),
      equity: 100000,
      realizedPnlToday: 0,
      unrealizedPnl: 0,
      openPositionsCount: 0,
      buyingPower: 100000,
    },
    trades: {
      executedCount: 0,
      winCount: 0,
      lossCount: 0,
      winRate: 0,
      avgWinAmount: 0,
      avgLossAmount: 0,
    },
    system: {
      avgOrderLatencyMs: 0,
      apiErrorCount: 0,
      lastDataSync: new Date().toISOString(),
    },
    openPositions: [],
  }),
  PauseTradingServices: vi.fn().mockResolvedValue(null),
  ResumeTradingServices: vi.fn().mockResolvedValue(null),
  SaveConfigurationAndRestart: vi.fn().mockResolvedValue(null),
  TestIBKRConnection: vi.fn().mockResolvedValue(true),
  TestAlertNotification: vi.fn().mockResolvedValue(null),
}))
