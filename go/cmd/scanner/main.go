package main

import (
	"flag"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/sirupsen/logrus"
	"github.com/trustdan/ibkr-trader/go/pkg/proto"
	"github.com/trustdan/ibkr-trader/go/pkg/scanner"
	"google.golang.org/grpc"
)

func main() {
	// Parse command line flags
	configPath := flag.String("config", "config.json", "Path to configuration file")
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
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Wait for termination signal
	sig := <-sigChan
	logrus.Infof("Received signal %v, gracefully shutting down", sig)

	// Gracefully stop the server
	server.GracefulStop()
	logrus.Info("Server stopped")
}

