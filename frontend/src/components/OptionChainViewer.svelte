<script lang="ts">
  import { onMount } from 'svelte';

  // Sample option chain data for demonstration
  export let symbol = '';
  export let expirationDate = '';
  export let filters = {
    minOpenInterest: 500,
    maxBidAskSpreadPercentage: 0.6,
    minIVRank: 25,
    maxIVRank: 75
  };

  // Sample data structure for options
  interface OptionContract {
    strike: number;
    callBid: number;
    callAsk: number;
    callOpenInterest: number;
    callIV: number;
    callDelta: number;
    callGamma: number;
    callTheta: number;
    callVega: number;
    putBid: number;
    putAsk: number;
    putOpenInterest: number;
    putIV: number;
    putDelta: number;
    putGamma: number;
    putTheta: number;
    putVega: number;
  }

  let optionChain: OptionContract[] = [];
  let loading = true;
  let error = '';
  let underlyingPrice = 0;
  let ivRank = 0;

  // Function to fetch option chain data (mock for now)
  async function fetchOptionChain() {
    try {
      loading = true;
      error = '';

      // In a real implementation, this would call the backend
      // const data = await GetOptionChain(symbol, expirationDate);

      // Create mock data for demonstration
      const mockUnderlyingPrice = 415.75;
      underlyingPrice = mockUnderlyingPrice;
      ivRank = 45; // Mock IV Rank

      const strikePrices = Array.from({ length: 11 }, (_, i) =>
        Math.round((mockUnderlyingPrice - 25 + (i * 5)) * 100) / 100
      );

      const mockOptionChain = strikePrices.map(strike => {
        const atmDiff = Math.abs(strike - mockUnderlyingPrice);
        const isAtm = atmDiff < 5;
        const isItm = strike < mockUnderlyingPrice;

        const callBid = isItm ? (mockUnderlyingPrice - strike) + Math.random() * 2 : Math.random() * 1.5;
        const callAsk = callBid + (Math.random() * 0.3 + 0.1);
        const callIV = (isAtm ? 0.25 : 0.20 + Math.random() * 0.15);
        const callDelta = isItm ? 0.5 + Math.random() * 0.4 : Math.random() * 0.45;
        const callOpenInterest = Math.floor(Math.random() * 2000) + (isAtm ? 1000 : 0);

        const putBid = !isItm ? (strike - mockUnderlyingPrice) + Math.random() * 2 : Math.random() * 1.5;
        const putAsk = putBid + (Math.random() * 0.3 + 0.1);
        const putIV = (isAtm ? 0.28 : 0.22 + Math.random() * 0.15);
        const putDelta = !isItm ? -0.5 - Math.random() * 0.4 : -Math.random() * 0.45;
        const putOpenInterest = Math.floor(Math.random() * 2000) + (isAtm ? 1200 : 0);

        return {
          strike,
          callBid: Math.round(callBid * 100) / 100,
          callAsk: Math.round(callAsk * 100) / 100,
          callOpenInterest,
          callIV: Math.round(callIV * 100),
          callDelta: Math.round(callDelta * 100) / 100,
          callGamma: Math.round(Math.random() * 0.05 * 100) / 100,
          callTheta: -Math.round(Math.random() * 0.2 * 100) / 100,
          callVega: Math.round(Math.random() * 0.3 * 100) / 100,
          putBid: Math.round(putBid * 100) / 100,
          putAsk: Math.round(putAsk * 100) / 100,
          putOpenInterest,
          putIV: Math.round(putIV * 100),
          putDelta: Math.round(putDelta * 100) / 100,
          putGamma: Math.round(Math.random() * 0.05 * 100) / 100,
          putTheta: -Math.round(Math.random() * 0.2 * 100) / 100,
          putVega: Math.round(Math.random() * 0.3 * 100) / 100
        };
      });

      optionChain = mockOptionChain;
    } catch (err) {
      error = `Failed to fetch option chain: ${err}`;
    } finally {
      loading = false;
    }
  }

  // Apply filters to the option chain
  function applyFilters(chain: OptionContract[]) {
    return chain.filter(option => {
      // Check call side
      const callBidAskSpread = option.callAsk - option.callBid;
      const callBidAskSpreadPct = option.callBid > 0 ? callBidAskSpread / ((option.callBid + option.callAsk) / 2) : 999;

      const callPassesFilters =
        option.callOpenInterest >= filters.minOpenInterest &&
        callBidAskSpreadPct <= filters.maxBidAskSpreadPercentage;

      // Check put side
      const putBidAskSpread = option.putAsk - option.putBid;
      const putBidAskSpreadPct = option.putBid > 0 ? putBidAskSpread / ((option.putBid + option.putAsk) / 2) : 999;

      const putPassesFilters =
        option.putOpenInterest >= filters.minOpenInterest &&
        putBidAskSpreadPct <= filters.maxBidAskSpreadPercentage;

      // A strike is included if either call or put passes filters
      return callPassesFilters || putPassesFilters;
    });
  }

  // Calculate if IV is within the IV Rank filters
  function isIVInFilterRange(iv: number) {
    return iv >= filters.minIVRank && iv <= filters.maxIVRank;
  }

  // Get CSS class for highlighting filters
  function getFilterClass(value: number, min: number, condition: (a: number, b: number) => boolean) {
    return condition(value, min) ? '' : 'filter-failed';
  }

  // When symbol or expiration changes, fetch new data
  $: if (symbol && expirationDate) {
    fetchOptionChain();
  }

  onMount(() => {
    if (!symbol) {
      symbol = 'SPY'; // Default for demonstration
      expirationDate = '2023-12-15';
    }

    fetchOptionChain();
  });

  // Apply filters to the chain for display
  $: filteredChain = applyFilters(optionChain);
