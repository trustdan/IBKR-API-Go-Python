<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import {
    LoadConfig,
    SaveConfig,
    GetContainers,
    PauseStack,
    UnpauseStack,
    SaveAndRestart,
    Status
  } from '../wailsjs/go/main/App.js';
  import SystemStatus from './components/SystemStatus.svelte';

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

  onMount(async () => {
    try {
      // Load initial configuration
      config = await LoadConfig();

      // Refresh container status initially
      await refreshContainers();

      // Setup periodic refresh (every 5 seconds)
      refreshTimer = setInterval(refreshContainers, 5000);
    } catch (err) {
      console.error('Failed to initialize:', err);
      statusError = err.message || 'Failed to initialize';
    }
  });

  onDestroy(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer);
    }
  });

  async function refreshContainers() {
    try {
      // Get container status
      containerStatus = await Status();

      // Get container list
      containers = await GetContainers();

      // Clear any previous errors
      statusError = '';
    } catch (err) {
      console.error('Error refreshing containers:', err);
      statusError = err.message || 'Error refreshing containers';
    }
  }

  async function saveAndRestart() {
    if (!config) return;

    saving = true;
    try {
      await SaveAndRestart(config);
      // Show success message
      alert('Configuration saved and services restarted successfully');
    } catch (err) {
      console.error('Failed to save and restart:', err);
      alert('Error: ' + (err.message || 'Failed to save configuration'));
    } finally {
      saving = false;
    }
  }

  async function pauseAllContainers() {
    if (containerStatus === 'No Containers') {
      alert('No containers to pause');
      return;
    }

    try {
      await PauseStack();
      await refreshContainers();
    } catch (err) {
      console.error('Failed to pause containers:', err);
      alert('Error: ' + (err.message || 'Failed to pause containers'));
    }
  }

  async function unpauseAllContainers() {
    if (containerStatus === 'No Containers') {
      alert('No containers to unpause');
      return;
    }

    try {
      await UnpauseStack();
      await refreshContainers();
    } catch (err) {
      console.error('Failed to unpause containers:', err);
      alert('Error: ' + (err.message || 'Failed to unpause containers'));
    }
  }
</script>

<main>
  <div class="container">
    <header>
      <h1>IBKR Trader Admin</h1>
      <div class="status-bar">
        <div class="status-indicator {containerStatus.toLowerCase()}">
          Status: {containerStatus}
        </div>
        {#if statusError}
          <div class="error-message">{statusError}</div>
        {/if}
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
                        container.Status.includes('Up') ? 'running' :
                        container.Status.includes('Paused') ? 'paused' : 'stopped'
                      }">{container.Status}</td>
                      <td>{new Date(container.Created).toLocaleString()}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            {/if}
          </div>

          <div class="action-buttons">
            <button class="btn" on:click={pauseAllContainers}>Pause All</button>
            <button class="btn" on:click={unpauseAllContainers}>Unpause All</button>
          </div>
        </div>
      {/if}
    </div>

    <div class="actions">
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
  .container {
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
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

  .tab-content {
    display: none;
  }

  .tab-content.active {
    display: block;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
  }

  .hint {
    display: block;
    font-size: 0.8rem;
    color: #666;
    margin-top: 0.25rem;
  }

  input[type="number"],
  input[type="text"],
  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .strategy-section {
    margin-bottom: 2rem;
    padding: 1rem;
    background-color: #f5f5f5;
    border-radius: 4px;
  }

  .strategy-section h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }

  .container-list {
    margin-bottom: 2rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  table th,
  table td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  .running {
    color: #4caf50;
  }

  .paused {
    color: #ff9800;
  }

  .stopped {
    color: #f44336;
  }

  .actions {
    margin-top: 2rem;
    display: flex;
    justify-content: flex-end;
  }

  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    background-color: #f5f5f5;
    color: #333;
    margin-left: 0.5rem;
  }

  .btn.primary {
    background-color: #2196f3;
    color: white;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .action-buttons {
    margin-top: 1rem;
  }
</style>
