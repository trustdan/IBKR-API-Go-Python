<script lang="ts">
  import { onMount } from 'svelte';
  import Sidebar from './components/Sidebar.svelte';
  import StatusBar from './components/StatusBar.svelte';
  import MonitoringTab from './tabs/MonitoringTab.svelte';
  import ConnectionTab from './tabs/ConnectionTab.svelte';
  import AlertsConfigurationTab from './tabs/AlertsConfigurationTab.svelte';
  import SchedulingTab from './tabs/SchedulingTab.svelte';

  // Import store functions
  import { loadSchema } from './stores/schemaStore';
  import { loadConfig } from './stores/configStore';
  import { updateStatus, startStatusPolling } from './stores/statusStore';
  import { updateMetrics } from './stores/metricsStore';
  import { activeTab } from './stores/activeTab';

  // Application state
  let loading = true;
  let pollingCleanup: (() => void) | null = null;

  // Loading and error states
  let isLoading = true;
  let hasError = false;
  let errorMessage = '';

  // Initialize the application
  onMount(async () => {
    try {
      // Load schema from backend
      const schemaLoaded = await loadSchema();

      // Load configuration
      await loadConfig();

      // Initialize status
      await updateStatus();
      pollingCleanup = startStatusPolling(5000);

      // Get initial metrics
      await updateMetrics();

      // Set loading complete
      isLoading = false;
    } catch (error) {
      console.error("Application initialization error:", error);
      isLoading = false;
      hasError = true;
      errorMessage = error instanceof Error ? error.message : String(error);
    }

    return () => {
      if (pollingCleanup) {
        pollingCleanup();
      }
    };
  });
</script>

<main class="app">
  {#if isLoading}
    <div class="loading-screen">
      <div class="spinner"></div>
      <p>Loading TraderAdmin...</p>
    </div>
  {:else if hasError}
    <div class="error-screen">
      <div class="error-icon">⚠️</div>
      <h2>Failed to initialize application</h2>
      <p>{errorMessage}</p>
      <button on:click={() => window.location.reload()}>Retry</button>
    </div>
  {:else}
    <div class="app-layout">
      <Sidebar />

      <div class="main-content">
        <StatusBar />

        <div class="tab-content">
          {#if $activeTab === 'connection'}
            <ConnectionTab />
          {:else if $activeTab === 'scheduling'}
            <SchedulingTab />
          {:else if $activeTab === 'strategies'}
            <div class="placeholder-tab">
              <h1>Strategies</h1>
              <p>This tab will allow you to configure and manage trading strategies.</p>
            </div>
          {:else if $activeTab === 'logs'}
            <div class="placeholder-tab">
              <h1>Logs</h1>
              <p>This tab will display system logs and debugging information.</p>
            </div>
          {:else if $activeTab === 'monitoring'}
            <MonitoringTab />
          {:else if $activeTab === 'alerts'}
            <AlertsConfigurationTab />
          {:else if $activeTab === 'settings'}
            <div class="placeholder-tab">
              <h1>Settings</h1>
              <p>This tab will allow you to configure general application settings.</p>
            </div>
          {:else}
            <div class="placeholder-tab">
              <h1>Tab not implemented</h1>
              <p>This functionality is not yet available.</p>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</main>

<style>
  /* App layout */
  .app {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .app-layout {
    display: flex;
    height: 100%;
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .tab-content {
    flex: 1;
    overflow: auto;
    padding: 20px;
  }

  /* Placeholder styles */
  .placeholder-tab {
    padding: 2rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    max-width: 800px;
    margin: 0 auto;
  }

  .placeholder-tab h1 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #1e293b;
  }

  .placeholder-tab p {
    color: #64748b;
    line-height: 1.6;
  }

  /* Loading and error screens */
  .loading-screen, .error-screen {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100vw;
    background-color: #f8fafc;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top-color: #3b82f6;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .error-screen h2 {
    margin: 0 0 1rem 0;
    color: #ef4444;
  }

  .error-screen button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-weight: 500;
  }

  .error-screen button:hover {
    background-color: #2563eb;
  }
</style>
