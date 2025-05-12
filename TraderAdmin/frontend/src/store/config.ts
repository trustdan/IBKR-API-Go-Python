import { writable } from 'svelte/store';
import type { Config } from '../types';

// Import the window Go runtime
declare global {
  interface Window {
    go: {
      main: {
        App: {
          GetConfigSchema: () => Promise<string>;
          LoadConfig: () => Promise<Config>;
          SaveConfig: (config: Config) => Promise<void>;
          GetStatus: () => Promise<any>;
          TestConnection: () => Promise<boolean>;
        }
      }
    }
  }
}

export const schema = writable<any>(null);
export const configStore = writable<Config | null>(null);
export const isLoading = writable<boolean>(true);
export const hasChanges = writable<boolean>(false);

export async function loadSchema() {
  try {
    // Use the GetConfigSchema method from the Go backend
    const raw = await window.go.main.App.GetConfigSchema();
    schema.set(JSON.parse(raw));
    return true;
  } catch (error) {
    console.error('Failed to load schema:', error);
    return false;
  }
}

export async function loadConfig() {
  isLoading.set(true);
  try {
    const cfg = await window.go.main.App.LoadConfig();
    configStore.set(cfg);
    hasChanges.set(false);
    return true;
  } catch (error) {
    console.error('Failed to load config:', error);
    return false;
  } finally {
    isLoading.set(false);
  }
}

export async function saveConfig(newCfg: Config) {
  isLoading.set(true);
  try {
    await window.go.main.App.SaveConfig(newCfg);
    configStore.set(newCfg);
    hasChanges.set(false);
    return true;
  } catch (error) {
    console.error('Failed to save config:', error);
    return false;
  } finally {
    isLoading.set(false);
  }
}

// Used by form components to track changes
export function updateConfig(path: string, value: any) {
  configStore.update(cfg => {
    if (!cfg) return cfg;

    const pathParts = path.split('.');
    let current: any = cfg;

    // Navigate to the nested object
    for (let i = 0; i < pathParts.length - 1; i++) {
      if (!current[pathParts[i]]) {
        current[pathParts[i]] = {};
      }
      current = current[pathParts[i]];
    }

    // Set the value
    current[pathParts[pathParts.length - 1]] = value;
    hasChanges.set(true);
    return cfg;
  });
}
