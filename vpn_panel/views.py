from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AmneziaConfig
import subprocess
import os

# -------------------------------------------------------------------------
# SUDOERS CONFIGURATION INSTRUCTIONS
# -------------------------------------------------------------------------
# To allow the Django web-server user (e.g., www-data or your local user)
# to execute these commands without a password prompt, run `sudo visudo`
# and add the following lines at the end of the file (replace www-data
# with your actual user if different):
#
# www-data ALL=(ALL) NOPASSWD: /usr/bin/awg-quick up awg0
# www-data ALL=(ALL) NOPASSWD: /usr/bin/awg-quick down awg0
# www-data ALL=(ALL) NOPASSWD: /sbin/iptables -t nat -A POSTROUTING -o awg0 -j MASQUERADE
# www-data ALL=(ALL) NOPASSWD: /sbin/iptables -t nat -D POSTROUTING -o awg0 -j MASQUERADE
# www-data ALL=(ALL) NOPASSWD: /sbin/iptables -A FORWARD -o awg0 -j ACCEPT
# www-data ALL=(ALL) NOPASSWD: /sbin/iptables -A FORWARD -i awg0 -j ACCEPT
# www-data ALL=(ALL) NOPASSWD: /sbin/iptables -D FORWARD -o awg0 -j ACCEPT
# www-data ALL=(ALL) NOPASSWD: /sbin/iptables -D FORWARD -i awg0 -j ACCEPT
#
# Note: You must also ensure the web server user has write access to the
# configuration directory (or use sudo tee to write the config file).
# Example: sudo chown -R www-data:www-data /etc/amnezia/amneziawg
# -------------------------------------------------------------------------

CONFIG_PATH = '/etc/amnezia/amneziawg/awg0.conf'
CONFIG_DIR = os.path.dirname(CONFIG_PATH)

def check_interface_status():
    """Check if the awg0 interface is up by running ip link show."""
    try:
        # Run ip link show awg0. If it returns 0, the interface exists and is up/down.
        # To strictly check if it's UP, we can inspect the output.
        result = subprocess.run(
            ['ip', 'link', 'show', 'awg0'], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode == 0 and 'state UP' in result.stdout:
            return True
        # Sometimes WireGuard interfaces show state UNKNOWN but are active, 
        # so just returning True if the interface exists is often a good fallback.
        # But let's check if the return code is 0 (interface exists).
        return result.returncode == 0
    except Exception:
        return False

@login_required
def dashboard(request):
    """Main dashboard view."""
    config, created = AmneziaConfig.objects.get_or_create(id=1)
    is_connected = check_interface_status()
    
    # Update DB state to match reality if they differ
    if config.is_active != is_connected:
        config.is_active = is_connected
        config.save()

    context = {
        'config': config,
        'is_connected': is_connected,
    }
    return render(request, 'vpn_panel/dashboard.html', context)

@login_required
def save_config(request):
    """Save the configuration to DB and write to physical OS file."""
    if request.method == 'POST':
        config_content = request.POST.get('config_content', '')
        config_name = request.POST.get('config_name', 'Default Profile')
        
        # Save to Database
        config, created = AmneziaConfig.objects.get_or_create(id=1)
        config.name = config_name
        config.config_content = config_content
        config.save()

        # Write to physical file
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR, exist_ok=True)
                
            with open(CONFIG_PATH, 'w') as f:
                f.write(config_content)
                
            messages.success(request, f"Configuration successfully saved to {CONFIG_PATH}")
        except PermissionError:
            messages.error(request, f"Permission Denied: Could not write to {CONFIG_PATH}. Please check folder permissions.")
        except Exception as e:
            messages.error(request, f"Error writing configuration file: {str(e)}")

    return redirect('vpn_panel:dashboard')

@login_required
def toggle_connection(request):
    """Start or Stop the AmneziaWG VPN and Setup Routing."""
    if request.method == 'POST':
        action = request.POST.get('action') # 'start' or 'stop'
        
        if action == 'start':
            try:
                # 1. Bring up the interface
                up_result = subprocess.run(
                    ['sudo', 'awg-quick', 'up', 'awg0'],
                    capture_output=True, text=True
                )
                
                if up_result.returncode != 0:
                    messages.error(request, f"Failed to start VPN: {up_result.stderr}")
                    return redirect('vpn_panel:dashboard')

                # 2. Add iptables rule for NAT / MASQUERADE and Forwarding
                subprocess.run(['sudo', 'iptables', '-A', 'FORWARD', '-o', 'awg0', '-j', 'ACCEPT'], check=False)
                subprocess.run(['sudo', 'iptables', '-A', 'FORWARD', '-i', 'awg0', '-j', 'ACCEPT'], check=False)
                iptables_result = subprocess.run(
                    ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', 'awg0', '-j', 'MASQUERADE'],
                    capture_output=True, text=True
                )
                
                if iptables_result.returncode != 0:
                    messages.warning(request, f"VPN started, but failed to set NAT rule: {iptables_result.stderr}")
                else:
                    messages.success(request, "VPN successfully connected and routing configured!")
                    
            except Exception as e:
                messages.error(request, f"Unexpected error while starting: {str(e)}")

        elif action == 'stop':
            try:
                # Bring down the interface
                down_result = subprocess.run(
                    ['sudo', 'awg-quick', 'down', 'awg0'],
                    capture_output=True, text=True
                )
                
                # Clean up iptables rules
                subprocess.run(['sudo', 'iptables', '-D', 'FORWARD', '-o', 'awg0', '-j', 'ACCEPT'], check=False)
                subprocess.run(['sudo', 'iptables', '-D', 'FORWARD', '-i', 'awg0', '-j', 'ACCEPT'], check=False)
                subprocess.run(['sudo', 'iptables', '-t', 'nat', '-D', 'POSTROUTING', '-o', 'awg0', '-j', 'MASQUERADE'], check=False)
                
                if down_result.returncode != 0:
                    messages.error(request, f"Failed to stop VPN: {down_result.stderr}")
                else:
                    messages.success(request, "VPN successfully disconnected.")
                    
            except Exception as e:
                messages.error(request, f"Unexpected error while stopping: {str(e)}")

    return redirect('vpn_panel:dashboard')
