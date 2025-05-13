<script lang="ts">
  import { onMount } from 'svelte';
  import { statusStore } from '../stores/statusStore';
  import { activeTab, setActiveTab } from '../stores/activeTab';

  // Simple placeholder data for the dashboard
  const placeholderStats = {
    activeStrategies: 3,
    pendingTrades: 2,
    avgWinRate: 67.5,
    positionCount: 5,
    lastTrade: new Date(Date.now() - 35 * 60 * 1000) // 35 minutes ago
  };

  // Format date for display
  function formatDate(date: Date): string {
    return date.toLocaleString();
  }

  // Format time ago
  function timeAgo(date: Date): string {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";

    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";

    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";

    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";

    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes ago";

    return Math.floor(seconds) + " seconds ago";
  }
</script>

<div class="overview-tab">
  <header>
    <h1>Dashboard</h1>
    <p>Overview of your trading system status and performance</p>
  </header>

  <div class="dashboard-grid">
    <!-- System Status Card -->
    <div class="card">
      <div class="card-header">
        <h2>System Status</h2>
      </div>
      <div class="card-content">
        <div class="status-items">
          <div class="status-item">
            <span class="status-label">IBKR Connection:</span>
            <span class={`status-value ${$statusStore.ibkr.connected ? 'positive' : 'negative'}`}>
              {$statusStore.ibkr.connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {#each $statusStore.services as service}
            <div class="status-item">
              <span class="status-label">{service.name}:</span>
              <span class={`status-value ${service.running ? 'positive' : 'negative'}`}>
                {service.running ? 'Running' : 'Stopped'}
              </span>
            </div>
          {/each}

          <div class="status-item">
            <span class="status-label">Trading Hours:</span>
            <span class={`status-value ${$statusStore.isTradingHours ? 'positive' : 'neutral'}`}>
              {$statusStore.isTradingHours ? 'Open' : 'Closed'}
            </span>
          </div>

          <div class="status-item">
            <span class="status-label">Trading Status:</span>
            <span class={`status-value ${$statusStore.tradingActive ? 'positive' : 'neutral'}`}>
              {$statusStore.tradingActive ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>

        <div class="card-actions">
          <button class="btn btn-secondary" on:click={() => setActiveTab('connection')}>
            Manage Connection
          </button>
        </div>
      </div>
    </div>

    <!-- Trading Stats Card -->
    <div class="card">
      <div class="card-header">
        <h2>Trading Stats</h2>
      </div>
      <div class="card-content">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{placeholderStats.activeStrategies}</div>
            <div class="stat-label">Active Strategies</div>
          </div>

          <div class="stat-item">
            <div class="stat-value">{placeholderStats.positionCount}</div>
            <div class="stat-label">Open Positions</div>
          </div>

          <div class="stat-item">
            <div class="stat-value">{placeholderStats.pendingTrades}</div>
            <div class="stat-label">Pending Trades</div>
          </div>

          <div class="stat-item">
            <div class="stat-value">{placeholderStats.avgWinRate}%</div>
            <div class="stat-label">Win Rate (30d)</div>
          </div>
        </div>

        <div class="card-actions">
          <button class="btn btn-secondary" on:click={() => setActiveTab('monitoring')}>
            View Details
          </button>
        </div>
      </div>
    </div>

    <!-- Recent Activity Card -->
    <div class="card">
      <div class="card-header">
        <h2>Recent Activity</h2>
      </div>
      <div class="card-content">
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-icon trade">💰</div>
            <div class="activity-content">
              <div class="activity-title">Trade Executed</div>
              <div class="activity-description">SPY Put Spread @ $395/$390</div>
              <div class="activity-time">{timeAgo(placeholderStats.lastTrade)}</div>
            </div>
          </div>

          <div class="activity-item">
            <div class="activity-icon alert">⚠️</div>
            <div class="activity-content">
              <div class="activity-title">Margin Warning</div>
              <div class="activity-description">Account margin requirement increased</div>
              <div class="activity-time">{timeAgo(new Date(Date.now() - 120 * 60 * 1000))}</div>
            </div>
          </div>

          <div class="activity-item">
            <div class="activity-icon system">🔄</div>
            <div class="activity-content">
              <div class="activity-title">System Update</div>
              <div class="activity-description">Configuration changed</div>
              <div class="activity-time">{timeAgo(new Date(Date.now() - 240 * 60 * 1000))}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions Card -->
    <div class="card">
      <div class="card-header">
        <h2>Quick Actions</h2>
      </div>
      <div class="card-content">
        <div class="action-buttons">
          <button class="action-button" on:click={() => setActiveTab('trading-risk')}>
            <span class="action-icon">⚖️</span>
            <span class="action-text">Trading & Risk</span>
          </button>

          <button class="action-button" on:click={() => setActiveTab('strategies')}>
            <span class="action-icon">📈</span>
            <span class="action-text">Strategies</span>
          </button>

          <button class="action-button" on:click={() => setActiveTab('options')}>
            <span class="action-icon">🔄</span>
            <span class="action-text">Options</span>
          </button>

          <button class="action-button" on:click={() => setActiveTab('settings')}>
            <span class="action-icon">⚙️</span>
            <span class="action-text">Settings</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .overview-tab {
    padding: 1rem;
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
    margin: 0;
    color: #1e293b;
  }

  p {
    color: #64748b;
    margin: 0;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .card {
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    overflow: hidden;
  }

  .card-header {
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
    background-color: #f8fafc;
  }

  .card-content {
    padding: 1rem;
  }

  .status-items {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .status-label {
    font-weight: 500;
    color: #64748b;
  }

  .status-value {
    font-weight: 600;
  }

  .status-value.positive {
    color: #22c55e;
  }

  .status-value.negative {
    color: #ef4444;
  }

  .status-value.neutral {
    color: #f59e0b;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-item {
    text-align: center;
    padding: 0.75rem;
    background-color: #f8fafc;
    border-radius: 0.375rem;
  }

  .stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .stat-label {
    font-size: 0.875rem;
    color: #64748b;
  }

  .card-actions {
    display: flex;
    justify-content: flex-end;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;
  }

  .btn-secondary {
    background-color: white;
    color: #1e293b;
    border: 1px solid #cbd5e1;
  }

  .btn-secondary:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
  }

  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .activity-item {
    display: flex;
    gap: 0.75rem;
  }

  .activity-icon {
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background-color: #f8fafc;
    flex-shrink: 0;
  }

  .activity-content {
    flex: 1;
  }

  .activity-title {
    font-weight: 600;
    color: #1e293b;
  }

  .activity-description {
    font-size: 0.875rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  .activity-time {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 0.25rem;
  }

  .action-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .action-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    transition: background-color 0.2s;
    cursor: pointer;
  }

  .action-button:hover {
    background-color: #f1f5f9;
  }

  .action-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .action-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1e293b;
  }
</style>
