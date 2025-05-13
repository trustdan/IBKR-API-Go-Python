<script lang="ts">
  import { activeTab, setActiveTab, type TabId } from '../stores/activeTab';

  // Define the tabs for navigation
  const tabs: Array<{ id: TabId; label: string; icon: string }> = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'connection', label: 'Connection', icon: '🔌' },
    { id: 'trading-risk', label: 'Trading & Risk', icon: '⚖️' },
    { id: 'strategies', label: 'Strategies', icon: '📈' },
    { id: 'options', label: 'Options', icon: '🔄' },
    { id: 'scheduling', label: 'Scheduling', icon: '🕒' },
    { id: 'monitoring', label: 'Monitoring', icon: '📡' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];
</script>

<div class="nav-tabs">
  <div class="logo">
    <span class="logo-text">TraderAdmin</span>
  </div>

  <nav>
    <ul>
      {#each tabs as tab}
        <li class:active={$activeTab === tab.id}>
          <button on:click={() => setActiveTab(tab.id)}>
            <span class="icon">{tab.icon}</span>
            <span class="label">{tab.label}</span>
          </button>
        </li>
      {/each}
    </ul>
  </nav>
</div>

<style>
  .nav-tabs {
    background-color: #1e293b;
    color: #cbd5e1;
    width: 240px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .logo {
    padding: 1.5rem 1rem;
    border-bottom: 1px solid #334155;
  }

  .logo-text {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f8fafc;
  }

  nav {
    flex: 1;
    padding: 1rem 0;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    margin-bottom: 0.25rem;
  }

  button {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.75rem 1rem;
    border: none;
    background-color: transparent;
    color: inherit;
    text-align: left;
    cursor: pointer;
    border-radius: 0.25rem;
    transition: background-color 0.2s, color 0.2s;
  }

  button:hover {
    background-color: #334155;
    color: #f8fafc;
  }

  li.active button {
    background-color: #3b82f6;
    color: #ffffff;
  }

  .icon {
    margin-right: 0.75rem;
    font-size: 1.1rem;
  }

  .label {
    font-size: 0.95rem;
  }
</style>
