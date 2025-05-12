<script lang="ts">
  import { onMount } from 'svelte';
  import StatusBar from './components/StatusBar.svelte';
  import NavTabs from './components/NavTabs.svelte';
  import ConnectionTab from './components/ConnectionTab.svelte';
  import OptionsTab from './components/OptionsTab.svelte';
  import SchedulingTab from './components/SchedulingTab.svelte';

  // Import the store functions
  import { loadSchema, loadConfig, configStore, hasChanges, saveConfig } from './store/config';
  import { initStatusPolling } from './store/status';

  // Active tab state
  let activeTab = 'overview';
  let loading = true;

  // Handle tab change events from NavTabs
  function handleTabChange(event: CustomEvent) {
    activeTab = event.detail;
  }

  // Save configuration changes
  async function saveChanges() {
    if ($configStore) {
      await saveConfig($configStore);
    }
  }

  // Initialize the app
  onMount(async () => {
    // Load schema and config data
    await loadSchema();
    await loadConfig();

    // Initialize status polling
    const cleanup = initStatusPolling();

    // Set loading state to false
    loading = false;

    // Cleanup on unmount
    return cleanup;
  });
</script>

<main class="app-container">
  <header>
    <div class="logo">
      <h1>TraderAdmin</h1>
    </div>
    <StatusBar />
  </header>

  <div class="content">
    <aside>
      <NavTabs activeTab={activeTab} on:tabchange={handleTabChange} />
    </aside>

    <section class="tab-content">
      {#if loading}
        <div class="loading">Loading application...</div>
      {:else}
        <!-- Conditionally render the active tab -->
        {#if activeTab === 'overview'}
          <div class="tab-panel">
            <h2>Overview</h2>
            <p>Welcome to TraderAdmin - Your IBKR Trading Platform.</p>
            <!-- Overview content will go here -->
          </div>

        {:else if activeTab === 'connection'}
          <ConnectionTab />

        {:else if activeTab === 'options'}
          <OptionsTab />

        {:else if activeTab === 'schedule'}
          <SchedulingTab />

        <!-- Add more tabs here as they are implemented -->
        {:else}
          <div class="tab-panel">
            <h2>{activeTab}</h2>
            <p>This tab is under construction.</p>
          </div>
        {/if}

        <!-- Save button (only show when there are changes) -->
        {#if $hasChanges}
          <div class="save-bar">
            <button class="save-btn" on:click={saveChanges}>Save Changes</button>
          </div>
        {/if}
      {/if}
    </section>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  }

  .app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 15px;
    height: 60px;
    background-color: #2c3e50;
    color: white;
  }

  .logo h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  .content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  aside {
    height: 100%;
  }

  .tab-content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    position: relative;
  }

  .tab-panel {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-size: 1.2rem;
    color: #666;
  }

  .save-bar {
    position: sticky;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 15px;
    background-color: rgba(255, 255, 255, 0.9);
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    text-align: right;
    z-index: 10;
    margin-top: 20px;
  }

  .save-btn {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
  }

  .save-btn:hover {
    background-color: #45a049;
  }
</style>
