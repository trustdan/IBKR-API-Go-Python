import { writable, derived } from 'svelte/store';
import { apiCall, toast } from '../lib/api';
import { LoadConfig, SaveConfig, BackupConfig } from '../../wailsjs/go/main/App';

// Define interfaces for our configuration
export interface Config {
  metadata: {
    version: string;
    created: string;
    description: string;
  };
  ibkr: {
    host: string;
    port: number;
    client_id: number;
    read_only: boolean;
  };
  trading: {
    mode: string;
    max_positions: number;
    risk_per_trade_pct: number;
  };
  auth: {
    realm: string;
    username: string;
    password_hash: string;
  };
  circuit_breaker: {
    enabled: boolean;
    max_loss_percent: number;
    max_error_count: number;
    cooldown_period: string;
  };
  // Add other configuration sections as needed
}

// Config store
export const configStore = writable<Config | null>(null);

// Schema store (for form generation)
export const schemaStore = writable<any>(null);

// Config version history
export const configHistory = writable<Config[]>([]);

// Derived store for config version
export const configVersion = derived(
  configStore,
  $config => $config?.metadata?.version || '0.0.0'
);

/**
 * Initialize the configuration
 */
export async function initialize(): Promise<boolean> {
  try {
    // Load config
    await loadConfig();
    return true;
  } catch (err) {
    console.error('Initialization failed:', err);
    return false;
  }
}

/**
 * Load configuration from backend
 */
export async function loadConfig(): Promise<Config> {
  const cfg = await apiCall(
    () => LoadConfig(),
    'Failed to load configuration'
  );

  // Add to history if different from current
  configStore.update(current => {
    if (current && JSON.stringify(current) !== JSON.stringify(cfg)) {
      configHistory.update(hist => {
        const newHist = [...hist, current];
        // Limit history size
        if (newHist.length > 10) newHist.shift();
        return newHist;
      });
    }
    return cfg;
  });

  return cfg;
}

/**
 * Save configuration to backend
 */
export async function saveConfig(newCfg: Config): Promise<void> {
  await apiCall(
    async () => {
      await SaveConfig(newCfg);
      configStore.set(newCfg);
      toast.success('Configuration saved successfully');
    },
    'Failed to save configuration'
  );
}

/**
 * Backup current configuration
 */
export async function backupConfig(): Promise<void> {
  await apiCall(
    async () => {
      await BackupConfig();
      toast.success('Configuration backed up successfully');
    },
    'Failed to backup configuration'
  );
}

/**
 * Undo last configuration change
 */
export function undoConfigChange(): void {
  configHistory.update(hist => {
    if (hist.length > 0) {
      const lastConfig = hist.pop();
      if (lastConfig) {
        configStore.set(lastConfig);
      }
      return hist;
    }
    return hist;
  });
}
