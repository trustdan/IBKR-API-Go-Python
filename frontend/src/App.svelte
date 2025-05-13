<script lang="ts">
  import { onMount } from 'svelte';
  import logo from './assets/images/logo-universal.png';
  import { Authenticate, IsAuthenticated, LogOut } from '../wailsjs/go/main/App';
  import { throttle } from './lib/utils';

  // UI Components
  import NavTabs from './components/NavTabs.svelte';
  import StatusBar from './components/StatusBar.svelte';
  import ToastContainer from './components/shared/ToastContainer.svelte';

  // Stores
  import { activeTab, isSmallScreen, windowWidth, globalSearchVisible } from './store/ui';
  import { updateStatus } from './store/status';
  import { initialize as initializeConfig } from './store/config';
  import { setupShortcuts } from './lib/shortcuts';

  // Initial state
  let username: string = "";
  let password: string = "";
  let authenticated: boolean = false;
  let authMessage: string = "";
  let loading: boolean = true;

  // For status bar data
  let ibkrConnected = false;
  let ibkrError = null;
  let containers = [];
  let lastUpdated = null;
  let statusUpdating = false;

  // Toast reference
  let toastRef: ToastContainer;

  // Update screen size for responsive layout
  $: layout = $isSmallScreen ? 'top' : 'side';

  // Update window dimensions
  const handleResize = throttle(() => {
    windowWidth.set(window.innerWidth);
  }, 100);

  // Handle tab changes
  function handleTabChange(event: CustomEvent<string>) {
    activeTab.set(event.detail);
  }

  // Handle status refresh
  async function handleStatusRefresh() {
    await updateStatus();
  }

  onMount(async () => {
    // Check authentication
    try {
      const isAuth = await IsAuthenticated();
      authenticated = isAuth;
    } catch (error) {
      console.error('Authentication check failed:', error);
    } finally {
      loading = false;
    }

    // Initialize configuration if authenticated
    if (authenticated) {
      try {
        await initializeConfig();
      } catch (error) {
        console.error('Failed to initialize configuration:', error);
        if (toastRef) {
          toastRef.error('Failed to load configuration');
        }
      }
    }

    // Set up window resize event
    window.addEventListener('resize', handleResize);

    // Set up keyboard shortcuts
    const cleanupShortcuts = setupShortcuts();

    // Initial status update
    handleStatusRefresh();

    // Set up status polling (every 30 seconds)
    const statusInterval = setInterval(handleStatusRefresh, 30000);

    // Clean up on component unmount
    return () => {
      window.removeEventListener('resize', handleResize);
      cleanupShortcuts();
      clearInterval(statusInterval);
    };
  });

  async function login(): Promise<void> {
    if (!username || !password) {
      authMessage = "Please enter both username and password";
      return;
    }

    loading = true;
    try {
      const result = await Authenticate(username, password);
      authenticated = result;

      if (!result) {
        authMessage = "Invalid username or password";
      } else {
        authMessage = "";

        // Initialize configuration after successful login
        await initializeConfig();
      }
    } catch (error) {
      authMessage = "Authentication error";
      console.error(error);
    } finally {
      loading = false;
    }
  }

  async function logout(): Promise<void> {
    await LogOut();
    authenticated = false;
    username = "";
    password = "";
  }
</script>

<!-- Toast notifications -->
<ToastContainer bind:this={toastRef} />

