<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { metricsStore, updateMetrics, startMetricsPolling } from '../stores/metricsStore';
  import { Card, CardBody, CardHeader, Row, Col, Table, Badge, Progress } from '@sveltestrap/sveltestrap';

  let pollingCleanup: (() => void) | null = null;

  onMount(async () => {
    // Get initial metrics
    await updateMetrics();

    // Start polling for updates
    pollingCleanup = startMetricsPolling(10000); // Update every 10 seconds
  });

  onDestroy(() => {
    if (pollingCleanup) {
      pollingCleanup();
    }
  });

  // Format currency values
  function formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  }

  // Format percentages
  function formatPercent(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100);
  }

  // Format date/time
  function formatDateTime(date: Date | string): string {
    if (!date) return 'N/A';
    const dateObj = date instanceof Date ? date : new Date(date);
    return dateObj.toLocaleString();
  }

  // Determine badge color for P&L values
  function getPnlBadgeColor(value: number) {
    if (value > 0) return 'success';
    if (value < 0) return 'danger';
    return 'secondary';
  }

  // Determine system health status color
  function getHealthColor(metric: string, threshold: number) {
    if (metric === 'latency') {
      if ($metricsStore.system.avgOrderLatencyMs > threshold) return 'danger';
      if ($metricsStore.system.avgOrderLatencyMs > threshold * 0.7) return 'warning';
      return 'success';
    }
    if (metric === 'errors') {
      if ($metricsStore.system.apiErrorCount > threshold) return 'danger';
      if ($metricsStore.system.apiErrorCount > threshold * 0.7) return 'warning';
      return 'success';
    }
    return 'secondary';
  }

  // Calculate time elapsed since last data sync
  function getLastSyncTime() {
    try {
      const lastSync = new Date($metricsStore.system.lastDataSync);
      const now = new Date();
      const diffMs = now.getTime() - lastSync.getTime();
      const diffSeconds = Math.floor(diffMs / 1000);

      if (diffSeconds < 60) return `${diffSeconds} seconds ago`;
      if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)} minutes ago`;
      return `${Math.floor(diffSeconds / 3600)} hours ago`;
    } catch (e) {
      return 'Unknown';
    }
  }

  // Thresholds for visualization
  const latencyThreshold = 500; // ms
  const errorThreshold = 10;
</script>

<div class="monitoring-tab">
  <header>
    <h1>Real-Time Monitoring</h1>
    <p>View the current status and performance metrics of your trading system.</p>
  </header>

  {#if !$metricsStore}
    <div class="loading">Loading metrics...</div>
  {:else}
    <div class="metrics-grid">
      <!-- Portfolio Metrics -->
      <div class="metrics-card">
        <h2>Portfolio</h2>
        <div class="metrics-content">
          <div class="metric-row">
            <span class="metric-label">Equity:</span>
            <span class="metric-value">{formatCurrency($metricsStore.portfolio.equity)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Realized P&L Today:</span>
            <span class="metric-value" class:positive={$metricsStore.portfolio.realizedPnlToday > 0} class:negative={$metricsStore.portfolio.realizedPnlToday < 0}>
              {formatCurrency($metricsStore.portfolio.realizedPnlToday)}
            </span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Unrealized P&L:</span>
            <span class="metric-value" class:positive={$metricsStore.portfolio.unrealizedPnl > 0} class:negative={$metricsStore.portfolio.unrealizedPnl < 0}>
              {formatCurrency($metricsStore.portfolio.unrealizedPnl)}
            </span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Open Positions:</span>
            <span class="metric-value">{$metricsStore.portfolio.openPositionsCount}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Buying Power:</span>
            <span class="metric-value">{formatCurrency($metricsStore.portfolio.buyingPower)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Last Updated:</span>
            <span class="metric-value">{formatDateTime($metricsStore.portfolio.timestamp)}</span>
          </div>
        </div>
      </div>

      <!-- Trading Stats -->
      <div class="metrics-card">
        <h2>Today's Trading</h2>
        <div class="metrics-content">
          <div class="metric-row">
            <span class="metric-label">Trades Executed:</span>
            <span class="metric-value">{$metricsStore.trades.executedCount}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Win Rate:</span>
            <span class="metric-value">{formatPercent($metricsStore.trades.winRate)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Wins:</span>
            <span class="metric-value positive">{$metricsStore.trades.winCount}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Losses:</span>
            <span class="metric-value negative">{$metricsStore.trades.lossCount}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Avg Win:</span>
            <span class="metric-value positive">{formatCurrency($metricsStore.trades.avgWinAmount)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Avg Loss:</span>
            <span class="metric-value negative">{formatCurrency($metricsStore.trades.avgLossAmount)}</span>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="metrics-card">
        <h2>System Health</h2>
        <div class="metrics-content">
          <div class="metric-row">
            <span class="metric-label">Avg Order Latency:</span>
            <span class="metric-value">{$metricsStore.system.avgOrderLatencyMs.toFixed(2)} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">API Errors:</span>
            <span class="metric-value" class:warning={$metricsStore.system.apiErrorCount > 0}>
              {$metricsStore.system.apiErrorCount}
            </span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Last Data Sync:</span>
            <span class="metric-value">{formatDateTime($metricsStore.system.lastDataSync)}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Open Positions Table -->
    <div class="positions-section">
      <h2>Open Positions</h2>

      {#if $metricsStore.openPositions.length === 0}
        <p class="no-positions">No open positions.</p>
      {:else}
        <div class="table-container">
          <table class="positions-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Strategy</th>
                <th>Quantity</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>Unrealized P&L</th>
                <th>Open Time</th>
              </tr>
            </thead>
            <tbody>
              {#each $metricsStore.openPositions as position}
                <tr>
                  <td>{position.symbol}</td>
                  <td>{position.strategy}</td>
                  <td>{position.quantity}</td>
                  <td>{formatCurrency(position.entryPrice)}</td>
                  <td>{formatCurrency(position.currentPrice)}</td>
                  <td class:positive={position.unrealizedPl > 0} class:negative={position.unrealizedPl < 0}>
                    {formatCurrency(position.unrealizedPl)}
                  </td>
                  <td>{formatDateTime(position.openTime)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .monitoring-tab {
    padding: 1rem;
    max-width: 1200px;
  }

  header {
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #1e293b;
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: #1e293b;
  }

  p {
    color: #64748b;
    margin: 0 0 1rem 0;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    font-size: 1.1rem;
    color: #64748b;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .metrics-card {
    background-color: #ffffff;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 1.25rem;
  }

  .metrics-content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .metric-label {
    font-weight: 500;
    color: #64748b;
  }

  .metric-value {
    font-weight: 600;
    color: #1e293b;
  }

  .positive {
    color: #10b981;
  }

  .negative {
    color: #ef4444;
  }

  .warning {
    color: #f97316;
  }

  .positions-section {
    margin-top: 2rem;
  }

  .no-positions {
    padding: 2rem;
    text-align: center;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    color: #64748b;
  }

  .table-container {
    overflow-x: auto;
  }

  .positions-table {
    width: 100%;
    border-collapse: collapse;
  }

  .positions-table th,
  .positions-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
  }

  .positions-table th {
    background-color: #f8fafc;
    font-weight: 600;
    color: #64748b;
  }

  .positions-table tr:hover {
    background-color: #f1f5f9;
  }
</style>
