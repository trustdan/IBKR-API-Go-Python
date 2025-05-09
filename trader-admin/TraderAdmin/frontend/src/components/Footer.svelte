<script lang="ts">
  import { onMount } from 'svelte';
  import { GetVersion, GetVersionDetails } from '../../wailsjs/go/main/App.js';

  let version = '';
  let versionDetails = null;
  let showDetails = false;

  onMount(async () => {
    try {
      version = await GetVersion();
      versionDetails = await GetVersionDetails();
    } catch (error) {
      console.error('Failed to load version information:', error);
    }
  });

  function toggleDetails() {
    showDetails = !showDetails;
  }
</script>

<footer class="app-footer">
  <div class="footer-content">
    <div class="version-info">
      <span on:click={toggleDetails} class="version-text">v{version}</span>
      {#if showDetails && versionDetails}
        <div class="version-details">
          <p>Version: {versionDetails.version}</p>
          <p>Build Date: {versionDetails.buildDate}</p>
          <p>Commit: {versionDetails.commitHash}</p>
        </div>
      {/if}
    </div>
    <div class="copyright">
      &copy; {new Date().getFullYear()} IBKR Auto Trader
    </div>
  </div>
</footer>

<style>
  .app-footer {
    margin-top: auto;
    padding: 8px 16px;
    border-top: 1px solid var(--border-color);
    font-size: 0.8rem;
    color: var(--text-secondary);
    background-color: var(--bg-secondary);
  }

  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .version-text {
    cursor: pointer;
  }

  .version-text:hover {
    text-decoration: underline;
  }

  .version-details {
    position: absolute;
    bottom: 40px;
    left: 16px;
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    font-size: 0.8rem;
    z-index: 100;
  }

  .version-details p {
    margin: 4px 0;
  }
</style> 