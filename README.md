# AmneziaNexus

A highly advanced, OOP-driven web-based control panel to manage **AmneziaWG (WireGuard)** VPN clients and act as a network router on Linux Single Board Computers (Orange Pi, Raspberry Pi) running Armbian, Ubuntu, or Debian.

Developed by [Amin Baranzehi](https://github.com/amin-baranzehi).

## Features
- **Multiple Servers**: Save and manage unlimited VPN configurations/profiles.
- **Latency Check (Ping)**: Built-in asynchronous latency tester for all saved endpoints.
- **Auto-Routing (Gateway Mode)**: Automatically sets up `iptables` NAT (Masquerade) and IP Forwarding so the board can act as a network router for other devices (phones, laptops, TVs).
- **Advanced Dark UI**: Clean, responsive, dark-themed Single Page Application (SPA) built with Tailwind CSS.
- **Secure Authentication**: Built-in Django authentication system.
- **Enterprise Architecture**: Built using OOP, SOLID principles, Django Class-Based Views (CBVs), and DRY methodologies.

## Automated Installation (Recommended)

This project includes a fully automated installation script that sets up the environment, installs dependencies, configures `systemd` to run the panel via **Gunicorn** on port 6612, and sets up a default admin user.

```bash
git clone https://github.com/amin-baranzehi/AmneziaNexus.git
cd AmneziaNexus
sudo bash install.sh
```

**Default Login:**
- Username: `admin`
- Password: `admin`

*Please change the password immediately after logging in.*

## Uninstallation

If you wish to completely remove AmneziaNexus and revert all system/routing changes made by the panel:

```bash
cd AmneziaNexus
sudo bash uninstall.sh
```

## Manual Setup (Development)

1. Clone the repository.
2. Create a virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Collect static files: `python manage.py collectstatic`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the server: `python manage.py runserver 0.0.0.0:6612`

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
