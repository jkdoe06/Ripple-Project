# Autonomous Life Agent — Docker Sandbox
# Run OpenClaw in an isolated container for safety

FROM node:24-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    curl jq git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (security: never run as root)
RUN useradd -m -s /bin/bash agent
USER agent
WORKDIR /home/agent/app

# Install OpenClaw
RUN npm install -g openclaw@latest

# Install Python dependencies
COPY --chown=agent:agent requirements.txt .
RUN python3 -m pip install --user --break-system-packages -r requirements.txt

# Copy project files
COPY --chown=agent:agent . .

# Expose gateway port (localhost only by default)
EXPOSE 18789

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:18789/health || exit 1

# Start OpenClaw gateway
CMD ["openclaw", "gateway", "--port", "18789", "--verbose"]
