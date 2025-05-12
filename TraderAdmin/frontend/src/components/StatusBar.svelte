<script lang="ts">
  import { onMount } from 'svelte';
  import { status } from '../store/status';

  let statusTimer: number;

  onMount(() => {
    // Clear interval on component unmount
    return () => {
      clearInterval(statusTimer);
    };
  });
</script>

<div class="status-bar">
  <div class="ibkr-status">
    <div class="status-icon {$status.ibkrConnected ? 'connected' : 'disconnected'}"
         title={$status.ibkrConnected ? 'Connected to IBKR' : 'Disconnected from IBKR'}>
      IBKR
    </div>
  </div>

  <div class="containers">
    {#each $status.containers as container}
      <div class="container-status">
        <div class="status-dot {container.state.toLowerCase()}"
             title="{container.name}: {container.state}"></div>
        <span>{container.name}</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .status-bar {
    display: flex;
    align-items: center;
    padding: 5px 10px;
    background-color: #f5f5f5;
    border-bottom: 1px solid #ddd;
    font-size: 0.9rem;
  }

  .ibkr-status {
    margin-right: 15px;
  }

  .status-icon {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
  }

  .status-icon.connected {
    background-color: #4caf50;
    color: white;
  }

  .status-icon.disconnected {
    background-color: #f44336;
    color: white;
  }

  .containers {
    display: flex;
    gap: 10px;
  }

  .container-status {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .status-dot.running {
    background-color: #4caf50;
  }

  .status-dot.paused {
    background-color: #ff9800;
  }

  .status-dot.stopped {
    background-color: #f44336;
  }
</style>
