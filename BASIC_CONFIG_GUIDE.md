# Network Vendor Basic Configuration Examples

This directory contains comprehensive basic configuration examples for all major network vendors supported by our Ansible automation framework. These playbooks provide standardized, production-ready configurations that can be deployed across heterogeneous network environments.

## Overview

Our multi-vendor automation framework supports **661 devices** across multiple vendor platforms, providing consistent management and configuration standards regardless of the underlying hardware platform.

### Supported Vendors

- **Cisco** - IOS, IOS-XE, NX-OS, IOS-XR platforms
- **Juniper** - JunOS (EX, QFX, SRX, MX, PTX series)
- **Arista** - EOS (7050, 7150, 7280, 7300, 7500, 7800 series)
- **Fortinet** - FortiGate firewalls (all series)
- **Palo Alto** - PAN-OS firewalls (PA-Series, VM-Series)

## Playbook Structure

### Multi-Vendor Unified Playbook
- **`multi_vendor_basic_config.yml`** - Universal playbook that automatically detects vendor platform and applies appropriate configurations
- **`multi_vendor_basic_config.yml` (variables)** - Centralized variable definitions with vendor-specific mappings

### Vendor-Specific Playbooks
- **`cisco_basic_config.yml`** - Cisco IOS/IOS-XE/NX-OS/IOS-XR configurations
- **`juniper_basic_config.yml`** - Juniper JunOS configurations
- **`arista_basic_config.yml`** - Arista EOS configurations
- **`fortinet_basic_config.yml`** - FortiGate FortiOS configurations
- **`paloalto_basic_config.yml`** - Palo Alto PAN-OS configurations

## Configuration Features

### System Management
- **Hostname Configuration** - Standardized device naming
- **Domain Settings** - DNS domain and name server configuration
- **Time Synchronization** - NTP server configuration with authentication
- **User Management** - Local user accounts with role-based access
- **SSH Security** - Hardened SSH settings with key-based authentication

### Network Services
- **SNMP Monitoring** - Community strings, trap destinations, system information
- **Logging** - Centralized syslog configuration with severity levels
- **Management Interface** - Dedicated management connectivity
- **Access Control** - Security policies and access restrictions

### Security Baseline
- **Authentication** - Multi-factor authentication support where available
- **Authorization** - Role-based access control (RBAC)
- **Encryption** - Secure protocols and cipher suites
- **Monitoring** - Security event logging and alerting

### Vendor-Specific Features

#### Cisco Platforms
- **IOS/IOS-XE Features**
  - Console and VTY line security
  - Crypto key generation for SSH
  - Access control lists for management
  - Service hardening and security features

- **NX-OS Features**
  - Feature enablement (SSH, SCP, NTP)
  - Management VRF configuration
  - User roles and authentication

- **IOS-XR Features**
  - Admin plane security
  - Commit model configuration
  - Advanced logging and monitoring

#### Juniper JunOS
- **System Security**
  - Firewall filters for routing engine protection
  - SSH hardening with modern crypto algorithms
  - Login class definitions and idle timeouts

- **Network Features**
  - IRB interfaces for L3 switching
  - VLAN configuration with L3 gateways
  - SNMP client lists and trap configuration

#### Arista EOS
- **Data Center Features**
  - Management VRF isolation
  - MLAG configuration for high availability
  - CloudVision Portal (CVP) integration
  - Control plane policing (CoPP)

- **API Management**
  - HTTP-Commands API configuration
  - Management SSH with connection limits
  - Certificate-based authentication

#### Fortinet FortiGate
- **Security Platform**
  - VDOM support for multi-tenancy
  - Security policies and NAT rules
  - Address and service objects
  - SSL/TLS inspection profiles

- **Network Services**
  - Static routing configuration
  - Interface access permissions
  - System replacement messages (banners)

#### Palo Alto PAN-OS
- **Next-Generation Firewall**
  - Security zones and policies
  - Application-based rules
  - Threat prevention profiles
  - User identification services

- **Management**
  - Panorama integration
  - Administrator roles and profiles
  - Certificate management
  - API access control

## Deployment Instructions

### Prerequisites
1. **Ansible Core** 2.12+ with required collections installed
2. **Inventory File** with device groupings by vendor
3. **Vault Encrypted** credentials for each platform
4. **Network Connectivity** to management interfaces

