#!/usr/bin/env python3
"""
Generate complete enterprise inventory with all required device counts
Target counts:
- Development devices: 10 (completed)
- Cisco switches: 300 (30 core/dist + 270 access)
- Cisco routers: 200
- Arista switches: 50  
- Juniper routers: 50
- Palo Alto firewalls: 50
Total: 660 network devices
"""

def generate_complete_inventory():
    inventory = """---
# Complete Enterprise-Scale Production Network Inventory
# Total Device Count Summary:
# - Development: 10 devices (completed)
# - Cisco Devices: 300 switches + 200 routers = 500 total
# - Arista Switches: 50 devices  
# - Juniper Routers: 50 devices
# - Palo Alto Firewalls: 50 devices
# TOTAL: 660 network devices

all:
  children:
    # ===========================
    # DEVELOPMENT ENVIRONMENT (10 devices)
    # ===========================
    development_devices:
      children:
        development_switches:
          hosts:
"""
    
    # Development devices (10 total)
    for i in range(1, 6):  # 5 switches
        inventory += f"""            sw-dev-{i:03d}:
              ansible_host: 10.255.1.{10+i-1}
              ansible_network_os: {'ios' if i <= 3 else 'eos'}
              ansible_connection: {'network_cli' if i <= 3 else 'httpapi'}
              ansible_user: "{{{{ vault_{'cisco' if i <= 3 else 'arista'}_username }}}}"
              ansible_password: "{{{{ vault_{'cisco' if i <= 3 else 'arista'}_password }}}}"
              {'ansible_httpapi_use_ssl: true' if i > 3 else ''}
              {'ansible_httpapi_port: 443' if i > 3 else ''}
              device_role: development_switch
              site: dev_lab
"""
    
    inventory += """        development_routers:
          hosts:
"""
    
    for i in range(1, 4):  # 3 routers  
        inventory += f"""            rtr-dev-{i:03d}:
              ansible_host: 10.255.2.{10+i-1}
              ansible_network_os: {'ios' if i <= 2 else 'junos'}
              ansible_connection: {'network_cli' if i <= 2 else 'netconf'}
              ansible_user: "{{{{ vault_{'cisco' if i <= 2 else 'juniper'}_username }}}}"
              ansible_password: "{{{{ vault_{'cisco' if i <= 2 else 'juniper'}_password }}}}"
              device_role: development_router
              site: dev_lab
"""
    
    inventory += """        development_firewalls:
          hosts:
            fw-dev-001:
              ansible_host: 10.255.3.10
              ansible_connection: local
              panos_username: "{{ vault_panos_username }}"
              panos_password: "{{ vault_panos_password }}"
              device_role: development_firewall
              site: dev_lab
              panos_provider:
                ip_address: "{{ ansible_host }}"
                username: "{{ panos_username }}"
                password: "{{ panos_password }}"
                timeout: 120
            fw-dev-002:
              ansible_host: 10.255.3.11
              ansible_connection: httpapi
              ansible_httpapi_use_ssl: true
              ansible_httpapi_port: 443
              ansible_httpapi_session_key: "{{ vault_fortigate_api_token }}"
              device_role: development_firewall
              site: dev_lab

    # ===========================
    # CISCO DEVICES (500 TOTAL)
    # ===========================
    cisco_devices:
      children:
        cisco_switches:
          children:
            core_switches:
              hosts:
"""
    
    # Core switches (10 devices)
    sites = ['datacenter_01', 'datacenter_01', 'datacenter_02', 'datacenter_02', 'datacenter_03', 
             'datacenter_03', 'branch_01', 'branch_01', 'branch_02', 'branch_02']
    
    for i in range(1, 11):
        inventory += f"""                sw-core-{i:03d}:
                  ansible_host: 10.0.1.{9+i}
                  ansible_network_os: ios
                  ansible_connection: network_cli
                  ansible_user: "{{{{ vault_cisco_username }}}}"
                  ansible_password: "{{{{ vault_cisco_password }}}}"
                  device_role: core_switch
                  site: {sites[i-1]}
"""
    
    inventory += """            distribution_switches:
              hosts:
"""
    
    # Distribution switches (20 devices)
    dist_sites = ['datacenter_01', 'datacenter_01', 'datacenter_02', 'datacenter_02', 'branch_01', 'branch_01',
                  'branch_02', 'branch_02', 'remote_01', 'remote_01', 'remote_02', 'remote_02', 'remote_03', 'remote_03',
                  'remote_04', 'remote_04', 'remote_05', 'remote_05', 'remote_06', 'remote_06']
    
    for i in range(1, 21):
        inventory += f"""                sw-dist-{i:02d}:
                  ansible_host: 10.0.2.{9+i}
                  ansible_network_os: ios
                  ansible_connection: network_cli
                  ansible_user: "{{{{ vault_cisco_username }}}}"
                  ansible_password: "{{{{ vault_cisco_password }}}}"
                  device_role: distribution_switch
                  site: {dist_sites[i-1]}
"""
    
    inventory += """            access_switches:
              hosts:
"""
    
    # Access switches (270 devices)
    for i in range(1, 271):
        site_num = ((i-1) // 10) + 1
        floor = ((i-1) % 10) + 1
        inventory += f"""                sw-access-{i:03d}:
                  ansible_host: 10.0.3.{i}
                  ansible_network_os: ios
                  ansible_connection: network_cli
                  ansible_user: "{{{{ vault_cisco_username }}}}"
                  ansible_password: "{{{{ vault_cisco_password }}}}"
                  device_role: access_switch
                  site: site_{site_num:02d}
                  floor: {floor}
"""
    
    inventory += """        cisco_routers:
          children:
            wan_routers:
              hosts:
"""
    
    # WAN routers (50 devices)
    for i in range(1, 51):
        site_num = ((i-1) // 8) + 1
        bgp_asn = 65000 + site_num
        inventory += f"""                rtr-wan-{i:03d}:
                  ansible_host: 10.1.2.{i}
                  ansible_network_os: ios
                  ansible_connection: network_cli
                  ansible_user: "{{{{ vault_cisco_username }}}}"
                  ansible_password: "{{{{ vault_cisco_password }}}}"
                  device_role: wan_router
                  site: site_{site_num:02d}
                  bgp_asn: {bgp_asn}
"""
    
    inventory += """            branch_routers:
              hosts:
"""
    
    # Branch routers (75 devices)
    for i in range(1, 76):
        site_num = ((i-1) // 8) + 1
        bgp_asn = 65000 + site_num
        inventory += f"""                rtr-branch-{i:03d}:
                  ansible_host: 10.1.3.{i}
                  ansible_network_os: ios
                  ansible_connection: network_cli
                  ansible_user: "{{{{ vault_cisco_username }}}}"
                  ansible_password: "{{{{ vault_cisco_password }}}}"
                  device_role: branch_router
                  site: site_{site_num:02d}
                  bgp_asn: {bgp_asn}
"""
    
    inventory += """            access_routers:
              hosts:
"""
    
    # Access routers (75 devices)
    for i in range(1, 76):
        site_num = ((i-1) // 8) + 1
        bgp_asn = 65000 + site_num
        inventory += f"""                rtr-access-{i:03d}:
                  ansible_host: 10.1.4.{i}
                  ansible_network_os: ios
                  ansible_connection: network_cli
                  ansible_user: "{{{{ vault_cisco_username }}}}"
                  ansible_password: "{{{{ vault_cisco_password }}}}"
                  device_role: access_router
                  site: site_{site_num:02d}
                  bgp_asn: {bgp_asn}
"""
    
    inventory += """
    # ===========================
    # ARISTA DEVICES (50 TOTAL)
    # ===========================
    arista_devices:
      children:
        arista_switches:
          hosts:
"""
    
    # Arista switches (50 devices)
    for i in range(1, 51):
        device_type = 'spine' if i <= 10 else 'leaf'
        base_ip = 10 if device_type == 'spine' else 20
        site_name = f"datacenter_{((i-1) // 5) + 1:02d}"
        inventory += f"""            sw-{device_type}-{i:03d}:
              ansible_host: 10.2.{1 if device_type == 'spine' else 2}.{base_ip + i - 1}
              ansible_network_os: eos
              ansible_connection: httpapi
              ansible_httpapi_use_ssl: true
              ansible_httpapi_port: 443
              ansible_user: "{{{{ vault_arista_username }}}}"
              ansible_password: "{{{{ vault_arista_password }}}}"
              device_role: {device_type}_switch
              site: {site_name}
"""
    
    inventory += """
    # ===========================
    # JUNIPER DEVICES (50 TOTAL)
    # ===========================
    juniper_devices:
      children:
        juniper_routers:
          hosts:
"""
    
    # Juniper routers (50 devices)
    for i in range(1, 51):
        if i <= 15:
            device_type = 'core'
            base_ip = 10
            site_num = ((i-1) // 5) + 1
        elif i <= 35:
            device_type = 'edge'
            base_ip = 20
            site_num = ((i-16) // 5) + 1
        else:
            device_type = 'pe'
            base_ip = 45
            site_num = ((i-36) // 5) + 8
            
        bgp_asn = 65100 + site_num
        inventory += f"""            rtr-{device_type}-jun-{i:03d}:
              ansible_host: 10.3.{1 if device_type == 'core' else 2 if device_type == 'edge' else 3}.{base_ip + ((i-1) % 15)}
              ansible_network_os: junos
              ansible_connection: netconf
              ansible_user: "{{{{ vault_juniper_username }}}}"
              ansible_password: "{{{{ vault_juniper_password }}}}"
              device_role: {device_type}_router
              site: site_{site_num:02d}
              bgp_asn: {bgp_asn}
"""
    
    inventory += """
    # ===========================
    # PALO ALTO DEVICES (50 TOTAL)
    # ===========================
    palo_alto_devices:
      children:
        palo_alto_firewalls:
          hosts:
"""
    
    # Palo Alto firewalls (50 devices)
    for i in range(1, 51):
        if i <= 10:
            device_type = 'perimeter'
            base_ip = 10
            site_num = ((i-1) // 5) + 1
        elif i <= 25:
            device_type = 'internal'
            base_ip = 20
            site_num = ((i-11) // 5) + 3
        else:
            device_type = 'dmz'
            base_ip = 35
            site_num = ((i-26) // 5) + 6
            
        inventory += f"""            fw-{device_type}-{i:03d}:
              ansible_host: 10.4.{1 if device_type == 'perimeter' else 2 if device_type == 'internal' else 3}.{base_ip + ((i-1) % 10)}
              ansible_connection: local
              panos_username: "{{{{ vault_panos_username }}}}"
              panos_password: "{{{{ vault_panos_password }}}}"
              device_role: {device_type}_firewall
              site: site_{site_num:02d}
              panos_provider:
                ip_address: "{{{{ ansible_host }}}}"
                username: "{{{{ panos_username }}}}"
                password: "{{{{ panos_password }}}}"
                timeout: 120
"""
    
    inventory += """
    # ===========================
    # FORTINET DEVICES
    # ===========================
    fortinet_devices:
      children:
        fortinet_firewalls:
          hosts:
            fw-internal-fort-01:
              ansible_host: 10.0.1.60
              ansible_connection: httpapi
              ansible_httpapi_use_ssl: true
              ansible_httpapi_port: 443
              ansible_httpapi_session_key: "{{ vault_fortigate_api_token }}"
              device_role: internal_firewall
              site: datacenter_01

    # ===========================
    # LOGICAL GROUPINGS
    # ===========================
    # Group by vendor
    all_cisco:
      children:
        - cisco_devices
    
    all_arista:
      children:
        - arista_devices
    
    all_juniper:
      children:
        - juniper_devices
    
    all_palo_alto:
      children:
        - palo_alto_devices
    
    # Group by device type
    all_switches:
      children:
        - cisco_devices:cisco_switches
        - arista_devices:arista_switches
    
    all_routers:
      children:
        - cisco_devices:cisco_routers
        - juniper_devices:juniper_routers
    
    all_firewalls:
      children:
        - palo_alto_devices:palo_alto_firewalls
        - fortinet_devices:fortinet_firewalls
        
    # Group by environment
    production:
      children:
        - cisco_devices
        - arista_devices
        - juniper_devices
        - palo_alto_devices
        - fortinet_devices
        
    development:
      children:
        - development_devices
"""
    
    return inventory

if __name__ == "__main__":
    print("Generating complete enterprise inventory...")
    inventory_content = generate_complete_inventory()
    
    with open("inventories/production/hosts_complete_enterprise.yml", "w") as f:
        f.write(inventory_content)
    
    print("Complete enterprise inventory generated successfully!")
    print("\nDevice count summary:")
    print("- Development devices: 10")
    print("- Cisco switches: 300 (10 core + 20 dist + 270 access)")
    print("- Cisco routers: 200 (50 WAN + 75 branch + 75 access)")
    print("- Arista switches: 50")
    print("- Juniper routers: 50")
    print("- Palo Alto firewalls: 50")
    print("- Fortinet firewalls: 1")
    print("TOTAL: 661 network devices")
