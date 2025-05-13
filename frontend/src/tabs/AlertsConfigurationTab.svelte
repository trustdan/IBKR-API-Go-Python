<script>
  import { onMount } from 'svelte';
  import { testAlertNotification } from '../stores/metricsStore';
  import { currentConfig, updateConfig, saveConfig } from '../stores/configStore';
  import { Button, Card, CardBody, CardHeader, Form, FormGroup, Input, Label, Alert, Row, Col } from '@sveltestrap/sveltestrap';

  let loading = false;
  let saveSuccess = false;
  let saveError = null;
  let confirmRestart = false;
  let testingEmail = false;
  let testingSlack = false;
  let testSuccess = false;
  let testError = null;

  // Local state for alerts configuration
  let enabled = true;
  let thresholds = {
    maxOrderLatencyMs: 1000,
    minDailyRealizedPnl: -500,
    maxPortfolioDrawdownPercentageToday: 5.0,
    maxApiErrorsPerHour: 10
  };
  let emailNotifications = {
    enabled: false,
    recipients: [],
    smtpHost: '',
    smtpPort: 587,
    smtpUser: '',
    smtpPass: ''
  };
  let slackNotifications = {
    enabled: false,
    webhookUrl: ''
  };
  let newRecipient = '';

  onMount(() => {
    if ($currentConfig && $currentConfig.AlertsConfig) {
      enabled = $currentConfig.AlertsConfig.Enabled;

      if ($currentConfig.AlertsConfig.Thresholds) {
        thresholds = {
          maxOrderLatencyMs: $currentConfig.AlertsConfig.Thresholds.MaxOrderLatencyMs || 1000,
          minDailyRealizedPnl: $currentConfig.AlertsConfig.Thresholds.MinDailyRealizedPnl || -500,
          maxPortfolioDrawdownPercentageToday: $currentConfig.AlertsConfig.Thresholds.MaxPortfolioDrawdownPercentageToday || 5.0,
          maxApiErrorsPerHour: $currentConfig.AlertsConfig.Thresholds.MaxApiErrorsPerHour || 10
        };
      }

      if ($currentConfig.AlertsConfig.Notifications) {
        if ($currentConfig.AlertsConfig.Notifications.Email) {
          emailNotifications = {
            enabled: $currentConfig.AlertsConfig.Notifications.Email.Enabled || false,
            recipients: $currentConfig.AlertsConfig.Notifications.Email.Recipients || [],
            smtpHost: $currentConfig.AlertsConfig.Notifications.Email.SmtpHost || '',
            smtpPort: $currentConfig.AlertsConfig.Notifications.Email.SmtpPort || 587,
            smtpUser: $currentConfig.AlertsConfig.Notifications.Email.SmtpUser || '',
            smtpPass: $currentConfig.AlertsConfig.Notifications.Email.SmtpPass || ''
          };
        }

        if ($currentConfig.AlertsConfig.Notifications.Slack) {
          slackNotifications = {
            enabled: $currentConfig.AlertsConfig.Notifications.Slack.Enabled || false,
            webhookUrl: $currentConfig.AlertsConfig.Notifications.Slack.WebhookUrl || ''
          };
        }
      }
    }
  });

  function updateAlertConfig() {
    const updatedConfig = {
      ...$currentConfig,
      AlertsConfig: {
        Enabled: enabled,
        Thresholds: {
          MaxOrderLatencyMs: thresholds.maxOrderLatencyMs,
          MinDailyRealizedPnl: thresholds.minDailyRealizedPnl,
          MaxPortfolioDrawdownPercentageToday: thresholds.maxPortfolioDrawdownPercentageToday,
          MaxApiErrorsPerHour: thresholds.maxApiErrorsPerHour
        },
        Notifications: {
          Email: {
            Enabled: emailNotifications.enabled,
            Recipients: emailNotifications.recipients,
            SmtpHost: emailNotifications.smtpHost,
            SmtpPort: emailNotifications.smtpPort,
            SmtpUser: emailNotifications.smtpUser,
            SmtpPass: emailNotifications.smtpPass
          },
          Slack: {
            Enabled: slackNotifications.enabled,
            WebhookUrl: slackNotifications.webhookUrl
          }
        }
      }
    };

    updateConfig(updatedConfig);
  }

  async function handleSaveConfig() {
    loading = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveConfig(true); // true indicates a restart is required
      saveSuccess = true;
      setTimeout(() => (saveSuccess = false), 3000);
    } catch (err) {
      saveError = err.message;
    } finally {
      loading = false;
      confirmRestart = false;
    }
  }

  async function handleTestNotification(channel) {
    let testing = false;

    if (channel === 'email') {
      if (!emailNotifications.enabled || emailNotifications.recipients.length === 0) {
        testError = 'Email notifications are not enabled or no recipients configured';
        setTimeout(() => (testError = null), 3000);
        return;
      }
      testing = testingEmail = true;
    } else if (channel === 'slack') {
      if (!slackNotifications.enabled || !slackNotifications.webhookUrl) {
        testError = 'Slack notifications are not enabled or webhook URL not configured';
        setTimeout(() => (testError = null), 3000);
        return;
      }
      testing = testingSlack = true;
    }

    testSuccess = false;
    testError = null;

    try {
      await testAlertNotification(channel);
      testSuccess = true;
      setTimeout(() => (testSuccess = false), 3000);
    } catch (err) {
      testError = err.message;
      setTimeout(() => (testError = null), 5000);
    } finally {
      if (channel === 'email') {
        testingEmail = false;
      } else if (channel === 'slack') {
        testingSlack = false;
      }
    }
  }

  function handleEnabledChange() {
    enabled = !enabled;
    updateAlertConfig();
  }

  function addRecipient() {
    if (newRecipient && isValidEmail(newRecipient) && !emailNotifications.recipients.includes(newRecipient)) {
      emailNotifications.recipients = [...emailNotifications.recipients, newRecipient];
      newRecipient = '';
      updateAlertConfig();
    }
  }

  function removeRecipient(email) {
    emailNotifications.recipients = emailNotifications.recipients.filter(r => r !== email);
    updateAlertConfig();
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
</script>

<h2 class="mb-4">Alerts Configuration</h2>

{#if saveSuccess}
  <Alert color="success" dismissible>Configuration saved successfully and services restarted!</Alert>
{/if}

{#if saveError}
  <Alert color="danger" dismissible>Error saving configuration: {saveError}</Alert>
{/if}

{#if testSuccess}
  <Alert color="success" dismissible>Test alert sent successfully!</Alert>
{/if}

{#if testError}
  <Alert color="danger" dismissible>Error sending test alert: {testError}</Alert>
{/if}

<Card class="mb-4">
  <CardHeader>
    <h4>Alert System Settings</h4>
  </CardHeader>
  <CardBody>
    <FormGroup check>
      <Input
        type="checkbox"
        id="enableAlerts"
        name="enableAlerts"
        checked={enabled}
        on:change={handleEnabledChange}
      />
      <Label for="enableAlerts" check>Enable Alert System</Label>
    </FormGroup>

    <h5 class="mt-4 mb-3">Alert Thresholds</h5>
    <Row>
      <Col md={6}>
        <FormGroup>
          <Label for="maxOrderLatency">Max Order Latency (ms)</Label>
          <Input
            type="number"
            id="maxOrderLatency"
            min="0"
            step="50"
            value={thresholds.maxOrderLatencyMs}
            on:change={(e) => {
              thresholds.maxOrderLatencyMs = parseFloat(e.target.value);
              updateAlertConfig();
            }}
            disabled={!enabled}
          />
          <small class="form-text text-muted">Alert when order execution latency exceeds this value</small>
        </FormGroup>
      </Col>
      <Col md={6}>
        <FormGroup>
          <Label for="minDailyPnl">Min Daily Realized P&L</Label>
          <Input
            type="number"
            id="minDailyPnl"
            step="100"
            value={thresholds.minDailyRealizedPnl}
            on:change={(e) => {
              thresholds.minDailyRealizedPnl = parseFloat(e.target.value);
              updateAlertConfig();
            }}
            disabled={!enabled}
          />
          <small class="form-text text-muted">Alert when daily P&L falls below this value</small>
        </FormGroup>
      </Col>
    </Row>
    <Row>
      <Col md={6}>
        <FormGroup>
          <Label for="maxDrawdown">Max Portfolio Drawdown (%)</Label>
          <Input
            type="number"
            id="maxDrawdown"
            min="0"
            max="100"
            step="0.5"
            value={thresholds.maxPortfolioDrawdownPercentageToday}
            on:change={(e) => {
              thresholds.maxPortfolioDrawdownPercentageToday = parseFloat(e.target.value);
              updateAlertConfig();
            }}
            disabled={!enabled}
          />
          <small class="form-text text-muted">Alert when portfolio drawdown exceeds this percentage</small>
        </FormGroup>
      </Col>
      <Col md={6}>
        <FormGroup>
          <Label for="maxApiErrors">Max API Errors (per hour)</Label>
          <Input
            type="number"
            id="maxApiErrors"
            min="0"
            step="1"
            value={thresholds.maxApiErrorsPerHour}
            on:change={(e) => {
              thresholds.maxApiErrorsPerHour = parseInt(e.target.value);
              updateAlertConfig();
            }}
            disabled={!enabled}
          />
          <small class="form-text text-muted">Alert when API errors exceed this count per hour</small>
        </FormGroup>
      </Col>
    </Row>
  </CardBody>
</Card>

<Card class="mb-4">
  <CardHeader>
    <h4>Email Notifications</h4>
  </CardHeader>
  <CardBody>
    <h5 class="mt-4 mb-3">Email Notifications</h5>
    <Row>
      <Col md={12}>
        <FormGroup check>
          <Input
            type="checkbox"
            id="enableEmailAlerts"
            name="enableEmailAlerts"
            checked={emailNotifications.enabled}
            on:change={() => {
              emailNotifications.enabled = !emailNotifications.enabled;
              updateAlertConfig();
            }}
            disabled={!enabled}
          />
          <Label for="enableEmailAlerts" check>Enable Email Notifications</Label>
        </FormGroup>
      </Col>
    </Row>

    <FormGroup>
      <Label for="smtpHost">SMTP Server</Label>
      <Input
        type="text"
        id="smtpHost"
        placeholder="smtp.example.com"
        value={emailNotifications.smtpHost}
        on:change={(e) => {
          emailNotifications.smtpHost = e.target.value;
          updateAlertConfig();
        }}
        disabled={!enabled || !emailNotifications.enabled}
      />
    </FormGroup>

    <Row>
      <Col md={4}>
        <FormGroup>
          <Label for="smtpPort">SMTP Port</Label>
          <Input
            type="number"
            id="smtpPort"
            placeholder="587"
            value={emailNotifications.smtpPort}
            on:change={(e) => {
              emailNotifications.smtpPort = parseInt(e.target.value);
              updateAlertConfig();
            }}
            disabled={!enabled || !emailNotifications.enabled}
          />
        </FormGroup>
      </Col>
      <Col md={4}>
        <FormGroup>
          <Label for="smtpUser">SMTP Username</Label>
          <Input
            type="text"
            id="smtpUser"
            placeholder="username"
            value={emailNotifications.smtpUser}
            on:change={(e) => {
              emailNotifications.smtpUser = e.target.value;
              updateAlertConfig();
            }}
            disabled={!enabled || !emailNotifications.enabled}
          />
        </FormGroup>
      </Col>
      <Col md={4}>
        <FormGroup>
          <Label for="smtpPass">SMTP Password</Label>
          <Input
            type="password"
            id="smtpPass"
            placeholder="password or env var"
            value={emailNotifications.smtpPass}
            on:change={(e) => {
              emailNotifications.smtpPass = e.target.value;
              updateAlertConfig();
            }}
            disabled={!enabled || !emailNotifications.enabled}
          />
        </FormGroup>
      </Col>
    </Row>

    <FormGroup>
      <Label>Recipients</Label>
      <div class="d-flex mb-2">
        <Input
          type="email"
          placeholder="Email address"
          value={newRecipient}
          on:change={(e) => (newRecipient = e.target.value)}
          disabled={!enabled || !emailNotifications.enabled}
          class="mr-2"
        />
        <Button
          color="secondary"
          on:click={addRecipient}
          disabled={!enabled || !emailNotifications.enabled || !newRecipient || !isValidEmail(newRecipient)}
        >
          Add
        </Button>
      </div>

      <div class="recipient-list">
        {#if emailNotifications.recipients.length === 0}
          <div class="text-muted">No recipients configured</div>
        {:else}
          {#each emailNotifications.recipients as email}
            <div class="recipient-item">
              {email}
              <Button
                size="sm"
                color="link"
                class="p-0 ml-2"
                on:click={() => removeRecipient(email)}
                disabled={!enabled || !emailNotifications.enabled}
              >
                ✕
              </Button>
            </div>
          {/each}
        {/if}
      </div>
    </FormGroup>

    <Button
      color="info"
      on:click={() => handleTestNotification('email')}
      disabled={!enabled || !emailNotifications.enabled || emailNotifications.recipients.length === 0 || testingEmail}
      class="mt-2"
    >
      {testingEmail ? 'Sending...' : 'Test Email Notification'}
    </Button>
  </CardBody>
</Card>

<Card class="mb-4">
  <CardHeader>
    <h4>Slack Notifications</h4>
  </CardHeader>
  <CardBody>
    <h5 class="mt-4 mb-3">Slack Notifications</h5>
    <Row>
      <Col md={12}>
        <FormGroup check>
          <Input
            type="checkbox"
            id="enableSlackAlerts"
            name="enableSlackAlerts"
            checked={slackNotifications.enabled}
            on:change={() => {
              slackNotifications.enabled = !slackNotifications.enabled;
              updateAlertConfig();
            }}
            disabled={!enabled}
          />
          <Label for="enableSlackAlerts" check>Enable Slack Notifications</Label>
        </FormGroup>
      </Col>
    </Row>

    <FormGroup>
      <Label for="webhookUrl">Webhook URL</Label>
      <Input
        type="text"
        id="webhookUrl"
        placeholder="https://hooks.slack.com/services/..."
        value={slackNotifications.webhookUrl}
        on:change={(e) => {
          slackNotifications.webhookUrl = e.target.value;
          updateAlertConfig();
        }}
        disabled={!enabled || !slackNotifications.enabled}
      />
      <small class="form-text text-muted">Enter the webhook URL or environment variable name containing it</small>
    </FormGroup>

    <Button
      color="info"
      on:click={() => handleTestNotification('slack')}
      disabled={!enabled || !slackNotifications.enabled || !slackNotifications.webhookUrl || testingSlack}
      class="mt-2"
    >
      {testingSlack ? 'Sending...' : 'Test Slack Notification'}
    </Button>
  </CardBody>
</Card>

<div class="mt-4">
  {#if confirmRestart}
    <Alert color="warning">
      This action will pause trading, save the configuration, and restart the services. Continue?
      <div class="mt-2">
        <Button color="danger" on:click={handleSaveConfig} disabled={loading}>
          {loading ? 'Saving...' : 'Yes, Save & Restart'}
        </Button>
        <Button color="secondary" class="ml-2" on:click={() => (confirmRestart = false)}>
          Cancel
        </Button>
      </div>
    </Alert>
  {:else}
    <Button
      color="primary"
      on:click={() => (confirmRestart = true)}
      disabled={loading}
    >
      Save & Restart Services
    </Button>
  {/if}
</div>

<style>
  h2 {
    font-size: 1.75rem;
  }

  h4 {
    font-size: 1.25rem;
    margin: 0;
  }

  h5 {
    font-size: 1.1rem;
  }

  .recipient-list {
    margin-top: 0.5rem;
  }

  .recipient-item {
    display: flex;
    align-items: center;
    padding: 0.3rem 0.5rem;
    margin-bottom: 0.25rem;
    background-color: #f8f9fa;
    border-radius: 0.25rem;
  }
</style>
