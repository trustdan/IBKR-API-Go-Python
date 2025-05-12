<script lang="ts">
  import { onMount } from 'svelte';
  import { LoadConfig, SaveAndRestartStack, TestAlert } from '../../wailsjs/go/main/App';
  import { toast } from '@zerodevx/svelte-toast';

  let config: any = {};
  let loading: boolean = false;
  let saving: boolean = false;
  let testingSending: boolean = false;

  // Alert test type
  let testAlertType: string = 'general';

  onMount(async () => {
    try {
      loading = true;
      config = await LoadConfig();

      // Initialize alerts config if not present
      if (!config.alerts) {
        config.alerts = {
          enable_email: false,
          email_to: '',
          enable_slack: false,
          slack_webhook_url: '',
          alert_on_errors: true,
          alert_on_trades: true,
          max_latency_ms: 500,
          min_daily_pnl: -1000,
          max_errors: 5
        };
      }
    } catch (error) {
      console.error('Failed to load config:', error);
      toast.push('Error loading configuration: ' + error.message, {
        theme: { '--toastBackground': '#F56565', '--toastBarBackground': '#C53030' }
      });
    } finally {
      loading = false;
    }
  });

  async function saveAlertSettings() {
    if (!config) return;

    try {
      saving = true;
      const result = await SaveAndRestartStack(config);
      toast.push('Alert settings saved and services restarted', {
        theme: { '--toastBackground': '#48BB78', '--toastBarBackground': '#2F855A' }
      });
      console.log('Save result:', result);
    } catch (error) {
      console.error('Failed to save alert settings:', error);
      toast.push('Error saving alert settings: ' + error.message, {
        theme: { '--toastBackground': '#F56565', '--toastBarBackground': '#C53030' }
      });
    } finally {
      saving = false;
    }
  }

  async function sendTestAlert() {
    try {
      testingSending = true;
      const result = await TestAlert(testAlertType);
      toast.push('Test alert sent: ' + result, {
        theme: { '--toastBackground': '#48BB78', '--toastBarBackground': '#2F855A' }
      });
    } catch (error) {
      console.error('Failed to send test alert:', error);
      toast.push('Error sending test alert: ' + error.message, {
        theme: { '--toastBackground': '#F56565', '--toastBarBackground': '#C53030' }
      });
    } finally {
      testingSending = false;
    }
  }

  function hasAlertChannelsEnabled(): boolean {
    return (config?.alerts?.enable_email && config?.alerts?.email_to) ||
           (config?.alerts?.enable_slack && config?.alerts?.slack_webhook_url);
  }
</script>

