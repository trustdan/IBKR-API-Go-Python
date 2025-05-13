<script>
  import { configStore } from '../store/config.js';
  import { onMount } from 'svelte';

  // Import API adapter
  import { getDataStats, triggerDataUpdate, clearDataCache } from '../api';

  let loading = false;
  let updateRunning = false;
  let clearingCache = false;

  let dataStats = {
    totalSymbols: 0,
    cachedBars: 0,
    cachedOptions: 0,
    lastUpdated: null,
    diskUsageMB: 0,
    dataSourceStatus: 'Unknown'
  };

  // Load data stats on mount
  onMount(async () => {
    await loadDataStats();
  });

  async function loadDataStats() {
    loading = true;
    try {
      dataStats = await getDataStats();
    } catch (error) {
      console.error("Failed to load data stats:", error);
    } finally {
      loading = false;
    }
  }

  async function handleTriggerUpdate() {
    updateRunning = true;
    try {
      await triggerDataUpdate();
      await loadDataStats();
    } catch (error) {
      console.error("Failed to trigger data update:", error);
      alert("Data update failed: " + error.message);
    } finally {
      updateRunning = false;
    }
  }

  async function handleClearCache() {
    if (!confirm("Are you sure you want to clear the data cache? This will remove all cached data and require a fresh download.")) {
      return;
    }

    clearingCache = true;
    try {
      await clearDataCache();
      await loadDataStats();
    } catch (error) {
      console.error("Failed to clear cache:", error);
      alert("Cache clearing failed: " + error.message);
    } finally {
      clearingCache = false;
    }
  }

  // Format date for display
  function formatDate(dateStr) {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  }
</script>

