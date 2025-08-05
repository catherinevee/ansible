#!/usr/bin/env python3
"""
Network Device Inventory Discovery Script
Automatically discovers network devices and generates Ansible inventory
"""

import argparse
import ipaddress
import json
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

def ping_host(ip):
    """Ping a host to check if it's reachable"""
    try:
        # Use ping command appropriate for the OS
        cmd = ["ping", "-n", "1", "-w", "1000", str(ip)] if sys.platform == "win32" else ["ping", "-c", "1", "-W", "1", str(ip)]
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        return ip if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, Exception):
        return None

def check_ssh_port(ip, port=22, timeout=3):
    """Check if SSH port is open on the target host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((str(ip), port))
        sock.close()
        return ip if result == 0 else None
    except Exception:
        return None

def discover_network_devices(network_range, max_workers=50):
    """Discover network devices in the given range"""
    print(f"Discovering devices in network range: {network_range}")
    
    try:
        network = ipaddress.ip_network(network_range, strict=False)
    except ValueError as e:
        print(f"Invalid network range: {e}")
        return []
    
    # First pass: ping sweep
    live_hosts = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        ping_futures = {executor.submit(ping_host, ip): ip for ip in network.hosts()}
        
        for future in as_completed(ping_futures):
            result = future.result()
            if result:
                live_hosts.append(result)
    
    print(f"Found {len(live_hosts)} responding hosts")
    
    # Second pass: SSH port check
    ssh_hosts = []
    with ThreadPoolExecutor(max_workers=max_workers // 2) as executor:
        ssh_futures = {executor.submit(check_ssh_port, ip): ip for ip in live_hosts}
        
        for future in as_completed(ssh_futures):
            result = future.result()
            if result:
                ssh_hosts.append(result)
    
    print(f"Found {len(ssh_hosts)} hosts with SSH enabled")
    return sorted(ssh_hosts)

def classify_device_type(ip):
    """Attempt to classify device type based on banner or other characteristics"""
    # This is a simplified classification - in practice, you'd use SNMP, 
    # SSH banners, or other methods to identify device types
    
    # For demonstration, classify based on IP ranges
    # This should be replaced with actual device detection logic
    last_octet = int(str(ip).split('.')[-1])
    
    if 1 <= last_octet <= 10:
        return "cisco_routers", "ios"
    elif 11 <= last_octet <= 30:
        return "cisco_switches", "ios"
    elif 31 <= last_octet <= 40:
        return "arista_switches", "eos"
    elif 41 <= last_octet <= 50:
        return "juniper_routers", "junos"
    elif 51 <= last_octet <= 60:
        return "palo_alto_firewalls", "panos"
    elif 61 <= last_octet <= 70:
        return "fortinet_firewalls", "fortios"
    else:
        return "unknown_devices", "unknown"

def generate_inventory(discovered_hosts, output_format='yaml'):
    """Generate Ansible inventory from discovered hosts"""
    
    inventory = {
        'all': {
            'children': {
                'cisco_devices': {
                    'children': {
                        'cisco_routers': {'hosts': {}},
                        'cisco_switches': {'hosts': {}}
                    }
                },
                'palo_alto_devices': {
                    'children': {
                        'palo_alto_firewalls': {'hosts': {}}
                    }
                },
                'fortinet_devices': {
                    'children': {
                        'fortinet_firewalls': {'hosts': {}}
                    }
                },
                'juniper_devices': {
                    'children': {
                        'juniper_routers': {'hosts': {}}
                    }
                },
                'arista_devices': {
                    'children': {
                        'arista_switches': {'hosts': {}}
                    }
                },
                'unknown_devices': {'hosts': {}}
            }
        }
    }
    
    for ip in discovered_hosts:
        device_group, os_type = classify_device_type(ip)
        hostname = f"device-{str(ip).replace('.', '-')}"
        
        device_config = {
            'ansible_host': str(ip),
            'device_role': 'auto_discovered',
            'site': 'discovered'
        }
        
        # Add OS-specific connection parameters
        if os_type == 'ios':
            device_config.update({
                'ansible_network_os': 'ios',
                'ansible_connection': 'network_cli',
                'ansible_user': '{{ vault_cisco_username }}',
                'ansible_password': '{{ vault_cisco_password }}'
            })
        elif os_type == 'eos':
            device_config.update({
                'ansible_network_os': 'eos',
                'ansible_connection': 'httpapi',
                'ansible_httpapi_use_ssl': True,
                'ansible_httpapi_port': 443,
                'ansible_user': '{{ vault_arista_username }}',
                'ansible_password': '{{ vault_arista_password }}'
            })
        elif os_type == 'junos':
            device_config.update({
                'ansible_network_os': 'junos',
                'ansible_connection': 'netconf',
                'ansible_user': '{{ vault_juniper_username }}',
                'ansible_password': '{{ vault_juniper_password }}'
            })
        elif os_type == 'panos':
            device_config.update({
                'ansible_connection': 'local',
                'panos_username': '{{ vault_panos_username }}',
                'panos_password': '{{ vault_panos_password }}',
                'panos_provider': {
                    'ip_address': '{{ ansible_host }}',
                    'username': '{{ panos_username }}',
                    'password': '{{ panos_password }}'
                }
            })
        elif os_type == 'fortios':
            device_config.update({
                'ansible_connection': 'httpapi',
                'ansible_httpapi_use_ssl': True,
                'ansible_httpapi_port': 443,
                'ansible_httpapi_session_key': '{{ vault_fortigate_api_token }}'
            })
        
        # Navigate to the correct group in the inventory structure
        group_path = inventory['all']['children']
        
        if device_group in ['cisco_routers', 'cisco_switches']:
            group_path['cisco_devices']['children'][device_group]['hosts'][hostname] = device_config
        elif device_group == 'palo_alto_firewalls':
            group_path['palo_alto_devices']['children'][device_group]['hosts'][hostname] = device_config
        elif device_group == 'fortinet_firewalls':
            group_path['fortinet_devices']['children'][device_group]['hosts'][hostname] = device_config
        elif device_group == 'juniper_routers':
            group_path['juniper_devices']['children'][device_group]['hosts'][hostname] = device_config
        elif device_group == 'arista_switches':
            group_path['arista_devices']['children'][device_group]['hosts'][hostname] = device_config
        else:
            group_path['unknown_devices']['hosts'][hostname] = device_config
    
    return inventory

def main():
    parser = argparse.ArgumentParser(description='Network Device Discovery Tool')
    parser.add_argument('network', help='Network range to scan (e.g., 192.168.1.0/24)')
    parser.add_argument('-o', '--output', default='discovered_inventory.yml', 
                        help='Output inventory file (default: discovered_inventory.yml)')
    parser.add_argument('-f', '--format', choices=['yaml', 'json'], default='yaml',
                        help='Output format (default: yaml)')
    parser.add_argument('-w', '--workers', type=int, default=50,
                        help='Number of worker threads (default: 50)')
    
    args = parser.parse_args()
    
    print("Network Device Discovery Tool")
    print("=" * 40)
    
    # Discover devices
    discovered_hosts = discover_network_devices(args.network, args.workers)
    
    if not discovered_hosts:
        print("No network devices found with SSH enabled")
        return
    
    # Generate inventory
    inventory = generate_inventory(discovered_hosts, args.format)
    
    # Write output
    output_path = Path(args.output)
    
    try:
        with open(output_path, 'w') as f:
            if args.format == 'yaml':
                yaml.dump(inventory, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(inventory, f, indent=2)
        
        print(f"\nInventory file created: {output_path}")
        print(f"Discovered {len(discovered_hosts)} network devices")
        print("\nNext steps:")
        print("1. Review and customize the generated inventory file") 
        print("2. Update device credentials in vault/secrets.yml")
        print("3. Test connectivity with ansible all -m ping")
        print("4. Customize device classifications as needed")
        
    except Exception as e:
        print(f"Error writing inventory file: {e}")

if __name__ == "__main__":
    main()
