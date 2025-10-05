import subprocess
import json
import os
import time
import socket
from urllib.parse import urlparse, parse_qs
import requests


def parse_vless_link(link):
    """Parse VLESS link and return config."""
    parsed = urlparse(link)
    if not all([parsed.username, parsed.hostname, parsed.port]):
        raise ValueError("Invalid VLESS link")
    
    params = parse_qs(parsed.query)
    network = params.get("type", ["tcp"])[0]
    header_type = params.get("headerType", ["none"])[0]
    
    # Build stream settings
    stream_settings = {
        "network": network,
        "security": params.get("security", ["none"])[0]
    }
    
    # Add TCP settings if using http header
    if network == "tcp" and header_type == "http":
        host = params.get("host", [""])[0]
        path = params.get("path", ["/"])[0]
        stream_settings["tcpSettings"] = {
            "header": {
                "type": "http",
                "request": {
                    "version": "1.1",
                    "method": "GET",
                    "path": [path],
                    "headers": {
                        "Host": [host] if host else [],
                        "User-Agent": ["Mozilla/5.0"],
                        "Accept-Encoding": ["gzip, deflate"],
                        "Connection": ["keep-alive"],
                        "Pragma": "no-cache"
                    }
                }
            }
        }
    
    return {
        "protocol": "vless",
        "settings": {
            "vnext": [{
                "address": parsed.hostname,
                "port": parsed.port,
                "users": [{"id": parsed.username, "encryption": params.get("encryption", ["none"])[0]}]
            }]
        },
        "streamSettings": stream_settings
    }


def find_v2ray_exe():
    """Find v2ray.exe in project folder."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    v2ray_path = os.path.join(project_root, "v2ray-windows-64", "v2ray.exe")
    
    if os.path.exists(v2ray_path):
        return v2ray_path
    return None


def check_v2ray_config(config_link, test_url="http://www.google.com/generate_204", timeout=10):
    """
    Test V2Ray config link by running v2ray and checking connection.
    
    Returns: (success: bool, message: str, latency_ms: float)
    """
    # Parse link
    try:
        parsed = urlparse(config_link)
        if parsed.scheme == "vless":
            outbound = parse_vless_link(config_link)
        else:
            return False, f"Unsupported protocol: {parsed.scheme}", -1.0
    except Exception as e:
        return False, f"Parse error: {e}", -1.0
    
    # Find v2ray
    v2ray_exe = find_v2ray_exe()
    if not v2ray_exe:
        return False, "v2ray.exe not found", -1.0
    
    # Create config
    local_port = 10809
    config = {
        "inbounds": [{
            "port": local_port,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": True}
        }],
        "outbounds": [outbound]
    }
    
    config_file = "temp_config.json"
    process = None
    
    try:
        # Write config
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Start v2ray
        process = subprocess.Popen(
            [v2ray_exe, "run", "-c", config_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for proxy to be ready
        for _ in range(20):
            try:
                socket.create_connection(("127.0.0.1", local_port), timeout=0.1).close()
                break
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(0.1)
        else:
            return False, "V2Ray failed to start", -1.0
        
        # Test connection
        proxies = {
            'http': f'socks5h://127.0.0.1:{local_port}',
            'https': f'socks5h://127.0.0.1:{local_port}'
        }
        
        start = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        latency = (time.time() - start) * 1000
        
        if 200 <= response.status_code < 300:
            return True, f"Success ({response.status_code})", round(latency)
        else:
            return False, f"HTTP {response.status_code}", -1.0
            
    except requests.exceptions.Timeout:
        return False, "Timeout", -1.0
    except Exception as e:
        return False, f"Error: {e}", -1.0
    finally:
        # Cleanup
        if process:
            process.kill()
            process.wait()
        if os.path.exists(config_file):
            os.remove(config_file)
