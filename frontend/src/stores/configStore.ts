// @ts-ignore - Svelte types may not be properly configured in the project
import { writable, get } from 'svelte/store';

// Import from the generated Wails bindings
import { GetConfig, UpdateConfig, SaveConfigurationAndRestart, PauseTradingServices, ResumeTradingServices } from '../wailsjs/go/main/App';

// Import the AllMetrics type definition
import type { AllMetrics } from './metricsStore';

// Declare the global window interface to extend it with Wails properties
declare global {
  interface Window {
    go: {
      main: {
        App: {
          // Methods from configStore.ts
          GetConfig: () => Promise<Configuration>;
          UpdateConfig: (config: Configuration) => Promise<void>;
          SaveConfigurationAndRestart: (config: Configuration) => Promise<void>;
          PauseTradingServices: () => Promise<void>;
          ResumeTradingServices: () => Promise<void>;
          // Methods from metricsStore.ts
          GetLatestMetrics: () => Promise<AllMetrics>;
          TestAlertNotification: (channelType: string, message: string) => Promise<void>;
        }
      }
    }
  }
}

// For now, we'll define a simple type that matches our config structure
export interface Configuration {
  General: {
    LogLevel: string;
  };
  IBKRConnection: {
    Host: string;
    Port: number;
    ClientIDTrading: number;
    ClientIDData: number;
    AccountCode: string;
    ReadOnlyAPI: boolean;
  };
  TradingParameters: {
    GlobalMaxConcurrentPositions: number;
    DefaultRiskPerTradePercentage: number;
    EmergencyStopLossPercentage: number;
  };
  OptionsFilters: {
    // Liquidity
    MinOpenInterest: number;
    MaxBidAskSpreadPercentage: number;
    // Volatility
    UseIVRankFilter: boolean;
    MinIVRank: number;
    MaxIVRank: number;
    UseIVSkewFilter: boolean;
    MinPutCallIVSkewPercentage: number;
    MaxPutCallIVSkewPercentage: number;
    // Probability & Risk/Reward
    UsePOPFilter: boolean;
    MinProbabilityOfProfitPercentage: number;
    UseWidthVsExpectedMoveFilter: boolean;
    MaxSpreadWidthVsExpectedMovePercentage: number;
  };
  GreekLimits: {
    UseGreekLimits: boolean;
    MaxAbsPositionDelta: number;
    MaxAbsPositionGamma: number;
    MaxAbsPositionVega: number;
    MinPositionTheta: number;
  };
  TradeTiming: {
    // Dynamic DTE Calculation
    UseDynamicDTE: boolean;
    TargetDTEMode: string;
    DTEAtrPeriod: number;
    DTEAtrCoefficient: number;
    FixedTargetDTE: number;
    MinDTE: number;
    MaxDTE: number;
    // Event Avoidance
    AvoidEarningsDaysBefore: number;
    AvoidEarningsDaysAfter: number;
    AvoidExDividendDaysBefore: number;
  };
  StrategyDefaults: Record<string, Record<string, any>>;
  Kubernetes: {
    Namespace: string;
    ConfigMapName: string;
    OrchestratorDeploymentName: string;
  };
  Schedule: {
    TradingStartTime: string;
    TradingEndTime: string;
    WeekendTrading: boolean;
  };
  TradingSchedule: {
    Enabled: boolean;
    StartTimeUTC: string;
    StopTimeUTC: string;
    DaysOfWeek: string[];
  };
  AlertsConfig: {
    Enabled: boolean;
    Thresholds: {
      MaxOrderLatencyMs: number;
      MinDailyRealizedPnl: number;
      MaxPortfolioDrawdownPercentageToday: number;
      MaxApiErrorsPerHour: number;
    };
    Notifications: {
      Email: {
        Enabled: boolean;
        Recipients: string[];
        SmtpHost: string;
        SmtpPort: number;
        SmtpUser: string;
        SmtpPass: string;
      };
      Slack: {
        Enabled: boolean;
        WebhookUrl: string;
      };
    };
  };
}

// Create a writable store for the configuration
export const currentConfig = writable<Configuration | null>(null);

// Define a function to load the configuration from the backend
export async function loadConfig(): Promise<boolean> {
  try {
    // Call the real Wails backend function
    const config = await GetConfig();
    console.log('Received config from backend:', config);
    currentConfig.set(config);
    return true;
  } catch (error) {
    console.error("Failed to load configuration:", error);
    return false;
  }
}

// Update config in the store without saving to backend
export function updateConfig(config: Configuration): void {
  currentConfig.set(config);
}

// Define a function to save the configuration to the backend
export async function saveConfig(config: Configuration, restartServices = false): Promise<boolean> {
  try {
    if (!config) {
      throw new Error("No configuration provided");
    }

    if (restartServices) {
      // Use the function that saves and restarts services
      await SaveConfigurationAndRestart(config);
    } else {
      // Use the regular update function
      await UpdateConfig(config);
    }

    return true;
  } catch (error) {
    console.error("Failed to save configuration:", error);
    throw error;
  }
}

// Functions for pausing and resuming trading services
export async function pauseTradingServices(): Promise<boolean> {
  try {
    await PauseTradingServices();
    return true;
  } catch (error) {
    console.error("Failed to pause trading services:", error);
    throw error;
  }
}

export async function resumeTradingServices(): Promise<boolean> {
  try {
    await ResumeTradingServices();
    return true;
  } catch (error) {
    console.error("Failed to resume trading services:", error);
    throw error;
  }
}
