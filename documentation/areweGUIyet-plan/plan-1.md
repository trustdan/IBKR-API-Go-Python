### Revised Plan 1: Foundation & Backend Setup

**Timeline:** 1 week

**Preamble:** This foundational phase focuses on establishing the core project structure, development environment, and essential backend services within the existing Git repository. We will prioritize a clean setup, centralized configuration, and mechanisms for dynamic updates. Git submodules will not be used. The directory structure will follow standard practices to avoid unnecessary nesting.

**Core Goals:**

1.  Initialize the Wails/Svelte-TS project scaffold (`TraderAdmin` directory) with a Go backend inside the current repository.
2.  Establish a Docker and Kubernetes-based runtime environment (initially for a single-node setup).
3.  Centralize all tunable parameters and configurations into a single `config.toml` file.
4.  Implement illustrative live-reload mechanisms for both Python and Go services to respond to configuration changes.

------

#### 1.1 Project & Dependency Initialization

* **Scaffold Wails Application:**
    This command initializes the main application structure within the current directory.
    ```bash
    wails init -n TraderAdmin -t svelte-ts
    cd TraderAdmin
    ```
    *Note: This creates a `TraderAdmin` subdirectory. All subsequent work specific to the GUI and its backend will be within this directory.*

* **Create Feature Branch:**
    Create a dedicated branch for this phase's work within the existing repository.
    ```bash
    # Assuming you are now inside the TraderAdmin directory
    git checkout -b feature/phase1-foundation-setup
    ```

* **Add Core Go Modules:**
    Include necessary Go libraries for backend functionality.

    ```go
    // In your go.mod file (likely TraderAdmin/go.mod or TraderAdmin/backend/go.mod)
    require (
      [github.com/wailsapp/wails/v2](https://github.com/wailsapp/wails/v2) v2.x.x // Replace with the latest stable version
      [github.com/docker/docker/client](https://github.com/docker/docker/client) v25.x.x // Replace with a recent stable version
      k8s.io/client-go v0.2x.x // Replace with a version compatible with your K8s
      [github.com/BurntSushi/toml](https://github.com/BurntSushi/toml) v1.x.x // Replace with a recent stable version
      [github.com/fsnotify/fsnotify](https://github.com/fsnotify/fsnotify) v1.x.x // For live config reload in Go
    )
    ```

