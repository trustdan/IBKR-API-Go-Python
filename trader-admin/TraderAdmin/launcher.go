package main

import (
	"fmt"
	"os"
	"os/exec"
	"regexp"
	goruntime "runtime"
	"strings"
	"time"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// ServiceStatus represents the status of a required service
type ServiceStatus struct {
	Name     string `json:"name"`
	Status   string `json:"status"`
	IsOK     bool   `json:"isOk"`
	Message  string `json:"message"`
	ExtraMsg string `json:"extraMsg,omitempty"`
}

// CheckRequiredServices checks if Docker, Kubernetes, and TWS are running
func (a *App) CheckRequiredServices() []ServiceStatus {
	results := []ServiceStatus{}

	// Check Docker status
	dockerStatus := ServiceStatus{
		Name:   "Docker Desktop",
		Status: "Not Running",
		IsOK:   false,
		Message: "Docker Desktop is required for TraderAdmin. Please start Docker Desktop and " +
			"ensure it's running before using this application.",
	}

	if isDockerRunning() {
		dockerStatus.Status = "Running"
		dockerStatus.IsOK = true
		dockerStatus.Message = "Docker Desktop is running properly."
	}
	results = append(results, dockerStatus)

	// Check Kubernetes status
	kubeStatus := ServiceStatus{
		Name:   "Kubernetes",
		Status: "Not Available",
		IsOK:   false,
		Message: "Kubernetes is not enabled in Docker Desktop. Please enable Kubernetes in Docker Desktop " +
			"settings for full functionality.",
	}

	if isKubernetesRunning() {
		kubeStatus.Status = "Running"
		kubeStatus.IsOK = true
		kubeStatus.Message = "Kubernetes is running properly."

		// Check if our trader stack namespace exists
		if !isNamespaceAvailable("trader-stack") {
			kubeStatus.ExtraMsg = "Warning: trader-stack namespace not found. Please deploy the trading stack with: kubectl apply -k kubernetes/base/"
		}
	}
	results = append(results, kubeStatus)

	// Check TWS/IB Gateway status
	twsStatus := ServiceStatus{
		Name:   "TWS/IB Gateway",
		Status: "Not Running",
		IsOK:   false,
		Message: "Interactive Brokers Trader Workstation or Gateway is not running. You will need to start it " +
			"before trading operations can begin.",
	}

	if isTWSRunning() {
		twsStatus.Status = "Running"
		twsStatus.IsOK = true
		twsStatus.Message = "TWS/IB Gateway is running."
	}
	results = append(results, twsStatus)

	return results
}

// ShowStatusDialog displays a modal dialog with service status information
func (a *App) ShowStatusDialog() {
	services := a.CheckRequiredServices()

	// Show warning or continue based on service status
	allOK := true
	criticalMissing := false

	for _, service := range services {
		if !service.IsOK {
			allOK = false
			if service.Name == "Docker Desktop" {
				criticalMissing = true
			}
		}
	}

	if !allOK {
		if criticalMissing {
			choice, err := runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
				Type:          runtime.QuestionDialog,
				Title:         "Critical Service Missing",
				Message:       "Docker Desktop is not running. TraderAdmin requires Docker Desktop to function properly. Continue anyway?",
				Buttons:       []string{"Continue Anyway", "Exit"},
				DefaultButton: "Exit",
				CancelButton:  "Exit",
			})

			if err != nil || choice == "Exit" {
				os.Exit(1)
			}
		} else {
			// Just show a warning for non-critical services
			_, err := runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
				Type:    runtime.WarningDialog,
				Title:   "Service Check Warning",
				Message: "One or more required services are not running. Some functionality may be limited.",
				Buttons: []string{"Continue"},
			})

			if err != nil {
				fmt.Println("Error showing dialog:", err)
			}
		}
	}
}

// Helper functions to check services

func isDockerRunning() bool {
	cmd := exec.Command("docker", "ps")
	err := cmd.Run()
	return err == nil
}

func isKubernetesRunning() bool {
	cmd := exec.Command("kubectl", "get", "nodes")
	err := cmd.Run()
	return err == nil
}

func isNamespaceAvailable(namespace string) bool {
	cmd := exec.Command("kubectl", "get", "namespace", namespace)
	err := cmd.Run()
	return err == nil
}

func isTWSRunning() bool {
	if goruntime.GOOS == "windows" {
		// For Windows, use tasklist
		cmd := exec.Command("tasklist", "/FI", "IMAGENAME eq Trader*.exe", "/FO", "CSV")
		output, err := cmd.Output()
		if err == nil && strings.Contains(string(output), "Trader") {
			return true
		}

		// Also check for IB Gateway
		cmd = exec.Command("tasklist", "/FI", "IMAGENAME eq IB*.exe", "/FO", "CSV")
		output, err = cmd.Output()
		if err == nil && strings.Contains(string(output), "IB") {
			return true
		}
	} else if goruntime.GOOS == "darwin" || goruntime.GOOS == "linux" {
		// For macOS/Linux, use ps
		cmd := exec.Command("ps", "-e")
		output, err := cmd.Output()
		if err == nil {
			outputStr := string(output)
			if regexp.MustCompile(`[Tt]rader|TWS|tws`).MatchString(outputStr) {
				return true
			}
			if regexp.MustCompile(`[Ii][Bb]|[Gg]ateway`).MatchString(outputStr) {
				return true
			}
		}
	}

	return false
}

// StartupSequenceCheck runs the service checks at app startup
func (a *App) StartupSequenceCheck() {
	// Allow UI to initialize first
	time.Sleep(500 * time.Millisecond)

	// Show the status dialog
	a.ShowStatusDialog()
}
