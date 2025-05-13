<script>
  import { configStore } from '../store/config.js';
  import { onMount } from 'svelte';

  // Import API adapter
  import { fetchAvailableSymbols } from '../api';

  let loading = false;
  let availableSymbols = [];
  let searchQuery = "";
  let filteredSymbols = [];

  // Load available symbols
  onMount(async () => {
    loading = true;
    try {
      availableSymbols = await fetchAvailableSymbols();
      updateFilteredSymbols();
    } catch (error) {
      console.error("Failed to fetch symbols:", error);
    } finally {
      loading = false;
    }
  });

  // Watch for search changes
  $: {
    updateFilteredSymbols();
  }

  // Filter symbols based on search
  function updateFilteredSymbols() {
    if (!searchQuery) {
      filteredSymbols = [...availableSymbols];
    } else {
      const query = searchQuery.toLowerCase();
      filteredSymbols = availableSymbols.filter(symbol =>
        symbol.symbol.toLowerCase().includes(query) ||
        symbol.name.toLowerCase().includes(query)
      );
    }
  }

  // Add a symbol to the universe
  function addToUniverse(symbol) {
    if (!$configStore.universe.symbols.includes(symbol.symbol)) {
      $configStore.universe.symbols = [...$configStore.universe.symbols, symbol.symbol];
    }
  }

  // Remove a symbol from the universe
  function removeFromUniverse(symbol) {
    $configStore.universe.symbols = $configStore.universe.symbols.filter(s => s !== symbol);
  }

  // Check if a symbol is in the universe
  function isInUniverse(symbol) {
    return $configStore.universe.symbols.includes(symbol.symbol);
  }
</script>

<div class="tab-container">
  <h2>Trading Universe</h2>
  <p class="description">Define the set of symbols that will be monitored for trading opportunities.</p>

  <div class="universe-settings">
    <h3>Universe Configuration</h3>

    <div class="form-group">
      <label for="auto-universe">Auto-Generate Universe</label>
      <input
        type="checkbox"
        id="auto-universe"
        bind:checked={$configStore.universe.auto_generate}
      />
      <span class="hint">If enabled, trading universe will be generated automatically based on criteria below.</span>
    </div>

    <div class="form-group">
      <label for="min-market-cap">Minimum Market Cap ($M)</label>
      <input
        type="range"
        id="min-market-cap"
        min="100"
        max="10000"
        step="100"
        bind:value={$configStore.universe.min_market_cap}
        disabled={!$configStore.universe.auto_generate}
      />
      <span class="value-display">${($configStore.universe.min_market_cap / 1000).toFixed(1)}B</span>
    </div>

    <div class="form-group">
      <label for="min-volume">Minimum Avg. Volume</label>
      <input
        type="range"
        id="min-volume"
        min="100000"
        max="10000000"
        step="100000"
        bind:value={$configStore.universe.min_avg_volume}
        disabled={!$configStore.universe.auto_generate}
      />
      <span class="value-display">{($configStore.universe.min_avg_volume / 1000000).toFixed(1)}M</span>
    </div>

    <div class="form-group">
      <label for="max-price">Maximum Price ($)</label>
      <input
        type="number"
        id="max-price"
        min="1"
        max="10000"
        bind:value={$configStore.universe.max_price}
        disabled={!$configStore.universe.auto_generate}
      />
    </div>

    <div class="form-group">
      <label for="sectors">Sectors</label>
      <div class="checkbox-group">
        {#each ['Technology', 'Healthcare', 'Financial', 'Consumer', 'Industrial', 'Energy', 'Materials', 'Utilities', 'Real Estate', 'Communication'] as sector}
          <label class="checkbox-label">
            <input
              type="checkbox"
              checked={$configStore.universe.sectors.includes(sector)}
              on:change={(e) => {
                if (e.target.checked) {
                  $configStore.universe.sectors = [...$configStore.universe.sectors, sector];
                } else {
                  $configStore.universe.sectors = $configStore.universe.sectors.filter(s => s !== sector);
                }
              }}
              disabled={!$configStore.universe.auto_generate}
            />
            {sector}
          </label>
        {/each}
      </div>
    </div>
  </div>

  <div class="manual-universe">
    <h3>Manual Universe Selection</h3>
    <p class="description">Manually select symbols to add to your trading universe.</p>

    <div class="search-container">
      <input
        type="text"
        placeholder="Search symbols or companies..."
        bind:value={searchQuery}
        class="search-input"
      />
    </div>

    <div class="symbols-container">
      <div class="symbols-list">
        <h4>Available Symbols</h4>
        {#if loading}
          <div class="loading">Loading symbols...</div>
        {:else if filteredSymbols.length === 0}
          <div class="no-results">No symbols match your search</div>
        {:else}
          <div class="symbols-grid">
            {#each filteredSymbols as symbol}
              <div class="symbol-item" class:in-universe={isInUniverse(symbol)}>
                <div class="symbol-info">
                  <div class="symbol-ticker">{symbol.symbol}</div>
                  <div class="symbol-name">{symbol.name}</div>
                </div>
                <button
                  class="add-button"
                  disabled={isInUniverse(symbol)}
                  on:click={() => addToUniverse(symbol)}
                >
                  {isInUniverse(symbol) ? '✓' : '+'}
                </button>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="selected-symbols">
        <h4>Your Universe ({$configStore.universe.symbols.length} symbols)</h4>
        {#if $configStore.universe.symbols.length === 0}
          <div class="no-results">No symbols in universe</div>
        {:else}
          <div class="symbols-grid">
            {#each $configStore.universe.symbols as symbol}
              <div class="symbol-item selected">
                <div class="symbol-info">
                  <div class="symbol-ticker">{symbol}</div>
                </div>
                <button
                  class="remove-button"
                  on:click={() => removeFromUniverse(symbol)}
                >
                  ×
                </button>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .tab-container {
    padding: 20px;
  }

  .description {
    margin-bottom: 20px;
    color: #666;
  }

  .universe-settings, .manual-universe {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 20px;
  }

  .form-group {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
  }

  label {
    width: 180px;
    font-weight: 500;
  }

  .hint {
    margin-left: 10px;
    font-size: 12px;
    color: #666;
  }

  input[type="range"] {
    flex: 1;
    margin-right: 10px;
  }

  input[type="number"] {
    width: 80px;
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
  }

  .value-display {
    width: 60px;
    text-align: right;
  }

  .checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    width: auto;
    margin-right: 15px;
  }

  .checkbox-label input {
    margin-right: 5px;
  }

  .search-container {
    margin-bottom: 15px;
  }

  .search-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .symbols-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .symbols-list, .selected-symbols {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    height: 400px;
    overflow-y: auto;
  }

  h4 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
  }

  .loading, .no-results {
    padding: 20px;
    text-align: center;
    color: #888;
  }

  .symbols-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .symbol-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border: 1px solid #eee;
    border-radius: 4px;
    background-color: #fff;
  }

  .symbol-item.in-universe {
    background-color: #f0f8ff;
    border-color: #cce5ff;
  }

  .symbol-item.selected {
    background-color: #f0f8ff;
    border-color: #cce5ff;
  }

  .symbol-info {
    display: flex;
    flex-direction: column;
  }

  .symbol-ticker {
    font-weight: 600;
  }

  .symbol-name {
    font-size: 12px;
    color: #666;
  }

  .add-button, .remove-button {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .add-button {
    background-color: #4caf50;
    color: white;
  }

  .add-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .remove-button {
    background-color: #f44336;
    color: white;
  }
</style>