<!-- Main application layout -->
<main>
  {#if loading}
    <div class="loading-screen">
      <img alt="IBKR Trader Admin" class="logo" src="{logo}">
      <div class="loading-indicator">Loading...</div>
    </div>
  {:else if authenticated}
    <div class="app-container">
      <!-- Status bar -->
      <StatusBar
        {ibkrConnected}
        {ibkrError}
        {containers}
        lastUpdated={lastUpdated}
        updating={statusUpdating}
        on:refresh={handleStatusRefresh}
      />

      <div class="content-layout">
        <!-- Navigation tabs -->
        <NavTabs
          activeTab={$activeTab}
          {layout}
          on:tabChange={handleTabChange}
        />

        <!-- Main content area -->
        <div class="content-area">
          <header class="content-header">
            <h1>{$activeTab.charAt(0).toUpperCase() + $activeTab.slice(1)}</h1>
            <div class="user-controls">
              <button class="logout-button" on:click={logout}>Logout</button>
            </div>
          </header>

          <div class="tab-content">
            {#if $activeTab === 'overview'}
              <p>Overview tab content will go here</p>
            {:else if $activeTab === 'connection'}
              <p>Connection tab content will go here</p>
            {:else if $activeTab === 'trading'}
              <p>Trading & Risk tab content will go here</p>
            {:else if $activeTab === 'strategies'}
              <p>Strategies tab content will go here</p>
            {:else if $activeTab === 'options'}
              <p>Options tab content will go here</p>
            {:else if $activeTab === 'universe'}
              <p>Universe tab content will go here</p>
            {:else if $activeTab === 'scanner'}
              <p>Scanner tab content will go here</p>
            {:else if $activeTab === 'data'}
              <p>Data Management tab content will go here</p>
            {:else if $activeTab === 'logging'}
              <p>Logging tab content will go here</p>
            {:else if $activeTab === 'schedule'}
              <p>Scheduling tab content will go here</p>
            {:else if $activeTab === 'alerts'}
              <p>Alerts tab content will go here</p>
            {:else if $activeTab === 'backup'}
              <p>Backup & Restore tab content will go here</p>
            {:else if $activeTab === 'devtools'}
              <p>Developer Tools tab content will go here</p>
            {:else if $activeTab === 'help'}
              <p>Help & Documentation tab content will go here</p>
            {:else}
              <p>Unknown tab</p>
            {/if}
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="login-screen">
      <img alt="IBKR Trader Admin" class="logo" src="{logo}">

      <div class="login-container">
        <h2>Login to IBKR Trader Admin</h2>

        {#if authMessage}
          <div class="auth-message error">{authMessage}</div>
        {/if}

        <div class="input-box">
          <label for="username">Username</label>
          <input
            id="username"
            type="text"
            bind:value={username}
            placeholder="Enter username"
            on:keypress={(e) => e.key === 'Enter' && login()}
          />
        </div>

        <div class="input-box">
          <label for="password">Password</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            placeholder="Enter password"
            on:keypress={(e) => e.key === 'Enter' && login()}
          />
        </div>

        <button class="btn login-btn" on:click={login} disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </div>
    </div>
  {/if}
</main>

<style>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
      Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
  }

  main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
  }

  .loading-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    background-color: #f5f5f5;
  }

  .logo {
    width: 200px;
    margin-bottom: 2rem;
  }

  .loading-indicator {
    font-size: 1.2rem;
    color: #666;
  }

  .app-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
  }

  .content-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
    height: calc(100% - 36px); /* Subtract status bar height */
  }

  .content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    border-bottom: 1px solid #e0e0e0;
    background-color: #f9f9f9;
  }

  .content-header h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  .user-controls {
    display: flex;
    align-items: center;
  }

  .logout-button {
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .logout-button:hover {
    background-color: #d32f2f;
  }

  .tab-content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
  }

  /* Login screen */
  .login-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    background-color: #f5f5f5;
  }

  .login-container {
    width: 100%;
    max-width: 400px;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: white;
  }

  .login-container h2 {
    margin-top: 0;
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .input-box {
    margin-bottom: 1.5rem;
    width: 100%;
  }

  .input-box label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .input-box input {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
  }

  .input-box input:focus {
    border-color: #0066cc;
    outline: none;
    box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2);
  }

  .btn {
    cursor: pointer;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    background-color: #0066cc;
    color: white;
    font-weight: 600;
    transition: background-color 0.2s;
  }

  .btn:hover {
    background-color: #0055aa;
  }

  .btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .login-btn {
    width: 100%;
  }

  .auth-message {
    margin-bottom: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    text-align: center;
  }

  .error {
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #ffcdd2;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .content-layout {
      flex-direction: column;
    }

    .content-header {
      padding: 0.75rem 1rem;
    }

    .tab-content {
      padding: 1rem;
    }
  }
</style>
