#!/usr/bin/env python3
"""
Script to generate large-scale network inventory for Ansible
Generates devices according to enterprise requirements:
- 300 Cisco switches (30 core/distribution + 270 access)
- 200 Cisco routers
- 50 Arista switches
- 50 Juniper routers
- 50 Palo Alto firewalls
"""

def generate_cisco_access_switches():
    """Generate 270 Cisco access switches"""
    switches = []
    for i in range(1, 271):
        site_num = ((i - 1) // 10) + 1
        switch_in_site = ((i - 1) % 10) + 1
        
        switch_config = f"""            sw-access-{i:03d}:
              ansible_host: 10.0.3.{i}
              ansible_network_os: ios
              ansible_connection: network_cli
              ansible_user: "{{ vault_cisco_username }}"
              ansible_password: "{{ vault_cisco_password }}"
              device_role: access_switch
              site: site_{site_num:02d}
              floor: {switch_in_site}"""
        switches.append(switch_config)
    
    return '\n'.join(switches)

def generate_cisco_routers():
    """Generate 200 Cisco routers"""
    routers = []
    for i in range(1, 201):
        site_num = ((i - 1) // 8) + 1
        
        if i <= 20:
            role = "edge_router"
            subnet = "10.1.1"
        elif i <= 50:
            role = "wan_router"
            subnet = "10.1.2"
        elif i <= 100:
            role = "branch_router"
            subnet = "10.1.3"
        else:
            role = "access_router"
            subnet = "10.1.4"
        
        ip_offset = ((i - 1) % 254) + 1
        bgp_asn = 65000 + site_num
        
        router_config = f"""            rtr-{role.split('_')[0]}-{i:03d}:
              ansible_host: {subnet}.{ip_offset}
              ansible_network_os: ios
              ansible_connection: network_cli
              ansible_user: "{{ vault_cisco_username }}"
              ansible_password: "{{ vault_cisco_password }}"
              device_role: {role}
              site: site_{site_num:02d}
              bgp_asn: {bgp_asn}"""
        routers.append(router_config)
    
    return '\n'.join(routers)

def generate_arista_switches():
    """Generate 50 Arista switches"""
    switches = []
    for i in range(1, 51):
        site_num = ((i - 1) // 5) + 1
        
        if i <= 10:
            role = "spine_switch"
            subnet = "10.2.1"
        elif i <= 25:
            role = "leaf_switch"
            subnet = "10.2.2"
        else:
            role = "tor_switch"
            subnet = "10.2.3"
        
        ip_offset = ((i - 1) % 50) + 10
        
        switch_config = f"""            sw-{role.split('_')[0]}-{i:03d}:
              ansible_host: {subnet}.{ip_offset}
              ansible_network_os: eos
              ansible_connection: httpapi
              ansible_httpapi_use_ssl: true
              ansible_httpapi_port: 443
              ansible_user: "{{ vault_arista_username }}"
              ansible_password: "{{ vault_arista_password }}"
              device_role: {role}
              site: datacenter_{site_num:02d}"""
        switches.append(switch_config)
    
    return '\n'.join(switches)

def generate_juniper_routers():
    """Generate 50 Juniper routers"""
    routers = []
    for i in range(1, 51):
        site_num = ((i - 1) // 5) + 1
        
        if i <= 15:
            role = "wan_router"
            subnet = "10.3.1"
        elif i <= 35:
            role = "edge_router"
            subnet = "10.3.2"
        else:
            role = "pe_router"
            subnet = "10.3.3"
        
        ip_offset = ((i - 1) % 50) + 10
        bgp_asn = 65100 + site_num
        
        router_config = f"""            rtr-{role.split('_')[0]}-jun-{i:03d}:
              ansible_host: {subnet}.{ip_offset}
              ansible_network_os: junos
              ansible_connection: netconf
              ansible_user: "{{ vault_juniper_username }}"
              ansible_password: "{{ vault_juniper_password }}"
              device_role: {role}
              site: site_{site_num:02d}
              bgp_asn: {bgp_asn}"""
        routers.append(router_config)
    
    return '\n'.join(routers)

def generate_palo_alto_firewalls():
    """Generate 50 Palo Alto firewalls"""
    firewalls = []
    for i in range(1, 51):
        site_num = ((i - 1) // 5) + 1
        
        if i <= 10:
            role = "perimeter_firewall"
            subnet = "10.4.1"
        elif i <= 25:
            role = "internal_firewall"
            subnet = "10.4.2"
        elif i <= 40:
            role = "dmz_firewall"
            subnet = "10.4.3"
        else:
            role = "datacenter_firewall"
            subnet = "10.4.4"
        
        ip_offset = ((i - 1) % 50) + 10
        
        firewall_config = f"""            fw-{role.split('_')[0]}-{i:03d}:
              ansible_host: {subnet}.{ip_offset}
              ansible_connection: local
              panos_username: "{{ vault_panos_username }}"
              panos_password: "{{ vault_panos_password }}"
              device_role: {role}
              site: site_{site_num:02d}
              panos_provider:
                ip_address: "{{ ansible_host }}"
                username: "{{ panos_username }}"
                password: "{{ panos_password }}"
                timeout: 120"""
        firewalls.append(firewall_config)
    
    return '\n'.join(firewalls)

def generate_complete_inventory():
    """Generate the complete inventory structure"""
    
    inventory_template = f"""
            # Access Switches (270 devices - completing 300 total with core/dist)
{generate_cisco_access_switches()}

        cisco_routers:
          hosts:
{generate_cisco_routers()}
    
    arista_devices:
      children:
        arista_switches:
          hosts:
{generate_arista_switches()}
    
    juniper_devices:
      children:
        juniper_routers:
          hosts:
{generate_juniper_routers()}
    
    palo_alto_devices:
      children:
        palo_alto_firewalls:
          hosts:
{generate_palo_alto_firewalls()}
    
    fortinet_devices:
      children:
        fortinet_firewalls:
          hosts:
            fw-internal-01:
              ansible_host: 10.5.1.10
              ansible_connection: httpapi
              ansible_httpapi_use_ssl: true
              ansible_httpapi_port: 443
              ansible_httpapi_session_key: "{{ vault_fortigate_api_token }}"
              device_role: internal_firewall
              site: datacenter_01
"""

    return inventory_template

if __name__ == "__main__":
    print(generate_complete_inventory())
