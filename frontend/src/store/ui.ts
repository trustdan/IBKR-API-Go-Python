import { writable, get, derived } from 'svelte/store';

// Initialize with default values
const storedTab = localStorage.getItem('activeTab');
export const activeTab = writable(storedTab || 'overview');

// Save tab selection to localStorage when it changes
activeTab.subscribe(value => {
  localStorage.setItem('activeTab', value);
});

// Track form dirty state per tab
export const dirtyForms = writable<Record<string, boolean>>({});

// Confirm before switching tabs with unsaved changes
export function confirmTabChange(newTab: string): boolean {
  const dirty = get(dirtyForms);
  const current = get(activeTab);

  if (dirty[current]) {
    return confirm('You have unsaved changes. Switch tabs anyway?');
  }
  return true;
}

// Dark mode setting
const storedTheme = localStorage.getItem('theme');
export const darkMode = writable(storedTheme === 'dark');

// Update theme when darkMode changes
darkMode.subscribe(value => {
  const theme = value ? 'dark' : 'light';
  localStorage.setItem('theme', theme);

  // Apply theme to the document
  if (value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
});

// Sidebar collapsed state
const storedSidebarState = localStorage.getItem('sidebarCollapsed');
export const sidebarCollapsed = writable(storedSidebarState === 'true');

// Update sidebar state when it changes
sidebarCollapsed.subscribe(value => {
  localStorage.setItem('sidebarCollapsed', String(value));
});

// Keep track of screen size for responsive layouts
export const windowWidth = writable(window.innerWidth);
export const windowHeight = writable(window.innerHeight);
export const isSmallScreen = derived(windowWidth, $width => $width < 768);
export const isMediumScreen = derived(windowWidth, $width => $width >= 768 && $width < 1024);
export const isLargeScreen = derived(windowWidth, $width => $width >= 1024);

// Keyboard shortcuts visible
export const keyboardShortcutsVisible = writable(false);

// Global search visible
export const globalSearchVisible = writable(false);

// Setup window resize listener
if (typeof window !== 'undefined') {
  const handleResize = () => {
    windowWidth.set(window.innerWidth);
    windowHeight.set(window.innerHeight);
  };

  window.addEventListener('resize', handleResize);
}
