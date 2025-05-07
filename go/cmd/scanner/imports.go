// This file exists solely to ensure that required dependencies are included
// in the go.mod file through explicit imports.
//go:build ignore
// +build ignore

package main

import (
	// Standard library packages
	_ "expvar"
	_ "net/http/httputil"

	// Third-party packages
	_ "github.com/prometheus/common/expfmt"
	_ "golang.org/x/net/http2"
	_ "golang.org/x/net/trace"
)

// This function is never called, it's just here to prevent compiler warnings
// about unused imports
func ensureDependencies() {
	// This function is intentionally empty
}
