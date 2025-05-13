<script>
  import { configStore } from '../store/config.js';
  import { onMount } from 'svelte';

  // Import API adapter
  import { getScannerStatus, runScannerNow } from '../api';

  let loadingStatus = false;
  let scannerStatus = {
    running: false,
    lastRun: null,
    scannedSymbols: 0,
    foundOpportunities: 0,
    nextRun: null
  };

  let runningManualScan = false;

  // Check scanner status on mount and periodically
  onMount(() => {
    loadScannerStatus();
    const interval = setInterval(loadScannerStatus, 10000); // Check every 10 seconds

    return () => {
      clearInterval(interval);
    };
  });

  async function loadScannerStatus() {
    loadingStatus = true;
    try {
      scannerStatus = await getScannerStatus();
    } catch (error) {
      console.error("Failed to get scanner status:", error);
    } finally {
      loadingStatus = false;
    }
  }

  async function handleRunScannerNow() {
    runningManualScan = true;
    try {
      await runScannerNow();
      await loadScannerStatus();
    } catch (error) {
      console.error("Failed to run scanner:", error);
      alert("Scanner failed to run: " + error.message);
    } finally {
      runningManualScan = false;
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
  <h2>Scanner Configuration</h2>
  <p class="description">Configure how the system scans for trading opportunities.</p>

  <div class="status-panel">
    <h3>Scanner Status</h3>
    <div class="status-grid">
      <div class="status-item">
        <div class="status-label">Status:</div>
        <div class="status-value">
          <span class="status-indicator" class:active={scannerStatus.running}></span>
          {scannerStatus.running ? 'Running' : 'Idle'}
        </div>
      </div>
      <div class="status-item">
        <div class="status-label">Last Run:</div>
        <div class="status-value">{formatDate(scannerStatus.lastRun)}</div>
      </div>
      <div class="status-item">
        <div class="status-label">Scanned Symbols:</div>
        <div class="status-value">{scannerStatus.scannedSymbols}</div>
      </div>
      <div class="status-item">
        <div class="status-label">Found Opportunities:</div>
        <div class="status-value">{scannerStatus.foundOpportunities}</div>
      </div>
      <div class="status-item">
        <div class="status-label">Next Scheduled Run:</div>
        <div class="status-value">{formatDate(scannerStatus.nextRun)}</div>
      </div>
    </div>

    <button
      class="primary-button"
      on:click={handleRunScannerNow}
      disabled={runningManualScan || scannerStatus.running}
    >
      {runningManualScan ? 'Running Scan...' : 'Run Scanner Now'}
    </button>
  </div>

  <div class="config-panel">
    <h3>Scanner Configuration</h3>

    <div class="config-section">
      <h4>Schedule Settings</h4>

      <div class="form-group">
        <label for="scan-interval">Scan Interval (minutes)</label>
        <input
          type="range"
          id="scan-interval"
          min="5"
          max="120"
          step="5"
          bind:value={$configStore.scanner.interval_minutes}
        />
        <span class="value-display">{$configStore.scanner.interval_minutes}</span>
      </div>

      <div class="form-group">
        <label for="market-hours-only">Market Hours Only</label>
        <input
          type="checkbox"
          id="market-hours-only"
          bind:checked={$configStore.scanner.market_hours_only}
        />
      </div>
    </div>

    <div class="config-section">
      <h4>Scan Filters</h4>

      <div class="form-group">
        <label for="max-symbols">Max Symbols per Scan</label>
        <input
          type="number"
          id="max-symbols"
          min="10"
          max="1000"
          bind:value={$configStore.scanner.max_symbols_per_scan}
        />
      </div>

      <div class="form-group">
        <label for="min-price">Minimum Price ($)</label>
        <input
          type="range"
          id="min-price"
          min="1"
          max="50"
          step="1"
          bind:value={$configStore.scanner.min_price}
        />
        <span class="value-display">${$configStore.scanner.min_price}</span>
      </div>

      <div class="form-group">
        <label for="max-price">Maximum Price ($)</label>
        <input
          type="range"
          id="max-price"
          min="50"
          max="1000"
          step="10"
          bind:value={$configStore.scanner.max_price}
        />
        <span class="value-display">${$configStore.scanner.max_price}</span>
      </div>

      <div class="form-group">
        <label for="price-change">Min Daily Price Change (%)</label>
        <input
          type="range"
          id="price-change"
          min="0"
          max="10"
          step="0.1"
          bind:value={$configStore.scanner.min_price_change_pct}
        />
        <span class="value-display">{$configStore.scanner.min_price_change_pct}%</span>
      </div>

      <div class="form-group">
        <label for="volume-increase">Min Volume Increase (%)</label>
        <input
          type="range"
          id="volume-increase"
          min="0"
          max="300"
          step="10"
          bind:value={$configStore.scanner.min_volume_increase_pct}
        />
        <span class="value-display">{$configStore.scanner.min_volume_increase_pct}%</span>
      </div>
    </div>

    <div class="config-section">
      <h4>Advanced Settings</h4>

      <div class="form-group">
        <label for="throttle-requests">Throttle API Requests</label>
        <input
          type="checkbox"
          id="throttle-requests"
          bind:checked={$configStore.scanner.throttle_requests}
        />
      </div>

      <div class="form-group">
        <label for="requests-per-second">Requests Per Second</label>
        <input
          type="range"
          id="requests-per-second"
          min="1"
          max="50"
          step="1"
          bind:value={$configStore.scanner.requests_per_second}
          disabled={!$configStore.scanner.throttle_requests}
        />
        <span class="value-display">{$configStore.scanner.requests_per_second}</span>
      </div>

      <div class="form-group">
        <label for="cache-duration">Data Cache Duration (min)</label>
        <input
          type="range"
          id="cache-duration"
          min="5"
          max="240"
          step="5"
          bind:value={$configStore.scanner.cache_duration_minutes}
        />
        <span class="value-display">{$configStore.scanner.cache_duration_minutes}</span>
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

  .status-panel, .config-panel {
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

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .status-item {
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
  }

  .status-label {
    font-weight: 500;
    margin-bottom: 5px;
    color: #666;
  }

  .status-value {
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
  }

  .status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #ccc;
    margin-right: 8px;
  }

  .status-indicator.active {
    background-color: #4caf50;
  }

  .primary-button {
    padding: 8px 16px;
    background-color: #3273dc;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .primary-button:disabled {
    background-color: #999;
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

  input[type="number"] {
    width: 80px;
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
  }

  .value-display {
    width: 60px;
    text-align: right;
  }
</style>
