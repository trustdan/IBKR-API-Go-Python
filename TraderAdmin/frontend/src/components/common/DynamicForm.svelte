<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let schema: any = null;
  export let data: Record<string, any> = {};
  export let parentPath: string = '';

  const dispatch = createEventDispatcher();

  function handleChange(path: string, value: any) {
    dispatch('change', { path, value });
  }

  // Helper functions to cast DOM event targets
  function getInputValue(event: Event): string {
    return (event.target as HTMLInputElement).value;
  }

  function getInputChecked(event: Event): boolean {
    return (event.target as HTMLInputElement).checked;
  }

  function getSelectValue(event: Event): string {
    return (event.target as HTMLSelectElement).value;
  }

  function getInputType(property: any): string {
    if (property.type === 'boolean') {
      return 'checkbox';
    }

    if (property.type === 'integer' || property.type === 'number') {
      if (property.minimum !== undefined && property.maximum !== undefined) {
        return 'range';
      }
      return 'number';
    }

    if (property.type === 'string') {
      if (property.enum) {
        return 'select';
      }
      return 'text';
    }

    if (property.type === 'object') {
      return 'object';
    }

    return 'text';
  }

  function isValid(property: any, value: any): boolean {
    if (value === undefined || value === null) {
      return !property.required;
    }

    if (property.type === 'number' || property.type === 'integer') {
      if (property.minimum !== undefined && value < property.minimum) {
        return false;
      }
      if (property.maximum !== undefined && value > property.maximum) {
        return false;
      }
    }

    if (property.type === 'string' && property.minLength !== undefined) {
      if (value.length < property.minLength) {
        return false;
      }
    }

    return true;
  }

  function getErrorMessage(property: any, value: any): string {
    if (value === undefined || value === null) {
      return property.required ? 'This field is required' : '';
    }

    if (property.type === 'number' || property.type === 'integer') {
      if (property.minimum !== undefined && value < property.minimum) {
        return `Value must be ≥ ${property.minimum}`;
      }
      if (property.maximum !== undefined && value > property.maximum) {
        return `Value must be ≤ ${property.maximum}`;
      }
    }

    if (property.type === 'string' && property.minLength !== undefined) {
      if (value.length < property.minLength) {
        return `Must be at least ${property.minLength} characters`;
      }
    }

    return '';
  }
</script>

{#if schema && schema.properties}
  <div class="dynamic-form">
    {#each Object.entries(schema.properties) as [fieldName, property]}
      {@const fullPath = parentPath ? `${parentPath}.${fieldName}` : fieldName}
      {@const fieldValue = data[fieldName]}
      {@const inputType = getInputType(property)}
      {@const valid = isValid(property, fieldValue)}
      {@const errorMsg = getErrorMessage(property, fieldValue)}

      {#if inputType === 'object' && property.properties}
        <fieldset>
          <legend>{property.title || fieldName}</legend>
          <svelte:self
            schema={property}
            data={data[fieldName] || {}}
            parentPath={fullPath}
            on:change
          />
        </fieldset>
      {:else}
        <div class="form-group" class:invalid={!valid}>
          <label for={fullPath}>
            {property.title || fieldName}
            {#if property.required}<span class="required">*</span>{/if}
          </label>

          {#if inputType === 'checkbox'}
            <input
              type="checkbox"
              id={fullPath}
              checked={fieldValue === true}
              on:change={(e) => handleChange(fullPath, getInputChecked(e))}
            />

          {:else if inputType === 'range'}
            <div class="range-container">
              <input
                type="range"
                id={fullPath}
                min={property.minimum}
                max={property.maximum}
                step={property.type === 'integer' ? 1 : 0.01}
                value={fieldValue}
                on:input={(e) => handleChange(fullPath, property.type === 'integer' ?
                  parseInt(getInputValue(e)) : parseFloat(getInputValue(e)))}
              />
              <span class="range-value">{fieldValue || 0}</span>
            </div>

          {:else if inputType === 'number'}
            <input
              type="number"
              id={fullPath}
              min={property.minimum}
              max={property.maximum}
              step={property.type === 'integer' ? 1 : 0.01}
              value={fieldValue}
              on:input={(e) => handleChange(fullPath, property.type === 'integer' ?
                parseInt(getInputValue(e)) : parseFloat(getInputValue(e)))}
            />

          {:else if inputType === 'select'}
            <select
              id={fullPath}
              value={fieldValue}
              on:change={(e) => handleChange(fullPath, getSelectValue(e))}
            >
              {#if !property.required}
                <option value="">-- Select --</option>
              {/if}
              {#each property.enum as option}
                <option value={option}>{option}</option>
              {/each}
            </select>

          {:else}
            <input
              type="text"
              id={fullPath}
              value={fieldValue || ''}
              on:input={(e) => handleChange(fullPath, getInputValue(e))}
            />
          {/if}

          {#if !valid}
            <div class="error-message">{errorMsg}</div>
          {/if}

          {#if property.description}
            <div class="description">{property.description}</div>
          {/if}
        </div>
      {/if}
    {/each}
  </div>
{/if}

<style>
  .dynamic-form {
    width: 100%;
  }

  .form-group {
    margin-bottom: 15px;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
  }

  input[type="text"],
  input[type="number"],
  select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .invalid input,
  .invalid select {
    border-color: #f44336;
  }

  .error-message {
    color: #f44336;
    font-size: 0.8rem;
    margin-top: 4px;
  }

  .description {
    color: #666;
    font-size: 0.8rem;
    margin-top: 4px;
  }

  .required {
    color: #f44336;
  }

  fieldset {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 15px;
  }

  legend {
    padding: 0 8px;
    font-weight: 500;
  }

  .range-container {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  input[type="range"] {
    flex: 1;
  }

  .range-value {
    min-width: 50px;
    text-align: right;
  }
</style>
