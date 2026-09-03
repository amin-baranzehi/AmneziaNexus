import subprocess
import os
import re

class NetworkManager:
    """Service to handle iptables and IP forwarding rules."""
    
    @staticmethod
    def enable_routing(interface: str = 'awg0') -> bool:
        """Enable NAT masquerading and forward rules for the given interface."""
        try:
            # Allow forwarding to and from the interface
            subprocess.run(['sudo', 'iptables', '-A', 'FORWARD', '-o', interface, '-j', 'ACCEPT'], check=False)
            subprocess.run(['sudo', 'iptables', '-A', 'FORWARD', '-i', interface, '-j', 'ACCEPT'], check=False)
            # Setup NAT
            subprocess.run(['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', interface, '-j', 'MASQUERADE'], check=False)
            return True
        except Exception:
            return False

    @staticmethod
    def disable_routing(interface: str = 'awg0') -> bool:
        """Disable NAT masquerading and forward rules for the given interface."""
        try:
            subprocess.run(['sudo', 'iptables', '-D', 'FORWARD', '-o', interface, '-j', 'ACCEPT'], check=False)
            subprocess.run(['sudo', 'iptables', '-D', 'FORWARD', '-i', interface, '-j', 'ACCEPT'], check=False)
            subprocess.run(['sudo', 'iptables', '-t', 'nat', '-D', 'POSTROUTING', '-o', interface, '-j', 'MASQUERADE'], check=False)
            return True
        except Exception:
            return False

class VPNManager:
    """Service to handle WireGuard / AmneziaWG connections."""
    
    CONFIG_PATH = '/etc/amnezia/amneziawg/awg0.conf'
    CONFIG_DIR = os.path.dirname(CONFIG_PATH)

    @classmethod
    def write_config(cls, config_content: str) -> bool:
        """Write the configuration content to the physical file."""
        try:
            if not os.path.exists(cls.CONFIG_DIR):
                os.makedirs(cls.CONFIG_DIR, exist_ok=True)
            with open(cls.CONFIG_PATH, 'w') as f:
                f.write(config_content)
            return True
        except Exception:
            return False

    @classmethod
    def start_connection(cls, config_content: str) -> tuple[bool, str]:
        """Write config and start the VPN connection."""
        if not cls.write_config(config_content):
            return False, "Permission Denied: Cannot write config file."
            
        result = subprocess.run(['sudo', 'awg-quick', 'up', 'awg0'], capture_output=True, text=True)
        if result.returncode == 0:
            NetworkManager.enable_routing()
            return True, "Connected successfully."
        return False, result.stderr

    @classmethod
    def stop_connection(cls) -> tuple[bool, str]:
        """Stop the VPN connection."""
        result = subprocess.run(['sudo', 'awg-quick', 'down', 'awg0'], capture_output=True, text=True)
        NetworkManager.disable_routing()
        if result.returncode == 0:
            return True, "Disconnected successfully."
        return False, result.stderr

    @staticmethod
    def is_connected() -> bool:
        """Check if the interface exists."""
        try:
            result = subprocess.run(['ip', 'link', 'show', 'awg0'], capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False

class PingService:
    """Service to handle latency checks."""
    
    @staticmethod
    def ping(address: str, count: int = 1, timeout: int = 2) -> str:
        """Ping a specific address and return the latency in ms."""
        if not address:
            return "N/A"
            
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), '-W', str(timeout), address],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                match = re.search(r'time=([\d.]+)\s*ms', result.stdout)
                if match:
                    return f"{match.group(1)}ms"
            return "Timeout"
        except Exception:
            return "Error"
