#!/bin/bash

# Check if steamcmd is installed
if ! command -v steamcmd &> /dev/null; then
    echo "steamcmd not found. Installing steamcmd..."
    sudo add-apt-repository multiverse -y
    sudo dpkg --add-architecture i386
    sudo apt update
    sudo apt install steamcmd -y
else
    echo "steamcmd is already installed."
fi

# Install Applications with SteamCMD
echo "Installing applications with SteamCMD..."
steamcmd +login anonymous +app_update 2394010 validate +quit
steamcmd +login anonymous +app_update 1007 validate +quit

# Fix Steam SDK Errors
echo "Creating directory and copying steamclient.so..."
mkdir -p ~/.steam/sdk64/
cp ~/Steam/steamapps/common/Steamworks\ SDK\ Redist/linux64/steamclient.so ~/.steam/sdk64/

# Start the Pal Server
echo "Starting Pal Server..."
./PalServer.sh -useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS port=8211 players=32

# Create a Service for Pal Server
echo "Creating Pal Server service..."
SERVICE_FILE=/etc/systemd/system/palserver.service
cat << EOF | sudo tee $SERVICE_FILE
[Unit]
Description=Pal Server
After=network.target

[Service]
User=$USER
Group=$USER
Type=simple
ExecStart=/home/$USER/Steam/steamapps/common/PalServer/PalServer.sh -useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS port=8211 players=32
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable palserver.service
sudo systemctl start palserver.service

# Allow User to Control palworld.service Without Sudo
echo "Setting up policy for non-sudo control..."
POLICY_FILE=/etc/polkit-1/localauthority/50-local.d/palworld-service-control.pkla
cat << EOF | sudo tee $POLICY_FILE
[Allow $USER control of palworld.service]
Identity=unix-user:$USER
Action=org.freedesktop.systemd1.manage-units
ResultActive=yes
ResultInactive=yes
ResultAny=yes
EOF

sudo systemctl restart polkit.service

echo "Setup complete!"