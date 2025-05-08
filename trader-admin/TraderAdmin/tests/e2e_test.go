package tests

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/docker/docker/client"
)

// This is a simple end-to-end test for the TraderAdmin app
// In a real implementation, you would use a testing framework like godog

func TestEndToEnd(t *testing.T) {
	// Initialize Docker client
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		t.Fatalf("Failed to initialize Docker client: %v", err)
	}
	defer cli.Close()

	ctx := context.Background()

	// Step 1: Check if trader containers exist
	containers, err := cli.ContainerList(ctx, containerListOpts())
	if err != nil {
		t.Fatalf("Failed to get trader containers: %v", err)
	}

	if len(containers) == 0 {
		t.Skip("No trader containers found. Skipping test.")
	}

	// Step 2: Create temp config file
	configDir := filepath.Join(os.TempDir(), "trader-test")
	if err := os.MkdirAll(configDir, 0755); err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	defer os.RemoveAll(configDir)

	configPath := filepath.Join(configDir, "config.toml")
	sampleConfig := createSampleConfig()

	// Marshal the config to TOML
	f, err := os.Create(configPath)
	if err != nil {
		t.Fatalf("Failed to create config file: %v", err)
	}
	if err := toml.NewEncoder(f).Encode(sampleConfig); err != nil {
		f.Close()
		t.Fatalf("Failed to encode config: %v", err)
	}
	f.Close()

	// Step 3: Pause containers
	t.Log("Pausing containers...")
	for _, c := range containers {
		if err := cli.ContainerPause(ctx, c.ID); err != nil {
			t.Fatalf("Failed to pause container %s: %v", c.ID, err)
		}
	}

	// Step 4: Modify config (change risk_per_trade to 0.03)
	t.Log("Modifying config...")
	sampleConfig.Trading.RiskPerTrade = 0.03

	f, err = os.Create(configPath)
	if err != nil {
		t.Fatalf("Failed to create config file: %v", err)
	}
	if err := toml.NewEncoder(f).Encode(sampleConfig); err != nil {
		f.Close()
		t.Fatalf("Failed to encode config: %v", err)
	}
	f.Close()

	// Step 5: Unpause containers
	t.Log("Unpausing containers...")
	for _, c := range containers {
		if err := cli.ContainerUnpause(ctx, c.ID); err != nil {
			t.Fatalf("Failed to unpause container %s: %v", c.ID, err)
		}
	}

	// Step 6: Send SIGUSR1 signal to reload config
	t.Log("Sending SIGUSR1 signal...")
	for _, c := range containers {
		if err := cli.ContainerKill(ctx, c.ID, "SIGUSR1"); err != nil {
			t.Fatalf("Failed to send SIGUSR1 to container %s: %v", c.ID, err)
		}
	}

	// Step 7: Verify containers are still running
	time.Sleep(1 * time.Second) // Give containers time to process the signal

	for _, c := range containers {
		info, err := cli.ContainerInspect(ctx, c.ID)
		if err != nil {
			t.Fatalf("Failed to inspect container %s: %v", c.ID, err)
		}

		if !info.State.Running {
			t.Errorf("Container %s should be running but it's not", c.ID)
		}
	}

	t.Log("Test completed successfully")
}

// Helper function to create container list options for consistency
func containerListOpts() interface{} {
	// Implementation-agnostic container listing that will work with any Docker API version
	// This avoids the specific type errors when Docker API versions change
	return struct {
		All     bool
		Filters map[string][]string
	}{
		All: true,
		Filters: map[string][]string{
			"label": {"app=ibkr-trader"},
		},
	}
}

// SampleConfig represents a simple test configuration
type SampleConfig struct {
	IBKR    IBKRConfig
	Trading TradingConfig
}

type IBKRConfig struct {
	Host     string `toml:"host"`
	Port     int    `toml:"port"`
	ClientID int    `toml:"client_id"`
}

type TradingConfig struct {
	Mode         string  `toml:"mode"`
	MaxPositions int     `toml:"max_positions"`
	RiskPerTrade float64 `toml:"risk_per_trade"`
	AllowLateDay bool    `toml:"allow_late_day_entry"`
}

func createSampleConfig() *SampleConfig {
	return &SampleConfig{
		IBKR: IBKRConfig{
			Host:     "127.0.0.1",
			Port:     7497,
			ClientID: 1,
		},
		Trading: TradingConfig{
			Mode:         "PAPER",
			MaxPositions: 5,
			RiskPerTrade: 0.02,
			AllowLateDay: true,
		},
	}
}
