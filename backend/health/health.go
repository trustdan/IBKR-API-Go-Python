package health

import (
	"encoding/json"
	"net/http"
	"time"
)

// HealthStatus represents the health status response
type HealthStatus struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Version   string    `json:"version"`
}

// Handler returns a simple health check handler function
func Handler(version string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		status := HealthStatus{
			Status:    "ok",
			Timestamp: time.Now(),
			Version:   version,
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(status)
	}
}
