#!/bin/bash

# Ensure the script is run with sudo/root privileges
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run this script with sudo: sudo bash setup_service.sh"
  exit 1
fi

# Detect absolute path of the project and current user
PROJECT_DIR="$(pwd)"
CURRENT_USER="${SUDO_USER:-$(whoami)}"

echo "⚙️ Starting CardioQSPR DevOps Setup..."
echo "📂 Project Directory: $PROJECT_DIR"
echo "👤 System User: $CURRENT_USER"

# 1. Install headless graphics libraries for RDKit molecular drawings
echo "📦 Installing system graphics dependencies..."
apt-get update && apt-get install -y libxrender1 libxext6 libsm6 libice6

# 2. Stop any existing loose processes
echo "🛑 Cleaning up existing background processes..."
pkill -f run.py || true
pkill -f uvicorn || true
pkill -f vite || true

# 3. Create the Systemd service dynamically
echo "✍️ Writing Systemd service configuration..."
cat <<EOF > /etc/systemd/system/cardio.service
[Unit]
Description=CardioQSPR Platform Service
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 4. Reload, Enable and Start the service
echo "🚀 Starting CardioQSPR service..."
systemctl daemon-reload
systemctl enable cardio
systemctl restart cardio

echo ""
echo "✅ CardioQSPR is now running as a background service!"
echo "--------------------------------------------------------"
echo "ℹ️ How to manage the service:"
echo "👉 View active status:      sudo systemctl status cardio"
echo "👉 View real-time logs:     journalctl -u cardio -f"
echo "👉 Restart the platform:    sudo systemctl restart cardio"
echo "👉 Stop the platform:       sudo systemctl stop cardio"
echo "--------------------------------------------------------"
