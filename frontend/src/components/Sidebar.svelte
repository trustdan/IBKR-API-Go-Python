<script lang="ts">
  import { activeTab } from '../stores/activeTab';

  // Navigation items
  const navItems = [
    { id: 'monitoring', label: 'Monitoring', icon: '📊' },
    { id: 'connection', label: 'Connection', icon: '🔌' },
    { id: 'scheduling', label: 'Scheduling', icon: '🕒' },
    { id: 'strategies', label: 'Strategies', icon: '📈' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
    { id: 'logs', label: 'Logs', icon: '📋' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  // Set active tab
  function setActiveTab(tabId: string) {
    activeTab.set(tabId);
  }
</script>

<div class="sidebar">
  <div class="logo">
    <h1>TraderAdmin</h1>
  </div>

  <nav>
    <ul>
      {#each navItems as item}
        <li
          class:active={$activeTab === item.id}
          on:click={() => setActiveTab(item.id)}
        >
          <span class="icon">{item.icon}</span>
          <span class="label">{item.label}</span>
        </li>
      {/each}
    </ul>
  </nav>

  <div class="version">
    <p>v1.0.0</p>
  </div>
</div>

<style>
  .sidebar {
    width: 220px;
    height: 100%;
    background-color: #1e293b;
    color: #f8fafc;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #334155;
  }

  .logo {
    padding: 1.5rem 1rem;
    border-bottom: 1px solid #334155;
    text-align: center;
  }

  .logo h1 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  nav {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 0;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    color: #94a3b8;
    transition: background-color 0.2s, color 0.2s;
  }

  li:hover {
    background-color: #334155;
    color: #f8fafc;
  }

  li.active {
    background-color: #334155;
    color: #f8fafc;
    border-left: 3px solid #3b82f6;
  }

  .icon {
    margin-right: 0.75rem;
    font-size: 1.1rem;
    width: 1.5rem;
    text-align: center;
  }

  .label {
    font-size: 0.9rem;
    font-weight: 500;
  }

  .version {
    padding: 1rem;
    text-align: center;
    font-size: 0.75rem;
    color: #64748b;
    border-top: 1px solid #334155;
  }

  .version p {
    margin: 0;
  }
</style>
