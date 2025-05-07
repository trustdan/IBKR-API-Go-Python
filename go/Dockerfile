# Accept Go version as build argument, defaulting to 1.23
ARG GO_VERSION=1.23

FROM golang:${GO_VERSION}-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Copy Go modules files
COPY go.mod go.sum* ./

# Retry mechanism for go mod download to handle transient network issues
RUN --mount=type=cache,target=/go/pkg/mod \
    for i in 1 2 3; do \
        go mod download && break || sleep 5; \
    done

# Copy the source code
COPY . .

# Build the binary with optimizations
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -ldflags="-s -w" -o /scanner ./cmd/scanner

# Use a minimal alpine image for the final container
FROM alpine:3.17

WORKDIR /root/

# Copy the binary from the builder stage
COPY --from=builder /scanner /usr/local/bin/

# Copy config file
COPY config.json /root/config.json

# Create config directory and expose ports
RUN mkdir -p /etc/scanner
EXPOSE 50051
EXPOSE 2112

# Run the binary
ENTRYPOINT ["scanner"]
