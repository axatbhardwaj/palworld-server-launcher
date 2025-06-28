# Palworld Server Launcher

A simple command-line tool to help you install, manage, and run a dedicated Palworld server on Linux. This tool automates the setup process, including installing dependencies, configuring the server as a systemd service, and setting up permissions for easy management.

## Features

- **Automated Installation**: Installs SteamCMD and the Palworld dedicated server with a single command.
- **Package Manager Repair**: Automatically attempts to fix common `apt` and `dpkg` issues before installation.
- **Service Management**: Creates a `systemd` service to run the server in the background and start it on boot.
- **Permission Handling**: Configures Polkit rules to allow server management (start, stop, restart) without needing `sudo`.
- **Unattended Setup**: Automatically accepts the SteamCMD license agreement for a smoother setup process.

## Prerequisites

- An Ubuntu Linux distribution.
- `sudo` privileges for the user running the script.

## Installation

```bash
pip install palworld-server-launcher
```

## Usage

After installation, you can use the `palworld-server-launcher` command:

### Install the Server

This command will install the server, configure it with the specified port and player count, and set it up as a systemd service.

```bash
# Install the server with default settings (port 8211, 32 players)
palworld-server-launcher install

# Install with custom settings and start the server immediately
palworld-server-launcher install --port 8211 --players 16 --start
```

### Manage the Server

Once installed, you can control the server state. Thanks to the Polkit setup, you do not need `sudo` for these commands.

```bash
# Start the server
palworld-server-launcher start

# Stop the server
palworld-server-launcher stop

# Restart the server
palworld-server-launcher restart

# Check the server's status
palworld-server-launcher status

# Enable the server to start automatically on boot
palworld-server-launcher enable

# Disable the server from starting on boot
palworld-server-launcher disable

### Update the Server
palworld-server-launcher update
```