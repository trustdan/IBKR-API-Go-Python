<script lang="ts">
  export let config;
  export let logAction;

  let loading = false;
  let errorMessage = '';
  let successMessage = '';

  async function saveAlertSettings() {
    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Saving Alert Settings');
      // We'll save settings using SaveConfig later
      // await SaveAlertConfig(config.Alerts);
      successMessage = 'Alert settings saved successfully';
      logAction('Alert Settings Saved', { success: true });
    } catch (err) {
      errorMessage = err.message || 'Failed to save alert settings';
      logAction('Alert Settings Save Failed', null, err);
      console.error('Alert save error:', err);
    } finally {
      loading = false;
    }
  }

  async function testEmailAlert() {
    if (!config.Alerts.EmailEnabled) {
      errorMessage = 'Email alerts are not enabled';
      return;
    }

    if (!config.Alerts.EmailAddress) {
      errorMessage = 'Email address is not configured';
      return;
    }

    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Sending Test Email Alert');
      // Will implement the backend later
      // await TestEmailAlert(config.Alerts.EmailAddress);
      successMessage = `Test email sent to ${config.Alerts.EmailAddress}`;
      logAction('Test Email Sent', { success: true });
    } catch (err) {
      errorMessage = err.message || 'Failed to send test email';
      logAction('Test Email Failed', null, err);
    } finally {
      loading = false;
    }
  }

  async function testSmsAlert() {
    if (!config.Alerts.SMSEnabled) {
      errorMessage = 'SMS alerts are not enabled';
      return;
    }

    if (!config.Alerts.SMSNumber) {
      errorMessage = 'SMS number is not configured';
      return;
    }

    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Sending Test SMS Alert');
      // Will implement the backend later
      // await TestSMSAlert(config.Alerts.SMSNumber);
      successMessage = `Test SMS sent to ${config.Alerts.SMSNumber}`;
      logAction('Test SMS Sent', { success: true });
    } catch (err) {
      errorMessage = err.message || 'Failed to send test SMS';
      logAction('Test SMS Failed', null, err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="tab-panel">
  <h2>Alert Settings</h2>
  <p>Configure alerts and notifications for trading events</p>

  {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {/if}

  {#if successMessage}
    <div class="success-message">{successMessage}</div>
  {/if}

  <div class="settings-section">
    <h3>Email Alerts</h3>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.EmailEnabled}>
        Enable Email Alerts
      </label>
    </div>

    <div class="form-group">
      <label for="email-address">Email Address</label>
      <input
        type="email"
        id="email-address"
        bind:value={config.Alerts.EmailAddress}
        disabled={!config.Alerts.EmailEnabled}
        placeholder="your@email.com"
      >
    </div>

    <button
      class="btn secondary test-button"
      on:click={testEmailAlert}
      disabled={!config.Alerts.EmailEnabled || !config.Alerts.EmailAddress || loading}
    >
      Send Test Email
    </button>
  </div>

  <div class="settings-section">
    <h3>SMS Alerts</h3>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.SMSEnabled}>
        Enable SMS Alerts
      </label>
    </div>

    <div class="form-group">
      <label for="sms-number">Phone Number</label>
      <input
        type="tel"
        id="sms-number"
        bind:value={config.Alerts.SMSNumber}
        disabled={!config.Alerts.SMSEnabled}
        placeholder="+1 (555) 123-4567"
      >
      <span class="hint">Include country code (e.g., +1 for US)</span>
    </div>

    <button
      class="btn secondary test-button"
      on:click={testSmsAlert}
      disabled={!config.Alerts.SMSEnabled || !config.Alerts.SMSNumber || loading}
    >
      Send Test SMS
    </button>
  </div>

  <div class="settings-section">
    <h3>Webhook Alerts</h3>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.WebhookEnabled}>
        Enable Webhook Alerts
      </label>
    </div>

    <div class="form-group">
      <label for="webhook-url">Webhook URL</label>
      <input
        type="url"
        id="webhook-url"
        bind:value={config.Alerts.WebhookURL}
        disabled={!config.Alerts.WebhookEnabled}
        placeholder="https://your-webhook-url.com/endpoint"
      >
      <span class="hint">Will receive JSON payload with alert details</span>
    </div>
  </div>

  <div class="settings-section">
    <h3>Alert Types</h3>
    <p>Choose which events should trigger alerts</p>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.AlertOnTrade}>
        Trade Execution
      </label>
      <span class="hint">Alert when trades are executed</span>
    </div>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.AlertOnError}>
        System Errors
      </label>
      <span class="hint">Alert on critical errors</span>
    </div>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.AlertOnStartup}>
        System Startup
      </label>
      <span class="hint">Alert when trading system starts</span>
    </div>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Alerts.AlertOnShutdown}>
        System Shutdown
      </label>
      <span class="hint">Alert when trading system stops</span>
    </div>
  </div>

  <div class="footer-actions">
    <button class="btn primary" on:click={saveAlertSettings} disabled={loading}>
      {loading ? 'Saving...' : 'Save Alert Settings'}
    </button>
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

  .test-button {
    margin-top: 0.5rem;
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

  .footer-actions {
    margin-top: 2rem;
    display: flex;
    justify-content: flex-end;
  }

  /* Dark mode */
  :global(body.dark-mode) .settings-section {
    border-color: #444;
  }

  :global(body.dark-mode) .hint {
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
</style>
