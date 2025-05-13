<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let activeTab: string = 'overview';
  export let layout: 'side' | 'top' = 'side';

  interface Tab {
    id: string;
    label: string;
    icon?: string;
  }

  // Available tabs in the application
  const tabs: Tab[] = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'connection', label: 'IBKR Connection', icon: '🔌' },
    { id: 'trading', label: 'Trading & Risk', icon: '📈' },
    { id: 'strategies', label: 'Strategies', icon: '🧩' },
    { id: 'options', label: 'Options', icon: '⚙️' },
    { id: 'universe', label: 'Universe', icon: '🌐' },
    { id: 'scanner', label: 'Scanner', icon: '🔍' },
    { id: 'data', label: 'Data Management', icon: '💾' },
    { id: 'logging', label: 'Logging', icon: '📝' },
    { id: 'schedule', label: 'Scheduling', icon: '🕒' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
    { id: 'backup', label: 'Backup & Restore', icon: '🔄' },
    { id: 'devtools', label: 'Developer Tools', icon: '🔧' },
    { id: 'help', label: 'Help', icon: '❓' }
  ];

  const dispatch = createEventDispatcher();

  function handleTabClick(tabId: string) {
    if (tabId !== activeTab) {
      // You can add a check for unsaved changes here before changing tabs
      dispatch('tabChange', tabId);
    }
  }
</script>

<nav class={`nav-tabs nav-tabs-${layout}`}>
  <ul>
    {#each tabs as tab}
      <li class={activeTab === tab.id ? 'active' : ''}>
        <button
          on:click={() => handleTabClick(tab.id)}
          aria-selected={activeTab === tab.id}
          role="tab"
          aria-controls={`tab-${tab.id}`}
          id={`tab-button-${tab.id}`}
        >
          {#if tab.icon}
            <span class="tab-icon">{tab.icon}</span>
          {/if}
          <span class="tab-label">{tab.label}</span>
        </button>
      </li>
    {/each}
  </ul>
</nav>

<style>
  .nav-tabs {
    --tab-active-color: #0066cc;
    --tab-hover-bg: #f0f7ff;
    --tab-active-bg: #e5f1ff;
  }

  .nav-tabs ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
  }

  /* Side layout */
  .nav-tabs-side {
    width: 220px;
    border-right: 1px solid #e0e0e0;
    height: 100%;
    overflow-y: auto;
    background-color: #f9f9f9;
  }

  .nav-tabs-side ul {
    flex-direction: column;
  }

  .nav-tabs-side li {
    margin: 0;
  }

  .nav-tabs-side button {
    display: flex;
    align-items: center;
    width: 100%;
    text-align: left;
    padding: 0.75rem 1rem;
    border: none;
    background: none;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .nav-tabs-side li.active button {
    background-color: var(--tab-active-bg);
    color: var(--tab-active-color);
    font-weight: 600;
    position: relative;
  }

  .nav-tabs-side li.active button::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background-color: var(--tab-active-color);
  }

  .nav-tabs-side button:hover:not(:disabled) {
    background-color: var(--tab-hover-bg);
  }

  /* Top layout */
  .nav-tabs-top {
    width: 100%;
    border-bottom: 1px solid #e0e0e0;
    overflow-x: auto;
    background-color: #f9f9f9;
  }

  .nav-tabs-top ul {
    flex-direction: row;
  }

  .nav-tabs-top li {
    margin: 0;
  }

  .nav-tabs-top button {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border: none;
    background: none;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background-color 0.2s;
    white-space: nowrap;
  }

  .nav-tabs-top li.active button {
    color: var(--tab-active-color);
    font-weight: 600;
    position: relative;
  }

  .nav-tabs-top li.active button::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: -1px;
    height: 2px;
    background-color: var(--tab-active-color);
  }

  .nav-tabs-top button:hover:not(:disabled) {
    background-color: var(--tab-hover-bg);
  }

  /* Tab icon and label */
  .tab-icon {
    margin-right: 0.5rem;
    font-size: 1rem;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .nav-tabs-side {
      width: 100%;
      height: auto;
      border-right: none;
      border-bottom: 1px solid #e0e0e0;
    }

    .nav-tabs-side ul {
      flex-direction: row;
      flex-wrap: wrap;
    }

    .nav-tabs-side li.active button::before {
      width: 100%;
      height: 3px;
      top: auto;
      bottom: -1px;
    }

    .tab-label {
      margin-left: 0.25rem;
    }
  }
</style>