<div class="tab-container">
  <h2>Data Management</h2>
  <p class="description">Manage market data downloads, storage, and update schedules.</p>

  <div class="stats-panel">
    <h3>Data Statistics</h3>
    {#if loading}
      <div class="loading">Loading data stats...</div>
    {:else}
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">Total Symbols:</div>
          <div class="stat-value">{dataStats.totalSymbols}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Cached Price Bars:</div>
          <div class="stat-value">{dataStats.cachedBars.toLocaleString()}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Cached Options:</div>
          <div class="stat-value">{dataStats.cachedOptions.toLocaleString()}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Last Updated:</div>
          <div class="stat-value">{formatDate(dataStats.lastUpdated)}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Disk Usage:</div>
          <div class="stat-value">{dataStats.diskUsageMB.toFixed(2)} MB</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Data Source:</div>
          <div class="stat-value" class:connected={dataStats.dataSourceStatus === 'Connected'}>
            {dataStats.dataSourceStatus}
          </div>
        </div>
      </div>

      <div class="actions">
        <button
          class="primary-button"
          on:click={handleTriggerUpdate}
          disabled={updateRunning}
        >
          {updateRunning ? 'Updating...' : 'Update Data Now'}
        </button>

        <button
          class="secondary-button"
          on:click={handleClearCache}
          disabled={clearingCache}
        >
          {clearingCache ? 'Clearing...' : 'Clear Cache'}
        </button>
      </div>
    {/if}
  </div>

  <div class="config-panel">
    <h3>Data Configuration</h3>

    <div class="config-section">
      <h4>Data Sources</h4>

      <div class="form-group">
        <label for="primary-source">Primary Data Source</label>
        <select id="primary-source" bind:value={$configStore.data.primary_source}>
          <option value="ibkr">Interactive Brokers</option>
          <option value="alphavantage">Alpha Vantage</option>
          <option value="yahoo">Yahoo Finance</option>
          <option value="polygon">Polygon.io</option>
        </select>
      </div>

      <div class="form-group">
        <label for="fallback-source">Fallback Data Source</label>
        <select id="fallback-source" bind:value={$configStore.data.fallback_source}>
          <option value="none">None</option>
          <option value="ibkr">Interactive Brokers</option>
          <option value="alphavantage">Alpha Vantage</option>
          <option value="yahoo">Yahoo Finance</option>
          <option value="polygon">Polygon.io</option>
        </select>
      </div>

      <div class="form-group">
        <label for="api-key">API Key (if needed)</label>
        <input
          type="text"
          id="api-key"
          bind:value={$configStore.data.api_key}
          placeholder="Enter API key for selected data source"
        />
      </div>
    </div>

    <div class="config-section">
      <h4>Update Schedule</h4>

      <div class="form-group">
        <label for="auto-update">Auto-Update Data</label>
        <input
          type="checkbox"
          id="auto-update"
          bind:checked={$configStore.data.auto_update}
        />
      </div>

      <div class="form-group">
        <label for="update-time">Daily Update Time</label>
        <input
          type="time"
          id="update-time"
          bind:value={$configStore.data.update_time}
          disabled={!$configStore.data.auto_update}
        />
      </div>

      <div class="form-group">
        <label for="weekend-update">Update on Weekends</label>
        <input
          type="checkbox"
          id="weekend-update"
          bind:checked={$configStore.data.update_on_weekends}
          disabled={!$configStore.data.auto_update}
        />
      </div>
    </div>

    <div class="config-section">
      <h4>Data Storage</h4>

      <div class="form-group">
        <label for="storage-path">Storage Path</label>
        <input
          type="text"
          id="storage-path"
          bind:value={$configStore.data.storage_path}
          placeholder="/path/to/data"
        />
      </div>

      <div class="form-group">
        <label for="max-history">Max History (days)</label>
        <input
          type="range"
          id="max-history"
          min="30"
          max="3650"
          step="30"
          bind:value={$configStore.data.max_history_days}
        />
        <span class="value-display">
          {$configStore.data.max_history_days < 365
            ? $configStore.data.max_history_days + ' days'
            : ($configStore.data.max_history_days / 365).toFixed(1) + ' years'}
        </span>
      </div>

      <div class="form-group">
        <label for="compression">Compress Data</label>
        <input
          type="checkbox"
          id="compression"
          bind:checked={$configStore.data.compress_data}
        />
      </div>

      <div class="form-group">
        <label for="max-disk">Max Disk Usage (GB)</label>
        <input
          type="range"
          id="max-disk"
          min="1"
          max="50"
          step="1"
          bind:value={$configStore.data.max_disk_usage_gb}
        />
        <span class="value-display">{$configStore.data.max_disk_usage_gb} GB</span>
      </div>
    </div>
  </div>
</div>

<style>
  .tab-container {
    padding: 20px;
  }

  .description {
    margin-bottom: 20px;
    color: #666;
  }

  .stats-panel, .config-panel {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 20px;
  }

  h4 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
  }

  .loading {
    padding: 20px;
    text-align: center;
    color: #888;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .stat-item {
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
  }

  .stat-label {
    font-weight: 500;
    margin-bottom: 5px;
    color: #666;
  }

  .stat-value {
    font-size: 16px;
    font-weight: 600;
  }

  .stat-value.connected {
    color: #4caf50;
  }

  .actions {
    display: flex;
    gap: 10px;
    margin-top: 20px;
  }

  .primary-button, .secondary-button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .primary-button {
    background-color: #3273dc;
    color: white;
  }

  .secondary-button {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
  }

  .primary-button:disabled, .secondary-button:disabled {
    background-color: #999;
    color: #ddd;
    cursor: not-allowed;
  }

  .config-section {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
  }

  .config-section:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }

  .form-group {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
  }

  label {
    width: 180px;
    font-weight: 500;
  }

  input[type="range"] {
    flex: 1;
    margin-right: 10px;
  }

  input[type="text"], select, input[type="time"] {
    flex: 1;
    max-width: 300px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
  }

  .value-display {
    width: 80px;
    text-align: right;
  }
</style>
