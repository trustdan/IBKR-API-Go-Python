<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let activeTab: string;

  const dispatch = createEventDispatcher();

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'connection', label: 'IBKR Connection' },
    { id: 'trading', label: 'Trading & Risk' },
    { id: 'strategies', label: 'Strategies' },
    { id: 'options', label: 'Options' },
    { id: 'universe', label: 'Universe' },
    { id: 'scanner', label: 'Scanner' },
    { id: 'data', label: 'Data Management' },
    { id: 'logging', label: 'Logging' },
    { id: 'schedule', label: 'Scheduling' },
    { id: 'alerts', label: 'Alerts' },
    { id: 'backup', label: 'Backup & Restore' },
    { id: 'dev', label: 'Developer Tools' },
    { id: 'help', label: 'Help' }
  ];

  function selectTab(tabId: string) {
    dispatch('tabchange', tabId);
  }

  function handleKeydown(event: KeyboardEvent, tabId: string) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectTab(tabId);
    }
  }
</script>

<div class="nav-tabs">
  <ul>
    {#each tabs as tab}
      <li
        class:active={activeTab === tab.id}
        on:click={() => selectTab(tab.id)}
        on:keydown={(e) => handleKeydown(e, tab.id)}
        tabindex="0"
        role="button"
        aria-pressed={activeTab === tab.id}
      >
        {tab.label}
      </li>
    {/each}
  </ul>
</div>

<style>
  .nav-tabs {
    width: 200px;
    background-color: #2c3e50;
    height: 100%;
    color: white;
  }

  ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }

  li {
    padding: 12px 15px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  li:hover {
    background-color: #34495e;
  }

  li.active {
    background-color: #3498db;
    font-weight: bold;
  }

  li:focus {
    outline: 2px solid #3498db;
    outline-offset: -2px;
  }
</style>