<div class="alerts-tab">
  <h2>Alerts & Notifications</h2>

  {#if loading}
    <div class="loading">Loading alert settings...</div>
  {:else}
    <div class="alert-settings-form">
      <!-- Alert Thresholds Section -->
      <div class="settings-section">
        <h3>Alert Thresholds</h3>
        <p class="section-description">Configure when alerts should be triggered</p>

        <div class="form-group">
          <label for="max_latency_ms">Maximum Latency (ms):</label>
          <input
            type="number"
            id="max_latency_ms"
            bind:value={config.alerts.max_latency_ms}
            min="0"
            step="50"
          />
          <span class="help-text">Alert when order execution latency exceeds this value</span>
        </div>

        <div class="form-group">
          <label for="min_daily_pnl">Minimum Daily P&L ($):</label>
          <input
            type="number"
            id="min_daily_pnl"
            bind:value={config.alerts.min_daily_pnl}
            step="100"
          />
          <span class="help-text">Alert when daily P&L falls below this value</span>
        </div>

        <div class="form-group">
          <label for="max_errors">Maximum Errors:</label>
          <input
            type="number"
            id="max_errors"
            bind:value={config.alerts.max_errors}
            min="0"
            step="1"
          />
          <span class="help-text">Alert when error count exceeds this value</span>
        </div>
      </div>

      <!-- Alert Notifications Section -->
      <div class="settings-section">
        <h3>Notification Channels</h3>
        <p class="section-description">Configure where alerts should be sent</p>

        <!-- Email Alerts -->
        <div class="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              bind:checked={config.alerts.enable_email}
            />
            Enable Email Alerts
          </label>
        </div>

        {#if config.alerts.enable_email}
          <div class="form-group">
            <label for="email_to">Email Address:</label>
            <input
              type="email"
              id="email_to"
              bind:value={config.alerts.email_to}
              placeholder="trader@example.com"
            />
            <span class="help-text">Where alert emails will be sent</span>
          </div>
        {/if}

        <!-- Slack Alerts -->
        <div class="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              bind:checked={config.alerts.enable_slack}
            />
            Enable Slack Alerts
          </label>
        </div>

        {#if config.alerts.enable_slack}
          <div class="form-group">
            <label for="slack_webhook_url">Slack Webhook URL:</label>
            <input
              type="text"
              id="slack_webhook_url"
              bind:value={config.alerts.slack_webhook_url}
              placeholder="https://hooks.slack.com/services/..."
            />
            <span class="help-text">Slack incoming webhook URL</span>
          </div>
        {/if}

        <!-- Alert Triggers -->
        <div class="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              bind:checked={config.alerts.alert_on_errors}
            />
            Alert on Errors
          </label>
        </div>

        <div class="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              bind:checked={config.alerts.alert_on_trades}
            />
            Alert on Trades
          </label>
        </div>
      </div>

      <!-- Test Alert Section -->
      <div class="settings-section">
        <h3>Test Alert</h3>
        <p class="section-description">Send a test alert to verify notification channels</p>

        <div class="form-group">
          <label for="test_alert_type">Alert Type:</label>
          <select id="test_alert_type" bind:value={testAlertType}>
            <option value="general">General</option>
            <option value="latency">High Latency</option>
            <option value="pnl">P&L Alert</option>
            <option value="error">Error Alert</option>
          </select>
        </div>

        <button
          class="test-button"
          on:click={sendTestAlert}
          disabled={testingSending || !hasAlertChannelsEnabled()}
        >
          {testingSending ? 'Sending...' : 'Send Test Alert'}
        </button>

        {#if !hasAlertChannelsEnabled()}
          <div class="warning-message">
            Configure at least one notification channel to send test alerts
          </div>
        {/if}
      </div>

      <div class="form-actions">
        <button
          class="save-button"
          on:click={saveAlertSettings}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Alert Settings'}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .alerts-tab {
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

  .alert-settings-form {
    max-width: 800px;
  }

  .settings-section {
    background-color: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .section-description {
    color: #718096;
    font-size: 0.875rem;
    margin-bottom: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
  }

  .checkbox-group label {
    display: flex;
    align-items: center;
    font-weight: normal;
  }

  .checkbox-group input {
    margin-right: 0.5rem;
  }

  input[type="text"],
  input[type="email"],
  input[type="number"],
  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #cbd5e0;
    border-radius: 0.25rem;
    font-size: 1rem;
    max-width: 500px;
  }

  .help-text {
    display: block;
    font-size: 0.8rem;
    color: #718096;
    margin-top: 0.25rem;
  }

  .form-actions {
    margin-top: 2rem;
  }

  .save-button, .test-button {
    background-color: #4299e1;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    transition: background-color 0.2s;
  }

  .save-button {
    background-color: #48bb78;
  }

  .save-button:hover {
    background-color: #38a169;
  }

  .test-button:hover {
    background-color: #3182ce;
  }

  .save-button:disabled, .test-button:disabled {
    background-color: #a0aec0;
    cursor: not-allowed;
  }

  .warning-message {
    margin-top: 0.5rem;
    color: #e53e3e;
    font-size: 0.875rem;
  }
</style>
