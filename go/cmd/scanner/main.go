package main

import (
	"flag"
	"net"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"

	"github.com/fsnotify/fsnotify"
	"github.com/sirupsen/logrus"
	"github.com/trustdan/ibkr-trader/go/pkg/proto"
	"github.com/trustdan/ibkr-trader/go/pkg/scanner"
	"google.golang.org/grpc"
)

// Define signals in an os-independent way
var shutdownSignals = []os.Signal{syscall.SIGINT, syscall.SIGTERM}

func main() {
	// Parse command line flags
	configPath := flag.String("config", "config.json", "Path to configuration file")
	tomlConfigPath := flag.String("toml-config", "/config/config.toml", "Path to TOML configuration file (shared with other services)")
	flag.Parse()

	// Load configuration
	config, err := scanner.LoadConfig(*configPath)
	if err != nil {
		logrus.Fatalf("Failed to load configuration: %v", err)
	}

	// Configure logging
	setupLogging(config.LogLevel)
	logrus.Info("Starting IBKR Auto Vertical Spread Trader Scanner Service")

	// Create scanner service
	scannerService := scanner.NewScannerService(config)
	scannerService.SetConfigPath(*configPath)

	// Setup file watcher for TOML config
	setupConfigWatcher(*tomlConfigPath, scannerService)

	// Create gRPC server
	server := grpc.NewServer()
	proto.RegisterScannerServiceServer(server, scannerService)

	// Start listening
	listener, err := net.Listen("tcp", config.ServerAddress)
	if err != nil {
		logrus.Fatalf("Failed to listen on %s: %v", config.ServerAddress, err)
	}
	logrus.Infof("Server listening on %s", config.ServerAddress)

	// Handle graceful shutdown
	go handleShutdown(server)

	// Start serving
	if err := server.Serve(listener); err != nil {
		logrus.Fatalf("Failed to serve: %v", err)
	}
}

// setupConfigWatcher sets up a watcher for the TOML config file
func setupConfigWatcher(tomlConfigPath string, service *scanner.ScannerService) {
	// Make sure the path is absolute
	if !filepath.IsAbs(tomlConfigPath) {
		workDir, err := os.Getwd()
		if err != nil {
			logrus.Errorf("Failed to get working directory: %v", err)
			return
		}
		tomlConfigPath = filepath.Join(workDir, tomlConfigPath)
	}

	// Check if TOML config exists
	if _, err := os.Stat(tomlConfigPath); os.IsNotExist(err) {
		logrus.Warnf("TOML config file does not exist at %s, skipping watcher setup", tomlConfigPath)
		return
	}

	// Create new watcher
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		logrus.Errorf("Failed to create config file watcher: %v", err)
		return
	}

	// Start watching in a goroutine
	go func() {
		defer watcher.Close()

		// Throttle reloads to prevent multiple rapid reloads
		var lastReload time.Time
		const minReloadInterval = 5 * time.Second

		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Op&fsnotify.Write == fsnotify.Write {
					// Check if enough time has passed since last reload
					if time.Since(lastReload) > minReloadInterval {
						logrus.Infof("TOML config file changed: %s", event.Name)
						if err := service.ReloadConfig(); err != nil {
							logrus.Errorf("Failed to reload configuration: %v", err)
						} else {
							logrus.Info("Configuration reloaded successfully")
							lastReload = time.Now()
						}
					}
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				logrus.Errorf("Config watcher error: %v", err)
			}
		}
	}()

	// Add TOML config directory to watcher
	configDir := filepath.Dir(tomlConfigPath)
	if err := watcher.Add(configDir); err != nil {
		logrus.Errorf("Failed to watch config directory %s: %v", configDir, err)
		return
	}

	logrus.Infof("Watching TOML config file: %s", tomlConfigPath)
}

// setupLogging configures the logging level
func setupLogging(level string) {
	// Set log format
	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})

	// Set log level
	switch level {
	case "debug":
		logrus.SetLevel(logrus.DebugLevel)
	case "info":
		logrus.SetLevel(logrus.InfoLevel)
	case "warn":
		logrus.SetLevel(logrus.WarnLevel)
	case "error":
		logrus.SetLevel(logrus.ErrorLevel)
	default:
		logrus.SetLevel(logrus.InfoLevel)
	}
}

// handleShutdown handles graceful shutdown on signals
func handleShutdown(server *grpc.Server) {
	// Create channel to receive signals
	sigChan := make(chan os.Signal, 1)

	// Register for the standard termination signals
	signal.Notify(sigChan, shutdownSignals...)

	// Wait for termination signal
	sig := <-sigChan
	logrus.Infof("Received signal %v", sig)

	logrus.Info("Gracefully shutting down")
	// Gracefully stop the server
	server.GracefulStop()
	logrus.Info("Server stopped")
}
