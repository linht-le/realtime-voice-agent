#!/bin/bash

set -e

# Load environment variables
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

source .env

if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "Error: NGROK_AUTHTOKEN not found in .env"
    exit 1
fi

# Install ngrok if not present
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update && sudo apt install -y ngrok
fi

# Configure authtoken
echo "Configuring ngrok authtoken..."
ngrok config add-authtoken $NGROK_AUTHTOKEN

echo "Creating systemd service..."
sudo tee /etc/systemd/system/ngrok.service > /dev/null <<EOF
[Unit]
Description=ngrok
After=network.target

[Service]
ExecStart=/usr/local/bin/ngrok http 8000 --log=stdout
Restart=always
User=$USER
WorkingDirectory=$PWD

[Install]
WantedBy=multi-user.target
EOF

echo "Starting ngrok service..."
sudo systemctl daemon-reload
sudo systemctl enable ngrok
sudo systemctl start ngrok

echo "Waiting for ngrok to start..."
sleep 5

echo "Public URL:"
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
