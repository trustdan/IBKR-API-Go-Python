// This file exists solely to ensure that required dependencies are included
// in the go.mod file through explicit imports.
//go:build ignore
// +build ignore

package main

import (
	// Standard library imports
	_ "context"
	_ "encoding/json"
	_ "flag"
	_ "fmt"
	_ "io"
	_ "log"
	_ "net/http"
	_ "os"
	_ "os/signal"
	_ "strings"
	_ "sync"
	_ "syscall"
	_ "time"

	// Third-party imports
	_ "github.com/patrickmn/go-cache"
	_ "github.com/prometheus/client_golang/prometheus"
	_ "github.com/prometheus/client_golang/prometheus/promhttp"
	_ "github.com/prometheus/common/expfmt"
	_ "github.com/shirou/gopsutil/cpu"
	_ "github.com/shirou/gopsutil/mem"
	_ "github.com/sirupsen/logrus"
	_ "golang.org/x/net/http2"
	_ "golang.org/x/net/trace"
	_ "google.golang.org/grpc"
	_ "google.golang.org/protobuf/proto"
	_ "gopkg.in/yaml.v3"

	// Internal imports - update these paths to match your actual project structure
	_ "github.com/trustdan/ibkr-trader/go/src/config"
	_ "github.com/trustdan/ibkr-trader/go/src/metrics"
)

// This function is never called, it's just here to prevent compiler warnings
// about unused imports
func ensureDependencies() {
	// This function is intentionally empty
}

