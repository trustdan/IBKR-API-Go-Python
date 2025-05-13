package k8s

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/fsnotify/fsnotify"
	"github.com/rs/zerolog/log"
	v1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

// ConfigWatcher watches for changes to a config file and triggers a callback
type ConfigWatcher struct {
	configPath    string
	watcher       *fsnotify.Watcher
	mu            sync.Mutex
	clientset     *kubernetes.Clientset
	namespace     string
	configMapName string
	callbacks     []func(map[string]interface{})
}

// NewConfigWatcher creates a new ConfigWatcher
func NewConfigWatcher(configPath, namespace, configMapName string) (*ConfigWatcher, error) {
	// Create fsnotify watcher
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return nil, fmt.Errorf("error creating watcher: %w", err)
	}

	// Initialize Kubernetes client
	var clientset *kubernetes.Clientset

	// Use in-cluster config if running in Kubernetes
	config, err := rest.InClusterConfig()
	if err != nil {
		// Fall back to kubeconfig file if not in cluster
		log.Info().Msg("Not running in cluster, trying kubeconfig file")
		kubeconfig := os.Getenv("KUBECONFIG")
		if kubeconfig == "" {
			kubeconfig = filepath.Join(os.Getenv("HOME"), ".kube", "config")
		}

		config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			log.Warn().Err(err).Msg("Could not build config from kubeconfig file")
			// Continue without K8s client
		}
	}

	if config != nil {
		clientset, err = kubernetes.NewForConfig(config)
		if err != nil {
			log.Warn().Err(err).Msg("Failed to create Kubernetes client")
			// Continue without K8s client
		}
	}

	return &ConfigWatcher{
		configPath:    configPath,
		watcher:       watcher,
		clientset:     clientset,
		namespace:     namespace,
		configMapName: configMapName,
		callbacks:     []func(map[string]interface{}){},
	}, nil
}

// AddCallback adds a callback function that will be called with the new config when changes occur
func (cw *ConfigWatcher) AddCallback(callback func(map[string]interface{})) {
	cw.mu.Lock()
	defer cw.mu.Unlock()
	cw.callbacks = append(cw.callbacks, callback)
}

// Start begins watching the config file for changes
func (cw *ConfigWatcher) Start(ctx context.Context) error {
	// Get the config directory to watch
	configDir := filepath.Dir(cw.configPath)

	// Ensure the directory exists
	if _, err := os.Stat(configDir); os.IsNotExist(err) {
		log.Error().Str("path", configDir).Msg("Config directory does not exist")
		return fmt.Errorf("config directory does not exist: %w", err)
	}

	// Watch the config directory
	if err := cw.watcher.Add(configDir); err != nil {
		return fmt.Errorf("error watching directory: %w", err)
	}

	log.Info().Str("path", configDir).Msg("Started watching config directory")

	// Load the initial config
	if err := cw.loadAndNotify(); err != nil {
		log.Warn().Err(err).Msg("Failed to load initial config")
	}

	// Watch for changes
	go func() {
		for {
			select {
			case <-ctx.Done():
				cw.watcher.Close()
				return

			case event, ok := <-cw.watcher.Events:
				if !ok {
					return
				}

				// Only care about the specific config file
				if filepath.Base(event.Name) != filepath.Base(cw.configPath) {
					continue
				}

				if event.Op&fsnotify.Write == fsnotify.Write || event.Op&fsnotify.Create == fsnotify.Create {
					log.Info().Str("file", event.Name).Msg("Config file changed")

					// Small delay to ensure the file is completely written
					time.Sleep(100 * time.Millisecond)

					if err := cw.loadAndNotify(); err != nil {
						log.Error().Err(err).Msg("Failed to reload config")
					}
				}

			case err, ok := <-cw.watcher.Errors:
				if !ok {
					return
				}
				log.Error().Err(err).Msg("Watcher error")
			}
		}
	}()

	return nil
}

// loadAndNotify loads the config file and notifies all callbacks
func (cw *ConfigWatcher) loadAndNotify() error {
	// Read config file
	config, err := cw.loadConfig()
	if err != nil {
		return err
	}

	// Update Kubernetes ConfigMap if available
	if cw.clientset != nil {
		if err := cw.updateConfigMap(config); err != nil {
			log.Error().Err(err).Msg("Failed to update ConfigMap")
		}
	}

	// Notify all callbacks
	cw.mu.Lock()
	defer cw.mu.Unlock()
	for _, callback := range cw.callbacks {
		callback(config)
	}

	return nil
}

// loadConfig loads the config file and returns the parsed content
func (cw *ConfigWatcher) loadConfig() (map[string]interface{}, error) {
	var config map[string]interface{}

	if _, err := os.Stat(cw.configPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("config file does not exist: %w", err)
	}

	if _, err := toml.DecodeFile(cw.configPath, &config); err != nil {
		return nil, fmt.Errorf("error decoding config: %w", err)
	}

	log.Info().Str("path", cw.configPath).Msg("Config loaded successfully")
	return config, nil
}

// updateConfigMap updates a Kubernetes ConfigMap with the current config
func (cw *ConfigWatcher) updateConfigMap(config map[string]interface{}) error {
	if cw.clientset == nil {
		return fmt.Errorf("Kubernetes client is not available")
	}

	// Read the config file contents
	fileContent, err := os.ReadFile(cw.configPath)
	if err != nil {
		return fmt.Errorf("error reading config file: %w", err)
	}

	// Check if the ConfigMap exists
	cmClient := cw.clientset.CoreV1().ConfigMaps(cw.namespace)
	cm, err := cmClient.Get(context.Background(), cw.configMapName, metav1.GetOptions{})

	if err != nil {
		// Create the ConfigMap if it doesn't exist
		cm = &v1.ConfigMap{
			ObjectMeta: metav1.ObjectMeta{
				Name: cw.configMapName,
			},
			Data: map[string]string{
				"config.toml": string(fileContent),
			},
		}
		_, err = cmClient.Create(context.Background(), cm, metav1.CreateOptions{})
		if err != nil {
			return fmt.Errorf("error creating ConfigMap: %w", err)
		}
		log.Info().Msg("Created ConfigMap with config data")
	} else {
		// Update the existing ConfigMap
		if cm.Data == nil {
			cm.Data = make(map[string]string)
		}
		cm.Data["config.toml"] = string(fileContent)
		_, err = cmClient.Update(context.Background(), cm, metav1.UpdateOptions{})
		if err != nil {
			return fmt.Errorf("error updating ConfigMap: %w", err)
		}
		log.Info().Msg("Updated ConfigMap with new config data")
	}

	return nil
}

// Stop stops the config watcher
func (cw *ConfigWatcher) Stop() {
	if cw.watcher != nil {
		cw.watcher.Close()
	}
}
