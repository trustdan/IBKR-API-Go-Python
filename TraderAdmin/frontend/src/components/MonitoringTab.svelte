<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { GetMetrics } from '../../wailsjs/go/main/App';
  import { toast } from '@zerodevx/svelte-toast';
  import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    BarChart, Bar
  } from 'recharts';

  // Metrics data type
  type Metrics = {
    timestamp: number;
    equity: number;
    dailyPnL: number;
    tradesExecuted: number;
    winCount: number;
    lossCount: number;
    maxLatencyMs: number;
    avgLatencyMs: number;
    errorCount: number;
    errorsByType: string[];
  };

  type Position = {
    symbol: string;
    quantity: number;
    entryPrice: number;
    currentPrice: number;
    pnl: number;
    strategy: string;
  };

  type MetricsData = {
    metrics: Metrics;
    positions: Position[];
    timePoints: number[];
    equityPoints: number[];
  };

  let loading = true;
  let metricsData: MetricsData | null = null;
  let equityChartData: any[] = [];
  let latencyChartData: any[] = [];
  let errorRate = 0;
  let errorsByType: { name: string, count: number }[] = [];
  let refreshInterval: number | null = null;
  let refreshRate = 5000; // 5 seconds default

  // Format numbers for display
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  // Format timestamp to time
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Tooltip formatter for currency values
  const currencyFormatter = (value: any) => {
    if (typeof value === 'number') {
      return formatCurrency(value);
    }
    return value;
  };

  // Process metrics data for charts
  const processMetrics = (data: MetricsData) => {
    // Process equity chart data
    equityChartData = data.timePoints.map((time, index) => ({
      time: formatTime(time),
      equity: data.equityPoints[index]
    }));

    // Create latency chart data
    latencyChartData = [
      { name: 'Average', value: data.metrics.avgLatencyMs },
      { name: 'Maximum', value: data.metrics.maxLatencyMs }
    ];

    // Process error data
    errorRate = data.metrics.errorCount;
    errorsByType = data.metrics.errorsByType.reduce((acc, error) => {
      const existing = acc.find(e => e.name === error);
      if (existing) {
        existing.count += 1;
      } else {
        acc.push({ name: error, count: 1 });
      }
      return acc;
    }, [] as { name: string, count: number }[]);
  };

  // Fetch metrics
  const fetchMetrics = async () => {
    try {
      const data = await GetMetrics();
      metricsData = data;
      processMetrics(data);
      loading = false;
    } catch (error) {
      console.error('Error fetching metrics:', error);
      toast.push('Error fetching metrics: ' + error.message, {
        theme: { '--toastBackground': '#F56565', '--toastBarBackground': '#C53030' }
      });
    }
  };

  // Start metrics polling
  const startPolling = () => {
    fetchMetrics();
    refreshInterval = window.setInterval(fetchMetrics, refreshRate);
  };

  // Stop metrics polling
  const stopPolling = () => {
    if (refreshInterval !== null) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  };

  // Change refresh rate
  const changeRefreshRate = (newRate: number) => {
    refreshRate = newRate;
    stopPolling();
    startPolling();
  };

  // Component lifecycle
  onMount(() => {
    startPolling();
  });

  onDestroy(() => {
    stopPolling();
  });
</script>

