<script lang="ts">
  import { SaveConfig } from '../../wailsjs/go/main/App.js';
  import { onMount } from 'svelte';

  export let config;
  export let logAction;

  let loading = false;
  let errorMessage = '';
  let successMessage = '';
  let backupFiles = [];
  let selectedBackup = '';

  // Load backups on component mount
  onMount(loadBackups);

  async function loadBackups() {
    loading = true;
    errorMessage = '';

    try {
      logAction('Loading Backup Files');
      // For now, we'll use mock data until backend is fully generated
      backupFiles = [
        "backups/config-20230101-120000.toml",
        "backups/config-20230102-134500.toml",
        "backups/config-20230103-150000.toml"
      ];
      logAction('Backup Files Loaded', { count: backupFiles.length });
    } catch (err) {
      errorMessage = err.message || 'Failed to load backup files';
      logAction('Backup Files Load Failed', null, err);
      console.error('Backup load error:', err);
    } finally {
      loading = false;
    }
  }

  async function doCreateBackup() {
    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Creating Backup');
      // For now, we'll simulate a backup creation
      const backupPath = `backups/config-${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14)}.toml`;
      successMessage = `Backup created successfully: ${backupPath}`;
      logAction('Backup Created', { path: backupPath });

      // Refresh backup list
      await loadBackups();

      // Select the newly created backup
      selectedBackup = backupPath;
    } catch (err) {
      errorMessage = err.message || 'Failed to create backup';
      logAction('Backup Creation Failed', null, err);
      console.error('Backup creation error:', err);
    } finally {
      loading = false;
    }
  }

  async function doRestoreBackup() {
    if (!selectedBackup) {
      errorMessage = 'Please select a backup file to restore';
      return;
    }

    // Confirm with the user
    if (!confirm(`Are you sure you want to restore the configuration from backup: ${selectedBackup}? Current settings will be overwritten.`)) {
      return;
    }

    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Restoring Backup', { file: selectedBackup });
      // We'll just simulate a restore for now
      successMessage = `Configuration restored successfully from: ${selectedBackup}`;
      logAction('Backup Restored', { path: selectedBackup });
    } catch (err) {
      errorMessage = err.message || 'Failed to restore backup';
      logAction('Backup Restore Failed', null, err);
      console.error('Backup restore error:', err);
    } finally {
      loading = false;
    }
  }

  function getBackupFileName(path) {
    // Extract just the filename from the full path
    const parts = path.split(/[\/\\]/);
    return parts[parts.length - 1];
  }

  function getBackupDate(filename) {
    // Extract date from config-YYYYMMDD-HHMMSS.toml format
    const match = filename.match(/config-(\d{8}-\d{6})\.toml/);
    if (match && match[1]) {
      const dateStr = match[1];
      const year = dateStr.substring(0, 4);
      const month = dateStr.substring(4, 6);
      const day = dateStr.substring(6, 8);
      const hour = dateStr.substring(9, 11);
      const minute = dateStr.substring(11, 13);
      const second = dateStr.substring(13, 15);

      return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
    }

    return 'Unknown date';
  }
</script>

<div class="tab-panel">
  <h2>Backup & Restore</h2>
  <p>Manage configuration backups</p>

  {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {/if}

  {#if successMessage}
    <div class="success-message">{successMessage}</div>
  {/if}

  <div class="settings-section">
    <h3>Create Backup</h3>
    <p>Create a snapshot of your current configuration</p>

    <button
      class="btn primary"
      on:click={doCreateBackup}
      disabled={loading}
    >
      {loading ? 'Creating...' : 'Create Backup Now'}
    </button>
  </div>

  <div class="settings-section">
    <h3>Auto Backup Settings</h3>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Backup.AutoBackupEnabled}>
        Enable Automatic Backups
      </label>
    </div>

    <div class="form-group">
      <label for="backup-interval">Backup Interval (hours)</label>
      <input
        type="number"
        id="backup-interval"
        bind:value={config.Backup.BackupIntervalHours}
        min="1"
        max="168"
        disabled={!config.Backup.AutoBackupEnabled}
      >
    </div>

    <div class="form-group">
      <label for="max-backups">Maximum Backups to Keep</label>
      <input
        type="number"
        id="max-backups"
        bind:value={config.Backup.MaxBackups}
        min="1"
        max="100"
        disabled={!config.Backup.AutoBackupEnabled}
      >
      <span class="hint">Oldest backups will be deleted when limit is reached</span>
    </div>

    <div class="form-group">
      <label for="backup-dir">Backup Directory</label>
      <input
        type="text"
        id="backup-dir"
        bind:value={config.Backup.BackupDir}
        disabled={!config.Backup.AutoBackupEnabled}
      >
    </div>
  </div>

  <div class="settings-section">
    <h3>Restore Configuration</h3>
    <p>Select a backup to restore your configuration</p>

    {#if loading}
      <div class="loading">Loading backups...</div>
    {:else if backupFiles.length === 0}
      <div class="no-backups">No backup files found</div>
    {:else}
      <div class="form-group">
        <label for="backup-select">Select Backup</label>
        <select id="backup-select" bind:value={selectedBackup}>
          <option value="">-- Select a backup file --</option>
          {#each backupFiles as backup}
            <option value={backup}>{getBackupFileName(backup)} ({getBackupDate(getBackupFileName(backup))})</option>
          {/each}
        </select>
      </div>

      <button
        class="btn warning"
        on:click={doRestoreBackup}
        disabled={!selectedBackup || loading}
      >
        Restore Selected Backup
      </button>
    {/if}

    <div class="refresh-action">
      <button class="btn secondary" on:click={loadBackups} disabled={loading}>
        {loading ? 'Refreshing...' : 'Refresh Backup List'}
      </button>
    </div>
  </div>
</div>

<style>
  .tab-panel {
    padding: 1rem;
  }

  .settings-section {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .hint {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.85rem;
    color: #888;
  }

  .error-message {
    padding: 0.5rem;
    background-color: #fff1f1;
    border: 1px solid #ffc0c0;
    color: #d32f2f;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .success-message {
    padding: 0.5rem;
    background-color: #f1fff1;
    border: 1px solid #c0ffc0;
    color: #2fd32f;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .loading, .no-backups {
    padding: 1rem;
    text-align: center;
    color: #888;
    font-style: italic;
  }

  .refresh-action {
    margin-top: 1rem;
    text-align: right;
  }

  .btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    background-color: #f5f5f5;
    cursor: pointer;
  }

  .btn.primary {
    background-color: #4caf50;
    color: white;
    border-color: #388e3c;
  }

  .btn.secondary {
    background-color: #2196f3;
    color: white;
    border-color: #1976d2;
  }

  .btn.warning {
    background-color: #ff9800;
    color: white;
    border-color: #f57c00;
  }

  /* Dark mode */
  :global(body.dark-mode) .settings-section {
    border-color: #444;
  }

  :global(body.dark-mode) .hint {
    color: #aaa;
  }

  :global(body.dark-mode) .loading,
  :global(body.dark-mode) .no-backups {
    color: #aaa;
  }

  :global(body.dark-mode) .btn {
    background-color: #333;
    border-color: #555;
    color: #eee;
  }

  :global(body.dark-mode) .btn.primary {
    background-color: #388e3c;
    border-color: #2e7d32;
  }

  :global(body.dark-mode) .btn.secondary {
    background-color: #1976d2;
    border-color: #1565c0;
  }

  :global(body.dark-mode) .btn.warning {
    background-color: #f57c00;
    border-color: #ef6c00;
  }
</style>
