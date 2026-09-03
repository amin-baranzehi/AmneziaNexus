#!/bin/bash

# AmneziaNexus Auto-Installation Script for Armbian / Ubuntu / Debian (x86_64 & ARM64)
# Run with sudo: sudo bash install.sh

set -e

echo "========================================="
echo " Starting AmneziaNexus Installation..."
echo "========================================="

# 1. Update and install dependencies
echo "[1/6] Installing system dependencies..."
apt-get update
apt-get install -y software-properties-common python3-venv python3-pip iptables wireguard-tools sudo curl build-essential gnupg2 ca-certificates

# Install AmneziaWG if not already installed
if ! command -v awg-quick &> /dev/null; then
    echo "Installing AmneziaWG tools..."
    
    # Detect distribution
    DISTRO_ID="unknown"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
    fi

    if [ "$DISTRO_ID" = "ubuntu" ]; then
        add-apt-repository -y ppa:amnezia/ppa || true
    else
        # Debian / Armbian (Bookworm/Bullseye)
        echo "Configuring Amnezia PPA repository for Debian..."
        mkdir -p /etc/apt/keyrings
        curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x57290828" | gpg --dearmor -o /etc/apt/keyrings/amnezia.gpg --yes 2>/dev/null || true
        echo "deb [signed-by=/etc/apt/keyrings/amnezia.gpg] https://ppa.launchpadcontent.net/amnezia/ppa/ubuntu jammy main" > /etc/apt/sources.list.d/amnezia.list
    fi

    apt-get update
    # Install kernel headers if available (needed for DKMS on ARM64)
    apt-get install -y linux-headers-$(uname -r) 2>/dev/null || true
    apt-get install -y amneziawg amneziawg-tools || apt-get install -y amneziawg-tools || true
fi

# 2. Setup permissions and directories
echo "[2/6] Setting up VPN directories and permissions..."
mkdir -p /etc/amnezia/amneziawg
chown -R www-data:www-data /etc/amnezia
chmod 700 /etc/amnezia/amneziawg

# Ensure www-data home directory exists
mkdir -p /var/www
chown -R www-data:www-data /var/www

# 3. Setup Sudoers for www-data
echo "[3/6] Configuring passwordless sudo for www-data..."
cat << 'EOF' > /etc/sudoers.d/amnezia-panel
www-data ALL=(ALL) NOPASSWD: /usr/bin/awg-quick *
www-data ALL=(ALL) NOPASSWD: /usr/bin/awg *
www-data ALL=(ALL) NOPASSWD: /sbin/iptables *
www-data ALL=(ALL) NOPASSWD: /usr/sbin/iptables *
www-data ALL=(ALL) NOPASSWD: /usr/bin/journalctl *
www-data ALL=(ALL) NOPASSWD: /bin/journalctl *
www-data ALL=(ALL) NOPASSWD: /usr/bin/dmesg
www-data ALL=(ALL) NOPASSWD: /bin/dmesg
EOF
chmod 440 /etc/sudoers.d/amnezia-panel

# Enable IP Forwarding
echo "Enabling IPv4 Forwarding..."
sysctl -w net.ipv4.ip_forward=1
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf

# 4. Setup Python Environment
echo "[4/6] Setting up Python Virtual Environment..."
PROJ_DIR=$(pwd)
chown -R www-data:www-data "$PROJ_DIR"

if [ ! -d "$PROJ_DIR/venv" ]; then
    sudo -u www-data python3 -m venv "$PROJ_DIR/venv"
fi

echo "Installing Python dependencies from requirements.txt..."
sudo -u www-data "$PROJ_DIR/venv/bin/pip" install --upgrade pip
sudo -u www-data "$PROJ_DIR/venv/bin/pip" install -r "$PROJ_DIR/requirements.txt"

# 5. Database and Superuser setup
echo "[5/6] Setting up database and Admin user..."
sudo -u www-data "$PROJ_DIR/venv/bin/python" "$PROJ_DIR/manage.py" makemigrations vpn_panel
sudo -u www-data "$PROJ_DIR/venv/bin/python" "$PROJ_DIR/manage.py" migrate
sudo -u www-data "$PROJ_DIR/venv/bin/python" "$PROJ_DIR/manage.py" collectstatic --noinput

# Create default superuser (admin / admin)
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=admin
export DJANGO_SUPERUSER_EMAIL=admin@example.com
sudo -u www-data -E "$PROJ_DIR/venv/bin/python" "$PROJ_DIR/manage.py" createsuperuser --noinput || echo "Admin user already exists or skipped."

# 6. Setup Systemd Service
echo "[6/6] Creating Systemd Service..."
cat << EOF > /etc/systemd/system/amnezia-panel.service
[Unit]
Description=AmneziaWG Control Panel (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJ_DIR
ExecStart=$PROJ_DIR/venv/bin/gunicorn amnezia_web.wsgi:application --workers 2 --bind 0.0.0.0:6612
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable amnezia-panel
systemctl restart amnezia-panel

echo "========================================="
echo " Installation Complete!"
echo " The panel is now running on port 6612."
echo " Login with Username: admin | Password: admin"
echo "========================================="
