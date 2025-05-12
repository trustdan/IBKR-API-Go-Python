### Plan 1: Foundation & Backend Setup

**Timeline:** 1 week
 **Core Goals:**

1. Spin up the Wails/Svelte-TS project scaffold with Go backend.
2. Establish Docker- and Kubernetes-based runtime (single-node).
3. Centralize every Ã¢â‚¬Å“tunabilityÃ¢â‚¬Â into a single `config.toml`.
4. Wire live-reload hooks in both services (Python and Go).

------

#### 1.1 Project & Dependency Initialization

- **Scaffold Wails app**

  ```bash
  wails init -n TraderAdmin -t svelte-ts
  cd TraderAdmin
  git init && git checkout -b feature/backend-setup
  ```

- **Add Go modules**

  ```go
  require (
    github.com/wailsapp/wails/v2 v2.x.x
    github.com/docker/docker/client v25.6.0
    k8s.io/client-go v0.26.0
    github.com/BurntSushi/toml v0.4.1
  )
  ```

- **Python orchestrator proto setup** (if using gRPC)

  ```bash
  pip install tomli grpcio-tools
  ```

------

#### 1.2 Configuration File Consolidation

- Create `config/config.toml` with **all** parameters from `models.ts` and your strategy docs:

  ```toml
  [ibkr]
  host = "localhost"
  port = 7497
  client_id = 0
  read_only = false

  [trading]
  mode = "PAPER"             # or LIVE
  max_positions = 5
  risk_per_trade_pct = 1.0

  [strategies.high_base]
  min_rsi = 50.0
  max_atr_ratio = 1.2

  # Ã¢â‚¬Â¦and so on for each strategy, option, cache, schedule, alert, etc.
  ```

- **Git-ignore**:

  ```
  /config/*.toml
  ```

- **Backup**: Copy `config.toml` Ã¢â€ â€™ `config.toml.bak` on each Save.

------

#### 1.3 Docker & Kubernetes Runtime

1. **Docker Desktop**

   - Enable Kubernetes in Docker settings.

2. **PersistentVolumeClaim** (e.g. `deploy/config-pvc.yaml`):

   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata: { name: trader-config }
   spec:
     accessModes: [ReadWriteOnce]
     resources: { requests: { storage: 100Mi } }
   ```

3. **Deployments** mount the PVC:

   ```yaml
   volumes:
     - name: cfg
       persistentVolumeClaim:
         claimName: trader-config

   containers:
     - name: orchestrator
       image: myrepo/orchestrator:latest
       volumeMounts: [{ name: cfg, mountPath: /config, readOnly: true }]
     - name: go-scanner
       image: myrepo/scanner:latest
       volumeMounts: [{ name: cfg, mountPath: /config, readOnly: true }]
   ```

4. **Host networking** (optional):

   ```yaml
   spec:
     hostNetwork: true
   ```

------

#### 1.4 Live-Reload Handlers

- **Python Orchestrator** (`orchestrator.py`):

  ```python
  import signal, tomli, threading, pathlib

  CFG = pathlib.Path("/config/config.toml")
  cfg_lock = threading.Lock()
  config = tomli.loads(CFG.read_text())

  def reload_cfg(signum, frame):
      with cfg_lock:
          config.update(tomli.loads(CFG.read_text()))
          print("Config reloaded")

  signal.signal(signal.SIGUSR1, reload_cfg)
  ```

- **Go Scanner** (`scanner/main.go`):

  ```go
  import (
    "github.com/fsnotify/fsnotify"
    "github.com/BurntSushi/toml"
    "sync/atomic"
  )
  var cfg atomic.Value

  func watchConfig(path string) {
    watcher, _ := fsnotify.NewWatcher()
    watcher.Add(path)
    for range watcher.Events {
      var newCfg Config
      toml.DecodeFile(path, &newCfg)
      cfg.Store(newCfg)
      log.Println("Config hot-reloaded")
    }
  }
  ```

------

#### 1.5 Validation & Smoke Tests

```gherkin
Feature: Foundation Smoke Tests
  Scenario: Docker & K8s startup
    Given Docker Desktop is running with Kubernetes enabled
    When I apply all manifests in deploy/
    Then all pods (orchestrator, scanner, etc.) enter Running state

  Scenario: Config reload
    Given orchestrator and scanner are running
    When I update config/config.toml
      And send SIGUSR1 to orchestrator container
    Then each service logs Ã¢â‚¬Å“Config reloadedÃ¢â‚¬Â
```

------

#### 1.6 Deliverables

- Wails project bootstrapped
- Kubernetes manifests under `deploy/`
- A single consolidated `config.toml`
- Live-reload proof-of-concept in both services
- Passing smoke tests

------

> **Next:** Once youÃ¢â‚¬â„¢re happy with this foundation, weÃ¢â‚¬â„¢ll dive into **Plan 2: Core GUI Components**Ã¢â‚¬â€building out the tabs, dynamic forms, and container-control APIs. Let me know your feedback!
