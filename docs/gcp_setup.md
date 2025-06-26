# Google Cloud Platform (GCP) Palworld Server Setup Guide

This guide walks you through setting up a Palworld dedicated server on a Google Cloud Platform Compute Engine virtual machine (VM).

## 1. Create Firewall Rules

Before you even create the VM, it's a good practice to set up your firewall rules. Palworld requires UDP port 8211 to be open for players to connect. It's also a good idea to open TCP port 8211.

These rules use a "target tag" (`palworld-server`) to ensure they only apply to your Palworld VM.

```bash
# Allow UDP traffic on port 8211
gcloud compute firewall-rules create palworld-server-udp \
    --network=default \
    --action=allow \
    --direction=INGRESS \
    --rules=udp:8211 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=palworld-server \
    --project="rapid-league-461312-a4"

# Allow TCP traffic on port 8211 (optional but recommended)
gcloud compute firewall-rules create palworld-server-tcp \
    --network=default \
    --action=allow \
    --direction=INGRESS \
    --rules=tcp:8211 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=palworld-server \
    --project="rapid-league-461312-a4"
```

## 2. Create and Connect to the VM

1.  Create a new Compute Engine VM instance in the GCP Console or using the `gcloud` CLI. A standard e2-medium instance is a good starting point.
2.  Once created, connect to it using SSH. Replace `YOUR_ZONE` and `YOUR_VM_NAME` with your actual VM details.

    ```bash
    gcloud compute ssh --zone "YOUR_ZONE" "YOUR_VM_NAME" --project "rapid-league-461312-a4"
    ```

## 3. Install the Server Software

Once you are connected to your VM via SSH, use the `palworld-server-launcher` to install and start the server.

```bash
# (Inside the VM)
palworld-server-launcher install --start
```

You can check the status to make sure it's running:

```bash
# (Inside the VM)
palworld-server-launcher status
```
You should see `Active: active (running)`.

## 4. Add the Network Tag to the VM

This is the most critical step. You must "tag" your VM with the `palworld-server` tag so that the firewall rules you created in Step 1 apply to it.

Run this command from your **local machine's terminal** (not inside the VM).

```bash
gcloud compute instances add-tags YOUR_VM_NAME \
  --zone=YOUR_ZONE \
  --project="rapid-league-461312-a4" \
  --tags=palworld-server
```

## 5. Get the Public IP and Connect to the Game

Your server is now running and accessible from the internet. Get its public IP address using this command on your **local machine**:

```bash
gcloud compute instances describe YOUR_VM_NAME \
  --zone=YOUR_ZONE \
  --project="rapid-league-461312-a4" \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Open Palworld, choose "Join Multiplayer Game", and enter the IP address followed by `:8211` at the bottom of the screen.

Example: `34.123.45.67:8211`

Enjoy your server! 