# AmneziaWG Control Panel

A lightweight, modern, and easy-to-use web-based control panel to manage an **AmneziaWG (WireGuard)** VPN client and act as a network router on Linux Single Board Computers (like Orange Pi, Raspberry Pi) running Armbian, Ubuntu, or Debian.

Developed by [Amin Baranzehi](https://github.com/amin-baranzehi).

## Features
- **One-Click Connect/Disconnect**: Easily start or stop the VPN connection.
- **Auto-Routing (Gateway Mode)**: Automatically sets up `iptables` NAT (Masquerade) and IP Forwarding so the board can act as a network router for other devices (phones, laptops, TVs).
- **Configuration Management**: Paste and save your `.conf` file directly from the web interface.
- **Secure Authentication**: Built-in Django authentication system.
- **Modern UI**: Clean, responsive, single-page dashboard built with Tailwind CSS.

## Automated Installation (Recommended for Orange Pi / Armbian)

This project includes an automated installation script that sets up the environment, installs dependencies, configures `systemd` to run the panel on port 6612, and sets up a default admin user.

```bash
git clone https://github.com/amin-baranzehi/amneziawg-web.git
cd amneziawg-web
sudo bash install.sh
```

**Default Login:**
- Username: `admin`
- Password: `admin`

*Please change the password immediately after logging in.*

## Manual Setup (Development)

If you wish to run the project manually or contribute:

1. Clone the repository.
2. Create a virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run the server: `python manage.py runserver 0.0.0.0:6612`

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
