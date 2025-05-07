FROM golang:1.20-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Copy Go modules files
COPY go.mod go.sum* ./

# Download dependencies
RUN go mod download

# Copy the source code
COPY . .

# Build the binary with optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -ldflags="-s -w" -o /scanner ./cmd/scanner

# Use a minimal alpine image for the final container
FROM alpine:3.17

WORKDIR /root/

# Copy the binary from the builder stage
COPY --from=builder /scanner /usr/local/bin/

# Create config directory and expose ports
RUN mkdir -p /etc/scanner
EXPOSE 50051
EXPOSE 2112

# Run the binary
ENTRYPOINT ["scanner"]