* **Python Orchestrator Dependencies:**
    Install necessary Python packages (assuming the orchestrator lives outside the `TraderAdmin` Wails structure but within the same repo, or adjust path accordingly).
    ```bash
    # In your Python environment/requirements.txt
    # pip install toml python-dotenv # Basic config and env var handling
    # pip install grpcio grpcio-tools # If using gRPC
    # pip install kubernetes # If Python orchestrator interacts with K8s API
    ```
    *(Adjust Python dependencies based on the orchestrator's specific needs.)*

------

#### 1.2 Configuration File Consolidation

* **Create Central Configuration File:**
    Establish `TraderAdmin/config/config.toml` (or a similar clear path within the `TraderAdmin` structure). This file will house all adjustable parameters for the GUI and its related services.
    *Example Structure for `TraderAdmin/config/config.toml`:*

    ```toml
    [general]
    log_level = "INFO"

    [ibkr_connection]
    host = "localhost"
    port = 7497
    client_id_trading = 1
    client_id_data = 2 # If using a separate data connection
    account_code = "YOUR_ACCOUNT_ID" # Or retrieve from env var
    read_only_api = false

    [trading_parameters]
    global_max_concurrent_positions = 10
    default_risk_per_trade_percentage = 1.0
    emergency_stop_loss_percentage = 5.0 # Global portfolio level

    [strategy_defaults.my_rsi_strategy]
    enabled = true
    min_rsi_value = 30
    max_rsi_value = 70
    atr_period_for_stop = 14
    atr_multiplier_for_stop = 2.5

    # ... other strategies, data source settings, alert configurations, scheduling parameters etc.
    ```

* **Git Ignore Configuration:**
    Ensure local configurations and build artifacts within `TraderAdmin` are ignored. Add these lines to the *root* `.gitignore` file of your existing repository:

    ```gitignore
    # Ignore local configuration files within TraderAdmin
    TraderAdmin/config/config.toml
    TraderAdmin/*.local.toml

    # Wails build artifacts within TraderAdmin
    TraderAdmin/build/bin/
    TraderAdmin/build/darwin/
    TraderAdmin/build/windows/
    TraderAdmin/build/linux/

    # Node modules within TraderAdmin frontend
    TraderAdmin/frontend/node_modules/
    ```
    *(Adjust paths if your structure differs slightly)*

* **Configuration Backup Mechanism (Conceptual):**
    Implement a simple backup on save if changes are made directly to a primary `config.toml`.
    *Pseudocode for backend service on config update:*
    ```
    function handle_config_save(new_config_content):
        if primary_config_file_exists:
            copy primary_config_file to primary_config_file_backup
        write new_config_content to primary_config_file
        trigger_config_reload_in_services()
    ```

------

#### 1.3 Docker & Kubernetes Runtime Setup

1.  **Prerequisite: Docker Desktop with Kubernetes Enabled:**
    Ensure your local development environment is prepared.

2.  **PersistentVolumeClaim (PVC) for Configuration:**
    To persist `config.toml` across pod restarts. Create `TraderAdmin/deploy/config-pvc.yaml`:

    ```yaml
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: traderadmin-config-pvc
    spec:
      accessModes:
        - ReadWriteOnce # Suitable for a single node or if only one pod writes
      resources:
        requests:
          storage: 100Mi # Small size, as it's just for config files
    ```

3.  **Kubernetes Deployments (Illustrative):**
    Define deployments for your backend services. Mount the PVC to access the configuration.
    *Example `TraderAdmin/deploy/orchestrator-deployment.yaml` snippet:*

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: orchestrator-deployment # Or traderadmin-orchestrator-deployment
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: orchestrator # Or traderadmin-orchestrator
      template:
        metadata:
          labels:
            app: orchestrator # Or traderadmin-orchestrator
        spec:
          volumes:
            - name: app-config
              persistentVolumeClaim:
                claimName: traderadmin-config-pvc
          containers:
            - name: orchestrator-container
              # Image likely built from code outside TraderAdmin dir, but uses its config
              image: your-repo/orchestrator-image:latest
              ports:
                - containerPort: 8080 # Example port
              volumeMounts:
                - name: app-config
                  # Mount point inside the container where the service expects config
                  mountPath: /app/config
                  readOnly: true
    ```
    *(Define similar deployments for other services like the Go scanner, ensuring consistent naming and volume mounts.)*

4.  **Host Networking (Optional Consideration):**
    Use `hostNetwork: true` in the pod spec only if absolutely necessary for direct host network access (e.g., IBKR).

------

#### 1.4 Live-Reload Handlers (Illustrative Examples)

* **Python Orchestrator (Conceptual Example using `watchdog`):**
    (Code example remains the same, ensure `CONFIG_PATH` points to the mounted volume path, e.g., `/app/config/config.toml`)

* **Go Service (Conceptual Example using `fsnotify`):**
    (Code example remains the same, ensure `ConfigPath` points to the mounted volume path, e.g., `/app/config/config.toml`, and watch the directory `/app/config/`)

------

#### 1.5 Validation & Smoke Tests (Behavior Defined with Gherkin)

```gherkin
Feature: Phase 1 Foundation and Backend Setup Validation

  Scenario: Successful Project Initialization and Structure within Existing Repo
    Given an existing Git repository
    When the command `wails init -n TraderAdmin -t svelte-ts` is executed
    And I navigate into the newly created "TraderAdmin" directory
    And I create a new git branch named "feature/phase1-foundation-setup"
    Then a "TraderAdmin" directory exists with standard Wails Svelte-TS project files
    And a "go.mod" file exists within the "TraderAdmin" structure (e.g., TraderAdmin/go.mod)
    And the current active git branch is "feature/phase1-foundation-setup"
    And no git submodules have been added to the repository

  Scenario: Kubernetes Cluster and PVC Setup
    Given Docker Desktop is running with Kubernetes enabled
    When I apply the `TraderAdmin/deploy/config-pvc.yaml` manifest
    Then a PersistentVolumeClaim named "traderadmin-config-pvc" is successfully created in the Kubernetes cluster
    And its status is "Bound"

  Scenario: Backend Service Deployment with Config Volume
    Given the "traderadmin-config-pvc" is "Bound"
    And a Docker image "your-repo/orchestrator-image:latest" is available
    And a `config.toml` file is present on the host path mapped to the PVC or initialized via an init container
    When I apply the `TraderAdmin/deploy/orchestrator-deployment.yaml` manifest
    Then a Deployment named "orchestrator-deployment" (or similar) is created
    And a Pod for the orchestrator service enters the "Running" state
    And the orchestrator Pod has the "app-config" volume mounted to "/app/config"

  Scenario: Configuration File Hot-Reload in Python Orchestrator
    Given the Python orchestrator service is running in Kubernetes
    And it is configured to watch "/app/config/config.toml" for changes
    When the content of the config file on the PVC (mounted at "/app/config/config.toml") is updated
    Then the Python orchestrator service detects the change
    And logs a message indicating that the configuration has been reloaded
    And the service starts operating with the new configuration values

  Scenario: Configuration File Hot-Reload in Go Service
    Given the Go backend service (e.g., scanner) is running in Kubernetes
    And it is configured to watch "/app/config/config.toml" for changes
    When the content of the config file on the PVC (mounted at "/app/config/config.toml") is updated
    Then the Go service detects the change
    And logs a message indicating that the configuration has been reloaded
    And the service starts operating with the new configuration values
