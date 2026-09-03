#!/bin/bash

# AmneziaWG Web Panel Auto-Installation Script for Armbian/Ubuntu/Debian
# Run with sudo: sudo bash install.sh

echo "========================================="
echo " Starting AmneziaWG Panel Installation..."
echo "========================================="

# 1. Update and install dependencies
echo "[1/6] Installing system dependencies..."
apt-get update
apt-get install -y python3-venv python3-pip iptables wireguard-tools sudo

# 2. Setup permissions and directories
echo "[2/6] Setting up VPN directories and permissions..."
mkdir -p /etc/amnezia/amneziawg
chown -R www-data:www-data /etc/amnezia
chmod 700 /etc/amnezia/amneziawg

# 3. Setup Sudoers for www-data
echo "[3/6] Configuring passwordless sudo for www-data..."
cat << 'EOF' > /etc/sudoers.d/amnezia-panel
www-data ALL=(ALL) NOPASSWD: /usr/bin/awg-quick up awg0
www-data ALL=(ALL) NOPASSWD: /usr/bin/awg-quick down awg0
www-data ALL=(ALL) NOPASSWD: /sbin/iptables -t nat -A POSTROUTING -o awg0 -j MASQUERADE
www-data ALL=(ALL) NOPASSWD: /sbin/iptables -t nat -D POSTROUTING -o awg0 -j MASQUERADE
www-data ALL=(ALL) NOPASSWD: /sbin/iptables -A FORWARD -o awg0 -j ACCEPT
www-data ALL=(ALL) NOPASSWD: /sbin/iptables -A FORWARD -i awg0 -j ACCEPT
www-data ALL=(ALL) NOPASSWD: /sbin/iptables -D FORWARD -o awg0 -j ACCEPT
www-data ALL=(ALL) NOPASSWD: /sbin/iptables -D FORWARD -i awg0 -j ACCEPT
www-data ALL=(ALL) NOPASSWD: /usr/bin/journalctl
www-data ALL=(ALL) NOPASSWD: /usr/bin/dmesg
EOF
chmod 440 /etc/sudoers.d/amnezia-panel

# Enable IP Forwarding
sysctl -w net.ipv4.ip_forward=1
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf

# 4. Setup Python Environment
echo "[4/6] Setting up Python Virtual Environment..."
PROJ_DIR=$(pwd)
chown -R www-data:www-data $PROJ_DIR
su - www-data -s /bin/bash -c "cd $PROJ_DIR && python3 -m venv venv"
su - www-data -s /bin/bash -c "cd $PROJ_DIR && source venv/bin/activate && pip install -r requirements.txt"

# 5. Database and Superuser setup
echo "[5/6] Setting up database and Admin user..."
su - www-data -s /bin/bash -c "cd $PROJ_DIR && source venv/bin/activate && python manage.py migrate"
su - www-data -s /bin/bash -c "cd $PROJ_DIR && source venv/bin/activate && python manage.py collectstatic --noinput"

# Create default superuser (admin / admin)
su - www-data -s /bin/bash -c "cd $PROJ_DIR && source venv/bin/activate && export DJANGO_SUPERUSER_USERNAME=admin && export DJANGO_SUPERUSER_PASSWORD=admin && export DJANGO_SUPERUSER_EMAIL=admin@example.com && python manage.py createsuperuser --noinput" || echo "Admin user already exists or failed to create."

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