<div class="monitoring-tab">
  <h2>Trading Monitoring & Metrics</h2>

  {#if loading}
    <div class="loading">Loading metrics data...</div>
  {:else}
    <div class="controls">
      <div class="refresh-controls">
        <label for="refreshRate">Refresh rate:</label>
        <select id="refreshRate" bind:value={refreshRate} on:change={() => changeRefreshRate(refreshRate)}>
          <option value={2000}>2 seconds</option>
          <option value={5000}>5 seconds</option>
          <option value={10000}>10 seconds</option>
          <option value={30000}>30 seconds</option>
        </select>
        <button on:click={fetchMetrics} class="refresh-button">Refresh Now</button>
      </div>
      <div class="last-updated">
        Last updated: {metricsData ? formatTime(metricsData.metrics.timestamp) : 'N/A'}
      </div>
    </div>

    <div class="dashboard">
      <!-- Key metrics panel -->
      <div class="metrics-panel">
        <div class="metric-card">
          <h3>Equity</h3>
          <div class="metric-value">{formatCurrency(metricsData?.metrics.equity || 0)}</div>
        </div>

        <div class="metric-card">
          <h3>Daily P&L</h3>
          <div class="metric-value" class:positive={metricsData?.metrics.dailyPnL > 0} class:negative={metricsData?.metrics.dailyPnL < 0}>
            {formatCurrency(metricsData?.metrics.dailyPnL || 0)}
          </div>
        </div>

        <div class="metric-card">
          <h3>Trades</h3>
          <div class="metric-value">{metricsData?.metrics.tradesExecuted || 0}</div>
          <div class="metric-detail">
            Win: {metricsData?.metrics.winCount || 0} / Loss: {metricsData?.metrics.lossCount || 0}
          </div>
        </div>

        <div class="metric-card">
          <h3>Execution Latency</h3>
          <div class="metric-value">{metricsData?.metrics.avgLatencyMs || 0}ms</div>
          <div class="metric-detail">
            Max: {metricsData?.metrics.maxLatencyMs || 0}ms
          </div>
        </div>

        <div class="metric-card">
          <h3>Errors</h3>
          <div class="metric-value">{metricsData?.metrics.errorCount || 0}</div>
          {#if errorsByType.length > 0}
            <div class="metric-detail">
              {#each errorsByType as error}
                <div>{error.name}: {error.count}</div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- Charts section -->
      <div class="charts-panel">
        <!-- Equity curve chart -->
        <div class="chart-container">
          <h3>Equity Curve</h3>
          <div class="chart">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={equityChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip formatter={currencyFormatter} />
                <Legend />
                <Line type="monotone" dataKey="equity" stroke="#3182CE" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <!-- Execution latency chart -->
        <div class="chart-container">
          <h3>Execution Latency (ms)</h3>
          <div class="chart">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={latencyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#4C51BF" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <!-- Open positions table -->
      <div class="positions-panel">
        <h3>Open Positions</h3>
        {#if metricsData?.positions && metricsData.positions.length > 0}
          <table class="positions-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Quantity</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>P&L</th>
                <th>Strategy</th>
              </tr>
            </thead>
            <tbody>
              {#each metricsData.positions as position}
                <tr>
                  <td>{position.symbol}</td>
                  <td>{position.quantity}</td>
                  <td>{formatCurrency(position.entryPrice)}</td>
                  <td>{formatCurrency(position.currentPrice)}</td>
                  <td class:positive={position.pnl > 0} class:negative={position.pnl < 0}>
                    {formatCurrency(position.pnl)}
                  </td>
                  <td>{position.strategy}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <div class="no-positions">No open positions</div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .monitoring-tab {
    padding: 1rem;
  }

  h2 {
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
    color: #4a5568;
  }

  .loading {
    padding: 2rem;
    text-align: center;
    color: #718096;
  }

  .controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .refresh-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .refresh-button {
    background-color: #4299e1;
    color: white;
    padding: 0.25rem 0.5rem;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
  }

  .refresh-button:hover {
    background-color: #3182ce;
  }

  .last-updated {
    font-size: 0.875rem;
    color: #718096;
  }

  .dashboard {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .metrics-panel {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .metric-card {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0.5rem 0;
  }

  .metric-detail {
    font-size: 0.875rem;
    color: #718096;
  }

  .positive {
    color: #48bb78;
  }

  .negative {
    color: #f56565;
  }

  .charts-panel {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .chart-container {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .chart {
    margin-top: 0.5rem;
  }

  .positions-panel {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .positions-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
  }

  .positions-table th, .positions-table td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
  }

  .positions-table th {
    font-weight: 600;
    background-color: #f7fafc;
  }

  .no-positions {
    padding: 1rem;
    text-align: center;
    color: #718096;
  }

  /* Responsive adjustments */
  @media (min-width: 1024px) {
    .dashboard {
      grid-template-columns: 1fr;
    }

    .charts-panel {
      grid-template-columns: 1fr 1fr;
    }
  }
</style>
