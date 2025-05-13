// @ts-ignore - Svelte types may not be properly configured in the project
import { writable } from 'svelte/store';

// Define the valid tab IDs
export type TabId =
  | 'monitoring'
  | 'connection'
  | 'scheduling'
  | 'strategies'
  | 'alerts'
  | 'logs'
  | 'settings';

// Create a writable store with 'monitoring' as the default tab
export const activeTab = writable<TabId>('monitoring');

// Helper function to change the active tab
export function setActiveTab(tabId: TabId): void {
  activeTab.set(tabId);
}
