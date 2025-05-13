<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let text: string;
  export let position: 'top' | 'right' | 'bottom' | 'left' = 'top';
  export let trigger: 'hover' | 'click' = 'hover';
  export let delay: number = 200; // ms
  export let maxWidth: string = '200px';
  export let disabled: boolean = false;

  const dispatch = createEventDispatcher();

  let visible = false;
  let timeoutId: number;

  function showTooltip() {
    if (disabled) return;

    clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      visible = true;
      dispatch('show');
    }, delay);
  }

  function hideTooltip() {
    clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      visible = false;
      dispatch('hide');
    }, 50);
  }

  function toggleTooltip() {
    if (disabled) return;

    if (visible) {
      hideTooltip();
    } else {
      showTooltip();
    }
  }
</script>

<div
  class="tooltip-container"
  on:mouseenter={trigger === 'hover' ? showTooltip : undefined}
  on:mouseleave={trigger === 'hover' ? hideTooltip : undefined}
  on:click={trigger === 'click' ? toggleTooltip : undefined}
  on:focus={trigger === 'hover' ? showTooltip : undefined}
  on:blur={trigger === 'hover' ? hideTooltip : undefined}
>
  <slot></slot>

  {#if visible}
    <div
      class={`tooltip tooltip-${position}`}
      style={`max-width: ${maxWidth};`}
      role="tooltip"
    >
      {text}
      <div class={`tooltip-arrow tooltip-arrow-${position}`}></div>
    </div>
  {/if}
</div>

<style>
  .tooltip-container {
    position: relative;
    display: inline-flex;
    vertical-align: middle;
  }

  .tooltip {
    position: absolute;
    z-index: 1000;
    background-color: #333;
    color: white;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    font-size: 0.875rem;
    line-height: 1.4;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    pointer-events: none;
  }

  .tooltip-arrow {
    position: absolute;
    width: 0;
    height: 0;
    border-style: solid;
  }

  /* Positions */
  .tooltip-top {
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-0.5rem);
    margin-bottom: 0.5rem;
  }

  .tooltip-top .tooltip-arrow {
    bottom: -0.25rem;
    left: 50%;
    transform: translateX(-50%);
    border-width: 0.25rem 0.25rem 0;
    border-color: #333 transparent transparent;
  }

  .tooltip-right {
    left: 100%;
    top: 50%;
    transform: translateY(-50%) translateX(0.5rem);
    margin-left: 0.5rem;
  }

  .tooltip-right .tooltip-arrow {
    left: -0.25rem;
    top: 50%;
    transform: translateY(-50%);
    border-width: 0.25rem 0.25rem 0.25rem 0;
    border-color: transparent #333 transparent transparent;
  }

  .tooltip-bottom {
    top: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(0.5rem);
    margin-top: 0.5rem;
  }

  .tooltip-bottom .tooltip-arrow {
    top: -0.25rem;
    left: 50%;
    transform: translateX(-50%);
    border-width: 0 0.25rem 0.25rem;
    border-color: transparent transparent #333;
  }

  .tooltip-left {
    right: 100%;
    top: 50%;
    transform: translateY(-50%) translateX(-0.5rem);
    margin-right: 0.5rem;
  }

  .tooltip-left .tooltip-arrow {
    right: -0.25rem;
    top: 50%;
    transform: translateY(-50%);
    border-width: 0.25rem 0 0.25rem 0.25rem;
    border-color: transparent transparent transparent #333;
  }
</style>