</script>

<div class="option-chain-viewer">
  <div class="viewer-header">
    <div class="symbol-info">
      <h3>{symbol || 'Select Symbol'}</h3>
      {#if underlyingPrice > 0}
        <div class="price-info">
          <span class="price">${underlyingPrice.toFixed(2)}</span>
          <span class="iv-rank">IV Rank: {ivRank}%</span>
        </div>
      {/if}
    </div>

    <div class="expiration-info">
      {#if expirationDate}
        <span>Expiration: {expirationDate}</span>
      {:else}
        <span>Select Expiration</span>
      {/if}
    </div>

    <div class="filter-controls">
      <div class="filter-title">Filters:</div>
      <div class="filter-values">
        <span>Min OI: {filters.minOpenInterest}</span>
        <span>Max Spread: {filters.maxBidAskSpreadPercentage * 100}%</span>
        <span>IV Rank: {filters.minIVRank}%-{filters.maxIVRank}%</span>
      </div>
    </div>
  </div>

  {#if loading}
    <div class="loading">Loading option chain data...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if filteredChain.length === 0}
    <div class="empty-message">No option contracts match the current filters.</div>
  {:else}
    <div class="option-table-container">
      <table class="option-table">
        <thead>
          <tr>
            <th class="calls-header" colspan="6">Calls</th>
            <th class="strike-header">Strike</th>
            <th class="puts-header" colspan="6">Puts</th>
          </tr>
          <tr>
            <th>OI</th>
            <th>IV%</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Delta</th>
            <th>Theta</th>
            <th class="strike-column">Strike</th>
            <th>OI</th>
            <th>IV%</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Delta</th>
            <th>Theta</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredChain as option}
            {@const callBidAskPct = ((option.callAsk - option.callBid) / ((option.callBid + option.callAsk) / 2)) * 100}
            {@const putBidAskPct = ((option.putAsk - option.putBid) / ((option.putBid + option.putAsk) / 2)) * 100}
            {@const atm = Math.abs(option.strike - underlyingPrice) < 2.5}

            <tr class={atm ? 'atm-row' : ''}>
              <!-- Call side -->
              <td class={getFilterClass(option.callOpenInterest, filters.minOpenInterest, (a, b) => a >= b)}>
                {option.callOpenInterest.toLocaleString()}
              </td>
              <td class={isIVInFilterRange(option.callIV) ? '' : 'filter-failed'}>
                {option.callIV}%
              </td>
              <td>{option.callBid.toFixed(2)}</td>
              <td>{option.callAsk.toFixed(2)}</td>
              <td>{option.callDelta.toFixed(2)}</td>
              <td>{option.callTheta.toFixed(2)}</td>

              <!-- Strike price -->
              <td class="strike-column">${option.strike.toFixed(2)}</td>

              <!-- Put side -->
              <td class={getFilterClass(option.putOpenInterest, filters.minOpenInterest, (a, b) => a >= b)}>
                {option.putOpenInterest.toLocaleString()}
              </td>
              <td class={isIVInFilterRange(option.putIV) ? '' : 'filter-failed'}>
                {option.putIV}%
              </td>
              <td>{option.putBid.toFixed(2)}</td>
              <td>{option.putAsk.toFixed(2)}</td>
              <td>{option.putDelta.toFixed(2)}</td>
              <td>{option.putTheta.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="chain-stats">
      <div class="stats-item">
        <span class="stats-label">Matching Strikes:</span>
        <span class="stats-value">{filteredChain.length}</span>
      </div>
      <div class="stats-item">
        <span class="stats-label">Total Strikes:</span>
        <span class="stats-value">{optionChain.length}</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .option-chain-viewer {
    background-color: white;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    width: 100%;
  }

  .viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background-color: #f1f5f9;
    border-bottom: 1px solid #e2e8f0;
  }

  .symbol-info h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 0.25rem 0;
    color: #1e293b;
  }

  .price-info {
    display: flex;
    gap: 1rem;
  }

  .price {
    font-weight: 600;
    color: #0f172a;
  }

  .iv-rank {
    color: #64748b;
  }

  .expiration-info {
    font-weight: 500;
    color: #64748b;
  }

  .filter-controls {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .filter-title {
    font-weight: 500;
    color: #64748b;
    font-size: 0.875rem;
  }

  .filter-values {
    display: flex;
    gap: 0.75rem;
    font-size: 0.75rem;
    color: #64748b;
  }

  .loading, .error, .empty-message {
    padding: 2rem;
    text-align: center;
    color: #64748b;
  }

  .error {
    color: #dc2626;
  }

  .option-table-container {
    max-height: 500px;
    overflow-y: auto;
  }

  .option-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
  }

  .option-table th {
    position: sticky;
    top: 0;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    padding: 0.5rem;
    text-align: center;
    font-weight: 600;
    color: #475569;
  }

  .option-table td {
    padding: 0.4rem 0.5rem;
    text-align: right;
    border-bottom: 1px solid #f1f5f9;
  }

  .calls-header {
    background-color: #dbeafe !important;
    color: #1e40af !important;
  }

  .puts-header {
    background-color: #fee2e2 !important;
    color: #991b1b !important;
  }

  .strike-header {
    background-color: #f1f5f9 !important;
  }

  .strike-column {
    background-color: #f8fafc;
    font-weight: 600;
    text-align: center !important;
    border-left: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
  }

  .atm-row {
    background-color: #f0f9ff;
  }

  .filter-failed {
    color: #94a3b8;
    font-style: italic;
  }

  .chain-stats {
    display: flex;
    justify-content: flex-end;
    gap: 1.5rem;
    padding: 0.75rem 1rem;
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
  }

  .stats-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .stats-label {
    font-size: 0.8125rem;
    color: #64748b;
  }

  .stats-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1e293b;
  }
</style>
