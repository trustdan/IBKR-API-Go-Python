<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { statusStore, startStatusPolling, updateStatus } from '../stores/statusStore';

  let stopPolling: (() => void) | null = null;

  onMount(async () => {
    // Fetch initial status
    await updateStatus();

    // Start polling for status updates every 5 seconds
    stopPolling = startStatusPolling(5000);
  });

  onDestroy(() => {
    // Clean up the polling interval when component is destroyed
    if (stopPolling) {
      stopPolling();
    }
  });

  // Format the last updated time
  function formatTime(date: Date): string {
    return date.toLocaleTimeString();
  }

  // Determine status indicator class based on connection status
  function getStatusClass(connected: boolean): string {
    return connected ? 'status-indicator-connected' : 'status-indicator-disconnected';
  }
</script>

<div class="status-bar">
  <div class="status-item">
    <span class="status-label">IBKR:</span>
    <span class={`status-indicator ${getStatusClass($statusStore.ibkr.connected)}`}></span>
    <span class="status-text">{$statusStore.ibkr.connected ? 'Connected' : 'Disconnected'}</span>
    {#if $statusStore.ibkr.error}
      <span class="status-error">{$statusStore.ibkr.error}</span>
    {/if}
  </div>

  <div class="status-divider"></div>

  <div class="status-item">
    <span class="status-label">Services:</span>
    {#each $statusStore.services as service}
      <span class="service-status">
        <span class={`status-indicator ${getStatusClass(service.running)}`}></span>
        <span class="service-name">{service.name}</span>
      </span>
    {/each}
  </div>

  <div class="status-divider"></div>

  <div class="status-item">
    <span class="status-label">Positions:</span>
    <span class="status-value">{$statusStore.activePositions}</span>
  </div>

  <div class="status-divider"></div>

  <div class="status-item">
    <span class="status-label">Trading:</span>
    <span class={`status-indicator ${getStatusClass($statusStore.tradingActive)}`}></span>
    <span class="status-text">{$statusStore.tradingActive ? 'Active' : 'Inactive'}</span>
  </div>

  <div class="status-divider"></div>

  <div class="status-item">
    <span class="status-label">Trading Hours:</span>
    <span class={`status-indicator ${getStatusClass($statusStore.isTradingHours)}`}></span>
  </div>

  <div class="status-item status-item-right">
    <span class="status-label">Last Updated:</span>
    <span class="status-text">{formatTime($statusStore.lastUpdated)}</span>
  </div>
</div>

<style>
  .status-bar {
    display: flex;
    align-items: center;
    background-color: #f1f5f9;
    border-top: 1px solid #e2e8f0;
    padding: 0 1rem;
    height: 36px;
    font-size: 0.8rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    margin-right: 1rem;
  }

  .status-item-right {
    margin-left: auto;
    margin-right: 0;
  }

  .status-label {
    font-weight: 600;
    color: #64748b;
    margin-right: 0.5rem;
  }

  .status-text {
    color: #334155;
  }

  .status-value {
    color: #334155;
    font-weight: 500;
  }

  .status-error {
    color: #dc2626;
    margin-left: 0.5rem;
  }

  .status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.5rem;
  }

  .status-indicator-connected {
    background-color: #22c55e;
  }

  .status-indicator-disconnected {
    background-color: #ef4444;
  }

  .status-divider {
    width: 1px;
    height: 16px;
    background-color: #cbd5e1;
    margin: 0 0.5rem;
  }

  .service-status {
    display: flex;
    align-items: center;
    margin-right: 1rem;
  }

  .service-name {
    font-size: 0.75rem;
    color: #334155;
  }
</style>
