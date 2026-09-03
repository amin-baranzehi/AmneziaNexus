#!/bin/bash

# AmneziaNexus Uninstallation Script
# Run with sudo: sudo bash uninstall.sh

echo "========================================="
echo " Starting AmneziaNexus Uninstallation..."
echo "========================================="

# 1. Stop and disable Systemd Service
echo "[1/4] Stopping and disabling amnezia-panel.service..."
systemctl stop amnezia-panel
systemctl disable amnezia-panel
rm -f /etc/systemd/system/amnezia-panel.service
systemctl daemon-reload

# 2. Remove sudoers rules
echo "[2/4] Removing sudoers configuration..."
rm -f /etc/sudoers.d/amnezia-panel

# 3. Stop active VPN and remove routing rules
echo "[3/4] Stopping active VPN connections and removing routing rules..."
if ip link show awg0 > /dev/null 2>&1; then
    awg-quick down awg0
fi
iptables -D FORWARD -o awg0 -j ACCEPT 2>/dev/null
iptables -D FORWARD -i awg0 -j ACCEPT 2>/dev/null
iptables -t nat -D POSTROUTING -o awg0 -j MASQUERADE 2>/dev/null

# Remove configuration files
rm -rf /etc/amnezia/amneziawg

# 4. Remove project directory (Optional)
echo "[4/4] Do you want to delete the project directory? (y/n)"
read -r DELETE_DIR
if [ "$DELETE_DIR" = "y" ] || [ "$DELETE_DIR" = "Y" ]; then
    PROJ_DIR=$(pwd)
    echo "Deleting $PROJ_DIR..."
    cd ..
    rm -rf "$PROJ_DIR"
fi

echo "========================================="
echo " Uninstallation Complete!"
echo "========================================="
