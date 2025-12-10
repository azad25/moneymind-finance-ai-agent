# Sandbox MCP - Secure code execution environment
# Built from https://github.com/pottekkat/sandbox-mcp

FROM golang:1.24-alpine AS builder

# Install git and build dependencies
RUN apk add --no-cache git

# Clone and build sandbox-mcp
WORKDIR /build
RUN git clone https://github.com/pottekkat/sandbox-mcp.git .
RUN go build -o /sandbox-mcp ./cmd/sandbox-mcp

# Runtime image with Docker and Python for HTTP wrapper
FROM docker:dind

# Install dependencies
RUN apk add --no-cache curl bash python3 py3-pip

# Copy the sandbox-mcp binary
COPY --from=builder /sandbox-mcp /usr/local/bin/sandbox-mcp

# Create config directory
RUN mkdir -p /root/.config/sandbox-mcp

# Copy the HTTP wrapper script
COPY http_wrapper.py /app/http_wrapper.py

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose HTTP port for API access
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the services
ENTRYPOINT ["/app/start.sh"]
