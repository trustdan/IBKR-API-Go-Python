<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import {
    LoadConfig,
    SaveConfig,
    GetContainers,
    PauseStack,
    UnpauseStack,
    SaveAndRestart,
    Status,
    DeployStack
  } from '../wailsjs/go/main/App.js';
  import SystemStatus from './components/SystemStatus.svelte';

  // Theme management
  let isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

  function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode', isDarkMode);
    localStorage.setItem('darkMode', isDarkMode.toString());
  }

  // Tabs and components
  let activeTab = 'trading';
  let containerStatus = 'Unknown';
  let statusError = '';
  let containers = [];
  let config = null;
  let loading = false;
  let saving = false;

  // Setup periodic refresh
  let refreshTimer;

  // Add logging
  let actionLog = [];
  const MAX_LOG_ENTRIES = 50;

  function logAction(action, result = null, error = null) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = {
      timestamp,
      action,
      result,
      error,
      success: !error
    };
    console.log(`[${timestamp}] ${action}`, result || '', error || '');
    actionLog = [logEntry, ...actionLog.slice(0, MAX_LOG_ENTRIES - 1)];
  }

  onMount(async () => {
    try {
      // Load saved theme preference
      const savedTheme = localStorage.getItem('darkMode');
      if (savedTheme !== null) {
        isDarkMode = savedTheme === 'true';
        document.body.classList.toggle('dark-mode', isDarkMode);
      }

      logAction('Application Started');

      // Load initial configuration
      logAction('Loading Configuration');
      config = await LoadConfig();
      logAction('Configuration Loaded', { success: true });

      // Refresh container status initially
      await refreshContainers();

      // Setup periodic refresh (every 5 seconds)
      refreshTimer = setInterval(refreshContainers, 5000);
    } catch (err) {
      console.error('Failed to initialize:', err);
      statusError = err.message || 'Failed to initialize';
      logAction('Initialization Failed', null, err);
    }
  });

  onDestroy(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer);
    }
    logAction('Application Shutdown');
  });

  async function refreshContainers() {
    try {
      // Get container status
      containerStatus = await Status();

      // Get container list
      containers = await GetContainers();

      // Debug log
      console.log('DEBUG: Container data received:', JSON.stringify(containers));

      // Check if containers have the proper shape
      if (containers && containers.length > 0) {
        console.log('DEBUG: First container:', containers[0]);
        console.log('DEBUG: Container field types:', {
          Name: typeof containers[0].Name,
          Status: typeof containers[0].Status,
          Created: typeof containers[0].Created,
          CreatedDate: new Date(containers[0].Created).toString()
        });
      }

      // Clear any previous errors
      statusError = '';

      // Only log this action occasionally to avoid spamming the log
      if (Math.random() < 0.1) { // Log approximately 1 in 10 refreshes
        logAction('Refreshed Containers', {
          status: containerStatus,
          count: containers.length
        });
      }
    } catch (err) {
      console.error('Error refreshing containers:', err);
      statusError = err.message || 'Error refreshing containers';
      logAction('Container Refresh Failed', null, err);
    }
  }

  async function saveAndRestart() {
    if (!config) return;

    saving = true;
    logAction('Save and Restart Initiated');

    try {
      await SaveAndRestart(config);
      // Show success message
      logAction('Save and Restart Completed', { success: true });
      alert('Configuration saved and services restarted successfully');
    } catch (err) {
      console.error('Failed to save and restart:', err);
      logAction('Save and Restart Failed', null, err);
      alert('Error: ' + (err.message || 'Failed to save configuration'));
    } finally {
      saving = false;
      await refreshContainers();
    }
  }

  async function pauseAllContainers() {
    if (containerStatus === 'No Containers') {
      logAction('Pause Containers', { status: 'No containers to pause' });
      alert('No containers to pause');
      return;
    }

    logAction('Pause All Containers Initiated');
    try {
      await PauseStack();
      logAction('Pause All Containers Completed', { success: true });
      await refreshContainers();
    } catch (err) {
      console.error('Failed to pause containers:', err);
      logAction('Pause All Containers Failed', null, err);
      alert('Error: ' + (err.message || 'Failed to pause containers'));
    }
  }

  async function unpauseAllContainers() {
    if (containerStatus === 'No Containers') {
      logAction('Unpause Containers', { status: 'No containers to unpause' });
      alert('No containers to unpause');
      return;
    }

    logAction('Unpause All Containers Initiated');
    try {
      await UnpauseStack();
      logAction('Unpause All Containers Completed', { success: true });
      await refreshContainers();
    } catch (err) {
      console.error('Failed to unpause containers:', err);
      logAction('Unpause All Containers Failed', null, err);
      alert('Error: ' + (err.message || 'Failed to unpause containers'));
    }
  }

  async function deployStack() {
    logAction('Deploy Stack Initiated');
    try {
      await DeployStack();
      logAction('Deploy Stack Completed', { success: true });
      await refreshContainers();
    } catch (err) {
      console.error('Failed to deploy stack:', err);
      logAction('Deploy Stack Failed', null, err);
      alert('Error: ' + (err.message || 'Failed to deploy stack'));
    }
  }

  // Clear log function
  function clearLog() {
    actionLog = [];
    logAction('Log Cleared');
  }
