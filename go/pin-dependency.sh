#!/bin/bash

# This script pins the tklauser/go-sysconf dependency to a version compatible with Go 1.21
cd "$(dirname "$0")"

# Update the go.mod file to use an older compatible version
go mod edit -replace github.com/tklauser/go-sysconf=github.com/tklauser/go-sysconf@v0.3.11

# Tidy up the go.mod file
go mod tidy -go=1.21

echo "Successfully pinned github.com/tklauser/go-sysconf to v0.3.11"

