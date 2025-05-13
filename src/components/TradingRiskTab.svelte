<script>
  import { configStore } from '../store/config.js';
  import { onMount } from 'svelte';

  // Import the API adapter
  import { runQuickBacktest } from '../api';

  let loading = false;
  let backtestResults = null;

  async function runBacktest() {
    loading = true;
    try {
      backtestResults = await runQuickBacktest();
      showBacktestModal = true;
    } catch (error) {
      console.error("Backtest failed:", error);
      alert("Backtest failed: " + error.message);
    } finally {
      loading = false;
    }
  }

  let showBacktestModal = false;

  function closeModal() {
    showBacktestModal = false;
  }
</script>

<div class="tab-container">
  <h2>Trading & Risk Settings</h2>

  <div class="form-section">
    <div class="form-group">
      <label for="trading-mode">Trading Mode</label>
      <select id="trading-mode" bind:value={$configStore.trading.mode}>
        <option value="PAPER">Paper Trading</option>
        <option value="LIVE">Live Trading</option>
        <option value="BACKTEST">Backtest Only</option>
      </select>
    </div>

    <div class="form-group">
      <label for="max-positions">Maximum Positions</label>
      <input
        type="range"
        id="max-positions"
        min="1"
        max="20"
        bind:value={$configStore.trading.max_positions}
      />
      <span class="value-display">{$configStore.trading.max_positions}</span>
    </div>

    <div class="form-group">
      <label for="risk-pct">Risk Per Trade (%)</label>
      <input
        type="range"
        id="risk-pct"
        min="0.1"
        max="5.0"
        step="0.1"
        bind:value={$configStore.trading.risk_per_trade_pct}
      />
      <span class="value-display">{$configStore.trading.risk_per_trade_pct}%</span>
    </div>

    <div class="form-group">
      <label for="max-drawdown">Max Drawdown Limit (%)</label>
      <input
        type="range"
        id="max-drawdown"
        min="1"
        max="20"
        step="0.5"
        bind:value={$configStore.trading.max_drawdown_pct}
      />
      <span class="value-display">{$configStore.trading.max_drawdown_pct}%</span>
    </div>
  </div>

  <div class="actions">
    <button on:click={runBacktest} disabled={loading} class="primary-button">
      {loading ? 'Running...' : 'Run Quick Backtest'}
    </button>
  </div>

  {#if showBacktestModal && backtestResults}
    <div class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Backtest Results</h3>
          <button on:click={closeModal} class="close-button">×</button>
        </div>
        <div class="modal-body">
          <div class="results-summary">
            <div class="metric">
              <span class="label">Total Return:</span>
              <span class="value">{backtestResults.totalReturn.toFixed(2)}%</span>
            </div>
            <div class="metric">
              <span class="label">Win Rate:</span>
              <span class="value">{backtestResults.winRate.toFixed(2)}%</span>
            </div>
            <div class="metric">
              <span class="label">Sharpe Ratio:</span>
              <span class="value">{backtestResults.sharpeRatio.toFixed(2)}</span>
            </div>
            <div class="metric">
              <span class="label">Max Drawdown:</span>
              <span class="value">{backtestResults.maxDrawdown.toFixed(2)}%</span>
            </div>
          </div>

          <div class="chart-container">
            <!-- Chart would go here - placeholder -->
            <div class="chart-placeholder">Equity Curve Chart</div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .tab-container {
    padding: 20px;
  }

  .form-section {
    margin-bottom: 20px;
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

  .value-display {
    width: 60px;
    text-align: right;
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

  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background-color: white;
    border-radius: 5px;
    width: 80%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
  }

  .modal-body {
    padding: 20px;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
  }

  .results-summary {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .metric {
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
  }

  .label {
    font-weight: 500;
    display: block;
    margin-bottom: 5px;
  }

  .value {
    font-size: 18px;
    font-weight: 600;
  }

  .chart-placeholder {
    height: 300px;
    background-color: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px dashed #ccc;
    color: #888;
  }
</style>
