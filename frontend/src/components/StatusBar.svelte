<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { formatDistanceToNow } from 'date-fns';

  // Status types
  type ContainerState = 'running' | 'paused' | 'stopped' | 'error';

  // Container interface
  interface Container {
    name: string;
    state: ContainerState;
    error?: string;
  }

  export let ibkrConnected: boolean = false;
  export let ibkrError: string | null = null;
  export let containers: Container[] = [];
  export let lastUpdated: Date | null = null;
  export let updating: boolean = false;

  $: systemHealth = getSystemHealth();

  const dispatch = createEventDispatcher();

  function getSystemHealth(): 'healthy' | 'degraded' | 'error' {
    if (!ibkrConnected) {
      return 'error';
    }

    if (containers.some(c => c.state === 'error')) {
      return 'error';
    }

    if (containers.some(c => c.state === 'stopped' || c.state === 'paused')) {
      return 'degraded';
    }

    return 'healthy';
  }

  function refreshStatus() {
    dispatch('refresh');
  }

  $: lastUpdatedText = lastUpdated
    ? `Last updated ${formatDistanceToNow(lastUpdated, { addSuffix: true })}`
    : 'Updating...';

  // Helper for container CSS classes
  function getContainerClass(state: ContainerState): string {
    switch (state) {
      case 'running': return 'status-healthy';
      case 'paused': return 'status-degraded';
      case 'stopped':
      case 'error':
      default: return 'status-error';
    }
  }
</script>

<div class="status-bar">
  <div class={`system-health status-${systemHealth}`}>
    <span class="status-dot"></span>
    <span class="status-label">System: {systemHealth}</span>

    <button
      class="refresh-button"
      on:click={refreshStatus}
      disabled={updating}
      aria-label="Refresh status"
    >
      <span class={`refresh-icon ${updating ? 'spinning' : ''}`}>🔄</span>
    </button>
  </div>

  <div class="connection-status">
    <div class={`status-item ${ibkrConnected ? 'status-healthy' : 'status-error'}`}>
      <span class="status-dot"></span>
      <span class="status-label">IBKR</span>
      {#if !ibkrConnected && ibkrError}
        <div class="status-tooltip">{ibkrError}</div>
      {/if}
    </div>

    {#each containers as container}
      <div class={`status-item ${getContainerClass(container.state)}`}>
        <span class="status-dot"></span>
        <span class="status-label">{container.name}</span>
        {#if container.error}
          <div class="status-tooltip">{container.error}</div>
        {/if}
      </div>
    {/each}
  </div>

  <div class="status-timestamp">
    {lastUpdatedText}
  </div>
</div>

<style>
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f9f9f9;
    border-bottom: 1px solid #e0e0e0;
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
    height: 36px;
    width: 100%;
  }

  .system-health {
    display: flex;
    align-items: center;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    margin-right: 1rem;
  }

  .status-healthy {
    color: #2e7d32;
  }

  .status-degraded {
    color: #ff8f00;
  }

  .status-error {
    color: #c62828;
  }

  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
  }

  .status-healthy .status-dot {
    background-color: #2e7d32;
  }

  .status-degraded .status-dot {
    background-color: #ff8f00;
  }

  .status-error .status-dot {
    background-color: #c62828;
  }

  .connection-status {
    display: flex;
    flex-grow: 1;
    gap: 1rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    position: relative;
  }

  .status-item:hover .status-tooltip {
    display: block;
  }

  .status-tooltip {
    display: none;
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background-color: #333;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.7rem;
    white-space: nowrap;
    margin-bottom: 5px;
    z-index: 1;
  }

  .status-tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border-width: 4px;
    border-style: solid;
    border-color: #333 transparent transparent;
  }

  .status-timestamp {
    color: #666;
    white-space: nowrap;
  }

  .refresh-button {
    background: none;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.25rem;
    margin-left: 0.5rem;
    border-radius: 50%;
    transition: background-color 0.2s;
  }

  .refresh-button:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }

  .refresh-button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .refresh-icon {
    font-size: 0.875rem;
    display: inline-block;
  }

  .spinning {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  /* Media query for small screens */
  @media (max-width: 600px) {
    .status-bar {
      flex-direction: column;
      height: auto;
      padding: 0.5rem;
      gap: 0.5rem;
    }

    .system-health,
    .connection-status,
    .status-timestamp {
      width: 100%;
    }

    .connection-status {
      flex-wrap: wrap;
      gap: 0.5rem;
    }
  }
</style>