### Running Multi-Vendor Deployment
```bash
# Deploy to all supported vendors
ansible-playbook -i inventory/production multi_vendor_basic_config.yml --ask-vault-pass

# Deploy to specific vendor group
ansible-playbook -i inventory/production multi_vendor_basic_config.yml --limit cisco_devices --ask-vault-pass

# Deploy with specific tags
ansible-playbook -i inventory/production multi_vendor_basic_config.yml --tags "system,users,ntp" --ask-vault-pass
```

### Running Vendor-Specific Deployments
```bash
# Cisco devices
ansible-playbook -i inventory/production cisco_basic_config.yml --ask-vault-pass

# Juniper devices
ansible-playbook -i inventory/production juniper_basic_config.yml --ask-vault-pass

# Arista devices
ansible-playbook -i inventory/production arista_basic_config.yml --ask-vault-pass

# FortiGate firewalls
ansible-playbook -i inventory/production fortinet_basic_config.yml --ask-vault-pass

# Palo Alto firewalls
ansible-playbook -i inventory/production paloalto_basic_config.yml --ask-vault-pass
```

## Variable Configuration

### Required Variables (All Vendors)
```yaml
# System Settings
domain_name: "company.local"
primary_dns: "8.8.8.8"
secondary_dns: "8.8.4.4"
timezone: "America/New_York"

# Management Network
mgmt_network: "10.100.0.0/16"
nms_network: "10.100.1.0/24"

# Local Users
local_users:
  - username: "netadmin"
    password: "{{ vault_netadmin_password }}"
    privilege: 15
    role: "network-admin"
    ssh_key: "ssh-rsa AAAAB3NzaC1yc2E..."

# NTP Servers
ntp_servers:
  - server: "pool.ntp.org"
    prefer: true
    key_id: 1
    key: "{{ vault_ntp_key }}"

# SNMP Configuration
snmp_ro_community: "{{ vault_snmp_ro_community }}"
snmp_rw_community: "{{ vault_snmp_rw_community }}"
snmp_location: "Data Center A"
snmp_contact: "network-team@company.com"

snmp_hosts:
  - host: "10.100.1.10"
    version: "2c"
    community: "{{ vault_snmp_ro_community }}"

# Syslog Servers
syslog_servers:
  - server: "10.100.1.20"
    port: 514
    protocol: "udp"
    level: "informational"
```

### Vendor-Specific Variables

#### Cisco Variables
```yaml
# Enable Secret
vault_cisco_enable_secret: "{{ vault_enable_secret }}"

# Management Interface
mgmt_interface: "GigabitEthernet0/0"
mgmt_ip: "10.100.0.10"
mgmt_mask: "24"
default_gateway: "10.100.0.1"

# SSH Settings
ssh_timeout: 60
ssh_retries: 3
rsa_key_size: 2048
```

#### Juniper Variables
```yaml
# Root Password
vault_juniper_root_password: "{{ vault_root_password }}"

# Management Interface
mgmt_interface: "fxp0"
web_mgmt_interface: "fxp0.0"

# Security Settings
admin_idle_timeout: 30
operator_idle_timeout: 15
readonly_idle_timeout: 10
```

#### Arista Variables
```yaml
# Enable Secret
vault_arista_enable_secret: "{{ vault_enable_secret }}"

# Management VRF
mgmt_vrf: "MGMT"
mgmt_interface: "Management1"

# MLAG Configuration (if enabled)
mlag_enabled: true
mlag_domain: "MLAG_DOMAIN1"
mlag_vlan: 4094
mlag_local_ip: "10.255.255.1"
mlag_peer_ip: "10.255.255.2"
```

#### FortiGate Variables
```yaml
# VDOM Configuration
fortios_vdom: "root"

# Admin Users
admin_users:
  - username: "fgtadmin"
    password: "{{ vault_fgt_admin_password }}"
    profile: "super_admin"
    trusted_host1: "10.100.0.0 255.255.0.0"

# Interfaces
interfaces:
  - name: "port1"
    ip: "10.100.0.10/24"
    access: ["ping", "https", "ssh", "snmp"]
    description: "Management Interface"
```