</script>

<svelte:head>
  <style>
    html {
      background-color: #1a1a1a;
    }

    body {
      margin: 0;
      padding: 0;
      background-color: #1a1a1a;
      color: #fff;
      transition: background-color 0.3s, color 0.3s;
      min-height: 100vh;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    }

    body.dark-mode {
      background-color: #1a1a1a;
      color: #ffffff;
    }

    /* Light mode override */
    body:not(.dark-mode) {
      background-color: #f5f5f5;
      color: #333;
    }

    /* Apply styles to all buttons in dark mode */
    body.dark-mode button,
    body.dark-mode input[type="button"] {
      background-color: #333;
      color: #fff;
      border-color: #444;
    }

    /* Fix the Refresh Status button */
    body.dark-mode input[type="button"] {
      background-color: #333;
      color: #fff;
      border: 1px solid #444;
      padding: 0.5rem 1rem;
      border-radius: 4px;
    }

    body.dark-mode input[type="button"]:hover {
      background-color: #444;
    }
  </style>
</svelte:head>

<main class:dark-mode={isDarkMode}>
  <div class="container">
    <header>
      <h1>IBKR Trader Admin</h1>
      <div class="header-controls">
        <button class="theme-toggle" on:click={toggleTheme} title="Toggle dark/light mode">
          {isDarkMode ? '☀️' : '🌙'}
        </button>
        <div class="status-bar">
          <div class="status-indicator {containerStatus.toLowerCase()}">
            Status: {containerStatus}
          </div>
          {#if statusError}
            <div class="error-message">{statusError}</div>
          {/if}
        </div>
      </div>
    </header>

    <div class="tabs">
      <button
        class:active={activeTab === 'trading'}
        on:click={() => activeTab = 'trading'}>
        Trading
      </button>
      <button
        class:active={activeTab === 'strategy'}
        on:click={() => activeTab = 'strategy'}>
        Strategy
      </button>
      <button
        class:active={activeTab === 'options'}
        on:click={() => activeTab = 'options'}>
        Options
      </button>
      <button
        class:active={activeTab === 'system'}
        on:click={() => activeTab = 'system'}>
        System
      </button>
      <button
        class:active={activeTab === 'logs'}
        on:click={() => activeTab = 'logs'}>
        Logs
      </button>
    </div>

    <div class="content">
      {#if !config}
        <div class="loading">Loading configuration...</div>
      {:else}
        <!-- Trading Settings Tab -->
        <div class="tab-content" class:active={activeTab === 'trading'}>
          <h2>Trading Settings</h2>
          {#if config.Trading}
            <div class="form-group">
              <label for="mode">Trading Mode</label>
              <select id="mode" bind:value={config.Trading.Mode}>
                <option value="PAPER">Paper Trading</option>
                <option value="LIVE">Live Trading</option>
              </select>
            </div>
            <div class="form-group">
              <label for="max-positions">Max Positions</label>
              <input type="number" id="max-positions" bind:value={config.Trading.MaxPositions} min="1" max="20">
            </div>
            <div class="form-group">
              <label for="max-daily-trades">Max Daily Trades</label>
              <input type="number" id="max-daily-trades" bind:value={config.Trading.MaxDailyTrades} min="1" max="20">
            </div>
            <div class="form-group">
              <label for="risk-per-trade">Risk Per Trade (%)</label>
              <input type="number" id="risk-per-trade" bind:value={config.Trading.RiskPerTrade} min="0.01" max="0.1" step="0.01">
              <span class="hint">Percentage of account size (e.g., 0.02 = 2%)</span>
            </div>
            <div class="form-group">
              <label for="price-improvement">Price Improvement Factor</label>
              <input type="number" id="price-improvement" bind:value={config.Trading.PriceImprovementFactor} min="0" max="1" step="0.1">
              <span class="hint">0.5 = midpoint, &lt;0.5 = closer to bid</span>
            </div>
            <div class="form-group">
              <label>
                <input type="checkbox" bind:checked={config.Trading.AllowLateDayEntry}>
                Allow Late Day Entry
              </label>
            </div>
          {/if}
        </div>

        <!-- Strategy Settings Tab -->
        <div class="tab-content" class:active={activeTab === 'strategy'}>
          <h2>Strategy Settings</h2>
          {#if config.Strategy}
            <div class="strategy-section">
              <h3>High Base Strategy</h3>
              <div class="form-group">
                <label for="high-max-atr">Max ATR Ratio</label>
                <input type="number" id="high-max-atr" bind:value={config.Strategy.HighBase.MaxATRRatio} min="0.5" max="5" step="0.1">
              </div>
              <div class="form-group">
                <label for="high-min-rsi">Min RSI</label>
                <input type="number" id="high-min-rsi" bind:value={config.Strategy.HighBase.MinRSI} min="50" max="80">
              </div>
            </div>

            <div class="strategy-section">
              <h3>Low Base Strategy</h3>
              <div class="form-group">
                <label for="low-min-atr">Min ATR Ratio</label>
                <input type="number" id="low-min-atr" bind:value={config.Strategy.LowBase.MinATRRatio} min="0.1" max="1" step="0.1">
              </div>
              <div class="form-group">
                <label for="low-max-rsi">Max RSI</label>
                <input type="number" id="low-max-rsi" bind:value={config.Strategy.LowBase.MaxRSI} min="20" max="50">
              </div>
            </div>

            <div class="strategy-section">
              <h3>Bull Pullback</h3>
              <div class="form-group">
                <label for="bull-rsi">RSI Threshold</label>
                <input type="number" id="bull-rsi" bind:value={config.Strategy.BullPullback.RSIThreshold} min="30" max="60">
              </div>
            </div>

            <div class="strategy-section">
              <h3>Bear Rally</h3>
              <div class="form-group">
                <label for="bear-rsi">RSI Threshold</label>
                <input type="number" id="bear-rsi" bind:value={config.Strategy.BearRally.RSIThreshold} min="40" max="70">
              </div>
            </div>
          {/if}
        </div>

        <!-- Options Settings Tab -->
        <div class="tab-content" class:active={activeTab === 'options'}>
          <h2>Options Settings</h2>
          {#if config.Options}
            <div class="form-group">
              <label for="min-dte">Min Days to Expiry</label>
              <input type="number" id="min-dte" bind:value={config.Options.MinDTE} min="1" max="90">
            </div>
            <div class="form-group">
              <label for="max-dte">Max Days to Expiry</label>
              <input type="number" id="max-dte" bind:value={config.Options.MaxDTE} min="1" max="120">
            </div>
            <div class="form-group">
              <label for="min-delta">Min Delta</label>
              <input type="number" id="min-delta" bind:value={config.Options.MinDelta} min="0.1" max="0.5" step="0.05">
            </div>
            <div class="form-group">
              <label for="max-delta">Max Delta</label>
              <input type="number" id="max-delta" bind:value={config.Options.MaxDelta} min="0.3" max="0.9" step="0.05">
            </div>
            <div class="form-group">
              <label for="max-spread-cost">Max Spread Cost ($)</label>
              <input type="number" id="max-spread-cost" bind:value={config.Options.MaxSpreadCost} min="100" max="2000" step="50">
            </div>
            <div class="form-group">
              <label for="min-reward-risk">Min Reward/Risk Ratio</label>
              <input type="number" id="min-reward-risk" bind:value={config.Options.MinRewardRisk} min="1" max="5" step="0.1">
            </div>
          {/if}
        </div>

        <!-- System Tab -->
        <div class="tab-content" class:active={activeTab === 'system'}>
          <h2>System Status</h2>

          <!-- Add the SystemStatus component -->
          <SystemStatus />

          <h3>Container Management</h3>
          <div class="container-list">
            {#if containers.length === 0}
              <p>No containers found.</p>
            {:else}
              <table>
                <thead>
                  <tr>
                    <th>Container</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {#each containers as container}
                    <tr>
                      <td>{container.Name}</td>
                      <td class="{
                        container.Status ? (
                          container.Status.includes('Running') || container.Status.includes('Up') ? 'running' :
                          container.Status.includes('Paused') ? 'paused' :
                          container.Status.includes('Stopped') || container.Status.includes('Exited') ? 'stopped' : 'unknown'
                        ) : 'unknown'
                      }">{container.Status || 'Unknown'}</td>
                      <td>{container.Created ? new Date(container.Created).toLocaleString() : 'Unknown'}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            {/if}
          </div>

          <div class="footer-actions">
            <div class="footer-left">
              <button class="btn" on:click={pauseAllContainers}>Pause All</button>
              <button class="btn" on:click={unpauseAllContainers}>Unpause All</button>
              <button class="btn" on:click={refreshContainers}>Refresh</button>
            </div>
            <div class="footer-right">
              <button class="btn deploy" on:click={deployStack}>Deploy Stack</button>
            </div>
          </div>
        </div>

        <!-- Logs Tab -->
        <div class="tab-content" class:active={activeTab === 'logs'}>
          <h2>Action Logs</h2>
          <div class="logs-header">
            <p>Recent application actions and results</p>
            <button class="btn secondary" on:click={clearLog}>Clear Log</button>
          </div>

          <div class="log-container">
            {#if actionLog.length === 0}
              <p class="empty-log">No log entries yet.</p>
            {:else}
              <table class="log-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Action</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {#each actionLog as entry}
                    <tr class={entry.error ? 'error' : (entry.success ? 'success' : '')}>
                      <td>{entry.timestamp}</td>
                      <td>{entry.action}</td>
                      <td>
                        {#if entry.error}
                          <span class="log-error">Error: {entry.error.message || 'Unknown error'}</span>
                        {:else if entry.result}
                          <span class="log-success">Success</span>
                        {:else}
                          <span class="log-info">Info</span>
                        {/if}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            {/if}
          </div>
        </div>
      {/if}
    </div>

    <!-- Fixed position Save Button -->
    <div class="main-footer">
      <button
        class="btn primary"
        on:click={saveAndRestart}
        disabled={saving || !config}>
        {saving ? 'Saving...' : 'Save & Restart'}
      </button>
    </div>
  </div>
</main>

<style>
  /* Base styles with dark mode support */
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  }

  main.dark-mode {
    background-color: #1a1a1a;
  }

  main:not(.dark-mode) {
    background-color: #f5f5f5;
  }

  .container {
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem;
    min-height: calc(100vh - 4rem);
  }

  /* Loading state */
  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  :global(body.dark-mode) .loading {
    color: #aaa;
  }

  /* Header and tabs */
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .theme-toggle {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 50%;
    cursor: pointer;
    background-color: #fff;
    font-size: 1.2rem;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.3s, border-color 0.3s;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .theme-toggle:hover {
    background-color: #f0f0f0;
  }

  .status-bar {
    display: flex;
    align-items: center;
  }

  .status-indicator {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    margin-right: 1rem;
    font-weight: bold;
  }

  .status-indicator.running {
    background-color: #4caf50;
    color: white;
  }

  .status-indicator.partial {
    background-color: #ff9800;
    color: white;
  }

  .status-indicator.no {
    background-color: #f44336;
    color: white;
  }

  .status-indicator.unknown {
    background-color: #9e9e9e;
    color: white;
  }

  .error-message {
    color: #f44336;
  }

  .tabs {
    display: flex;
    margin-bottom: 1rem;
    border-bottom: 1px solid #ddd;
  }

  .tabs button {
    padding: 0.5rem 1rem;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 1rem;
    border-bottom: 2px solid transparent;
  }

  .tabs button.active {
    border-bottom: 2px solid #2196f3;
    font-weight: bold;
  }

  /* Tab content */
  .tab-content {
    display: none;
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }

  .tab-content.active {
    display: block;
  }

  :global(body.dark-mode) .tab-content {
    background-color: #2a2a2a;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  /* Form elements */
  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
  }

  input[type="number"],
  input[type="text"],
  select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    background-color: #fff;
    color: #333;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
  }

  :global(body.dark-mode) input[type="number"],
  :global(body.dark-mode) input[type="text"],
  :global(body.dark-mode) select {
    background-color: #333;
    color: #fff;
    border-color: #555;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
  }

  .hint {
    display: block;
    font-size: 0.8rem;
    color: #666;
    margin-top: 0.25rem;
    padding-left: 2px;
  }

  :global(body.dark-mode) .hint {
    color: #aaa;
  }

  /* Strategy sections */
  .strategy-section {
    margin-bottom: 1.5rem;
    padding: 1.5rem;
    background-color: #fff;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }

  .strategy-section h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    color: #333;
    text-align: center;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
  }

  /* Container table */
  .container-list {
    margin-bottom: 2rem;
    background-color: #fff;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }

  :global(body.dark-mode) .container-list {
    background-color: #2a2a2a;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  table th,
  table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  :global(body.dark-mode) table th,
  :global(body.dark-mode) table td {
    border-bottom: 1px solid #444;
  }

  table th {
    font-weight: bold;
    color: #555;
  }

  :global(body.dark-mode) table th {
    color: #ccc;
  }

  td.unknown {
    color: #9e9e9e;
  }

  td.running {
    color: #4caf50;
    font-weight: bold;
  }

  td.paused {
    color: #ff9800;
    font-weight: bold;
  }

  td.stopped, td.exited {
    color: #f44336;
    font-weight: bold;
  }

  /* Footer and action buttons */
  .footer-actions {
    background-color: transparent;
    padding: 0.75rem 0;
    border-radius: 0;
    margin-top: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: none;
    border-top: 1px solid #e0e0e0;
  }

  .footer-left {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .footer-right {
    display: flex;
    justify-content: flex-end;
  }

  /* Button styling */
  .btn {
    padding: 0.5rem 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    cursor: pointer;
    background-color: #f5f5f5;
    color: #333;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 100px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
  }

  .btn:hover {
    background-color: #e8e8e8;
    box-shadow: 0 2px 3px rgba(0,0,0,0.1);
  }

  .btn.primary {
    background-color: #2196f3;
    color: white;
    border-color: #1e88e5;
  }

  .btn.primary:hover {
    background-color: #1976d2;
  }

  .btn.deploy {
    background-color: #4caf50;
    color: white;
    border-color: #43a047;
  }

  .btn.deploy:hover {
    background-color: #43a047;
  }

  /* Dark mode overrides */
  :global(body.dark-mode) .strategy-section {
    background-color: #2a2a2a;
    border-color: #444;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  :global(body.dark-mode) .strategy-section h3 {
    color: #fff;
    border-bottom-color: #444;
  }

  :global(body.dark-mode) .footer-actions {
    background-color: transparent;
    border-top-color: #444;
    box-shadow: none;
  }

  :global(body.dark-mode) .btn {
    background-color: #333;
    color: #fff;
    border-color: #555;
    box-shadow: 0 1px 2px rgba(0,0,0,0.2);
  }

  :global(body.dark-mode) .btn:hover {
    background-color: #444;
    box-shadow: 0 2px 3px rgba(0,0,0,0.25);
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .action-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
  }

  /* Log Styles */
  .logs-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .log-container {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    background-color: #f9f9f9;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
  }

  :global(body.dark-mode) .log-container {
    background-color: #2a2a2a;
    border-color: #444;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
  }

  .empty-log {
    text-align: center;
    color: #666;
    padding: 2rem;
  }

  .log-table {
    width: 100%;
  }

  .log-table tr.error {
    background-color: rgba(244, 67, 54, 0.1);
  }

  .log-table tr.success {
    background-color: rgba(76, 175, 80, 0.1);
  }

  .log-error {
    color: #f44336;
    font-weight: bold;
  }

  .log-success {
    color: #4caf50;
    font-weight: bold;
  }

  .log-info {
    color: #2196f3;
    font-weight: bold;
  }

  /* Dark mode overrides */
  :global(body.dark-mode) .theme-toggle {
    background-color: #333;
    color: #fff;
  }

  :global(body.dark-mode) .theme-toggle:hover {
    background-color: #444;
  }

  /* Fix tabs in dark mode */
  :global(body.dark-mode) .tabs {
    border-bottom-color: #444;
  }

  :global(body.dark-mode) .tabs button {
    color: #fff;
  }

  :global(body.dark-mode) .tabs button.active {
    border-bottom-color: #64b5f6;
  }

  /* Fix form elements in dark mode */
  :global(body.dark-mode) input[type="number"],
  :global(body.dark-mode) input[type="text"],
  :global(body.dark-mode) select {
    background-color: #333;
    color: #fff;
    border-color: #555;
  }

  :global(body.dark-mode) .hint {
    color: #aaa;
  }

  :global(body.dark-mode) .strategy-section {
    background-color: #2a2a2a;
    border: 1px solid #444;
  }

  :global(body.dark-mode) table th,
  :global(body.dark-mode) table td {
    border-bottom-color: #444;
  }

  :global(body.dark-mode) .log-container {
    background-color: #2a2a2a;
    border-color: #444;
  }

  :global(body.dark-mode) .btn {
    background-color: #333;
    color: #fff;
  }

  :global(body.dark-mode) .btn.primary {
    background-color: #1976d2;
  }

  :global(body.dark-mode) .btn.primary:hover {
    background-color: #1565c0;
  }

  :global(body.dark-mode) .log-table tr.error {
    background-color: rgba(244, 67, 54, 0.2);
  }

  :global(body.dark-mode) .log-table tr.success {
    background-color: rgba(76, 175, 80, 0.2);
  }

  :global(body.dark-mode) .status-indicator {
    opacity: 0.9;
  }

  :global(body.dark-mode) .empty-log {
    color: #aaa;
  }

  /* Fix the system status cards */
  :global(.system-status-card) {
    background-color: #fff;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    border: 1px solid #e0e0e0;
  }

  :global(.system-status-title) {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #333;
  }

  :global(.system-status-text) {
    color: #555;
  }

  :global(body.dark-mode) :global(.system-status-card) {
    background-color: #2a2a2a;
    border-color: #444;
  }

  :global(body.dark-mode) :global(.system-status-title) {
    color: #fff;
  }

  :global(body.dark-mode) :global(.system-status-text) {
    color: #e0e0e0;
  }

  /* Fix heading colors */
  :global(body.dark-mode) h1,
  :global(body.dark-mode) h2,
  :global(body.dark-mode) h3 {
    color: #fff;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    box-shadow: none;
  }

  :global(body.dark-mode) .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    box-shadow: none;
  }

  /* Refresh Status button styling */
  :global(input[type="button"]) {
    padding: 0.5rem 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    cursor: pointer;
    background-color: #f5f5f5;
    color: #333;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
  }

  :global(input[type="button"]:hover) {
    background-color: #e8e8e8;
    box-shadow: 0 2px 3px rgba(0,0,0,0.1);
  }

  :global(body.dark-mode) :global(input[type="button"]) {
    background-color: #333;
    color: #fff;
    border-color: #555;
    box-shadow: 0 1px 2px rgba(0,0,0,0.2);
  }

  :global(body.dark-mode) :global(input[type="button"]:hover) {
    background-color: #444;
    box-shadow: 0 2px 3px rgba(0,0,0,0.25);
  }

  /* Main footer with Save button */
  .main-footer {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 0;
    padding: 1rem;
    z-index: 100;
    background-color: #1a1a1a;
    border-top: 1px solid #444;
    display: flex;
    justify-content: flex-end;
  }

  :global(body.dark-mode) .main-footer {
    background-color: #1a1a1a;
    border-top: 1px solid #444;
  }

  .main-footer .btn {
    min-width: 120px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  }

  :global(body.dark-mode) .main-footer .btn {
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  }

  /* Add bottom margin to content to avoid overlap with fixed footer */
  .content {
    margin-bottom: 6rem;
  }
</style>
