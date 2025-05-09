package main

// Version information
var (
	// Version is the application version
	Version = "0.0.9"

	// BuildDate is the date when the application was built
	BuildDate = "2025-05-09"

	// CommitHash is the git commit hash at build time
	CommitHash = "3c51cb7"
)

// GetVersionInfo returns a formatted version string
func GetVersionInfo() string {
	return Version
}

// GetFullVersionInfo returns detailed version information
func GetFullVersionInfo() map[string]string {
	return map[string]string{
		"version":    Version,
		"buildDate":  BuildDate,
		"commitHash": CommitHash,
	}
}