#### Palo Alto Variables
```yaml
# Management Profile
mgmt_profile_name: "MGMT-Profile"
mgmt_permitted_ips: ["10.100.0.0/16"]

# Security Zones
security_zones:
  - name: "TRUST"
    mode: "layer3"
    interfaces: ["ethernet1/1"]
  - name: "UNTRUST"
    mode: "layer3"
    interfaces: ["ethernet1/2"]

# Security Policies
security_policies:
  - name: "Allow-Internal"
    source_zones: ["TRUST"]
    destination_zones: ["UNTRUST"]
    action: "allow"
    log_end: true
```

## Integration with Advanced Features

These basic configuration playbooks integrate seamlessly with our advanced automation:

### Data Center Automation
- **EVPN-VXLAN** deployment builds upon basic L3 interface configuration
- **MLAG** configurations extend basic interface and VLAN settings
- **Anycast Gateways** utilize standardized SVI configurations

### Service Provider Features
- **eBGP** peering leverages basic routing and interface configuration
- **MPLS-VPN** services build on established management and security baselines
- **Traffic Engineering** extends basic IGP and interface configurations

### Security Integration
- **Firewall Policies** utilize standardized address and service objects
- **VPN Connectivity** builds on established crypto and routing foundations
- **Threat Prevention** extends basic logging and monitoring configurations

## Verification and Validation

Each playbook includes comprehensive verification tasks:

### System Verification
- Device facts gathering and hardware status
- Configuration syntax and consistency checks
- Service status and operational state validation

### Connectivity Testing
- Management interface reachability
- NTP synchronization status
- DNS resolution functionality

### Security Validation
- User authentication and authorization testing
- SSH connectivity with key-based authentication
- SNMP access and trap functionality

### Reporting
- Detailed configuration status reports
- Deployment success/failure summaries
- Hardware and software inventory updates

## Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Test management connectivity
ansible all -i inventory/production -m ping --ask-vault-pass

# Validate credentials
ansible-playbook -i inventory/production test_connectivity.yml --ask-vault-pass
```

#### Configuration Conflicts
```bash
# Check for syntax errors
ansible-playbook -i inventory/production multi_vendor_basic_config.yml --syntax-check

# Dry run deployment
ansible-playbook -i inventory/production multi_vendor_basic_config.yml --check --ask-vault-pass
```

#### Vendor-Specific Issues
- **Cisco**: Check feature licensing and platform capabilities
- **Juniper**: Verify NETCONF connectivity and commit permissions
- **Arista**: Ensure proper API access and certificate validation
- **Fortinet**: Validate VDOM permissions and administrative access
- **Palo Alto**: Check device registration and licensing status

### Best Practices

1. **Staged Deployment** - Test configurations in lab environment first
2. **Backup Configurations** - Always backup before making changes
3. **Gradual Rollout** - Deploy to small groups before full deployment
4. **Monitoring** - Continuously monitor device status during deployment
5. **Documentation** - Maintain accurate inventory and configuration records

## Support Matrix

| Vendor | Platform | Ansible Collection | Minimum Version | Connection Type |
|--------|----------|-------------------|-----------------|-----------------|
| Cisco | IOS/IOS-XE | cisco.ios | 4.0.0 | network_cli |
| Cisco | NX-OS | cisco.nxos | 4.0.0 | network_cli |
| Cisco | IOS-XR | cisco.iosxr | 4.0.0 | network_cli |
| Juniper | JunOS | junipernetworks.junos | 4.0.0 | netconf |
| Arista | EOS | arista.eos | 6.0.0 | network_cli |
| Fortinet | FortiOS | fortinet.fortios | 2.2.0 | httpapi |
| Palo Alto | PAN-OS | paloaltonetworks.panos | 2.14.0 | local |

## Security Considerations

### Credential Management
- All passwords stored in Ansible Vault
- SSH keys managed through secure key distribution
- Regular credential rotation policies

### Network Segmentation
- Management traffic isolated to dedicated VRF/VLAN
- Production and management networks properly segmented
- Access control lists restricting management access

### Audit and Compliance
- All configuration changes logged and tracked
- Role-based access control for administrative functions
- Regular security assessments and vulnerability scanning

---

For additional support or feature requests, contact the Network Automation Team.
