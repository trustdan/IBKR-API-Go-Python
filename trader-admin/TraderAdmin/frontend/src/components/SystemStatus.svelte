<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { CheckRequiredServices } from '../../wailsjs/go/main/App.js';

  // Service status data
  let services = [];
  let loading = true;
  let refreshInterval;

  onMount(async () => {
    await refreshServices();
    // Setup refresh interval (every 10 seconds)
    refreshInterval = setInterval(refreshServices, 10000);
  });

  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });

  async function refreshServices() {
    try {
      loading = true;
      services = await CheckRequiredServices();
    } catch (err) {
      console.error('Error checking services:', err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="system-status">
  <h3>System Status</h3>

  {#if loading && services.length === 0}
    <div class="loading">Checking service status...</div>
  {:else}
    <div class="services-grid">
      {#each services as service}
        <div class="service-card {service.isOk ? 'ok' : 'error'}">
          <div class="service-name">{service.name}</div>
          <div class="service-status">
            <span class="status-indicator {service.isOk ? 'running' : 'stopped'}"></span>
            {service.status}
          </div>
          <div class="service-message">{service.message}</div>
          {#if service.extraMsg}
            <div class="service-extra-msg">{service.extraMsg}</div>
          {/if}
        </div>
      {/each}
    </div>

    <div class="actions">
      <button class="btn secondary" on:click={refreshServices}>
        Refresh Status
      </button>
    </div>
  {/if}
</div>

<style>
  .system-status {
    margin-bottom: 2rem;
  }

  .loading {
    text-align: center;
    padding: 1rem;
    color: #666;
  }

  .services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .service-card {
    padding: 1rem;
    border-radius: 8px;
    background-color: #f5f5f5;
    border-left: 4px solid #ddd;
  }

  .service-card.ok {
    border-left-color: #4caf50;
  }

  .service-card.error {
    border-left-color: #f44336;
  }

  .service-name {
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }

  .service-status {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 0.5rem;
  }

  .status-indicator.running {
    background-color: #4caf50;
  }

  .status-indicator.stopped {
    background-color: #f44336;
  }

  .service-message {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    color: #666;
  }

  .service-extra-msg {
    font-size: 0.85rem;
    color: #ff9800;
    padding: 0.5rem;
    background-color: rgba(255, 152, 0, 0.1);
    border-radius: 4px;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
  }

  .btn.secondary {
    background-color: #f5f5f5;
  }
</style>
