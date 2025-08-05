# Palo Alto Networks Ansible Playbooks - Comprehensive Guide

This directory contains a comprehensive collection of Palo Alto Networks (PAN-OS) Ansible playbooks for enterprise network security automation. These playbooks provide complete coverage of PAN-OS features from basic configuration to advanced threat prevention and SD-WAN deployment.

## Table of Contents

1. [Overview](#overview)
2. [Playbook Descriptions](#playbook-descriptions)
3. [Prerequisites](#prerequisites)
4. [Installation and Setup](#installation-and-setup)
5. [Configuration Variables](#configuration-variables)
6. [Usage Examples](#usage-examples)
7. [Advanced Features](#advanced-features)
8. [Integration Examples](#integration-examples)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Overview

The Palo Alto Networks automation framework provides enterprise-grade security automation with support for:

- **Complete PAN-OS Configuration**: Interfaces, zones, policies, NAT, VPN
- **Advanced Threat Prevention**: WildFire, DNS Security, SSL decryption, behavioral analysis
- **Panorama Management**: Centralized device management, policy distribution, reporting
- **SD-WAN Deployment**: Path selection, QoS, application-based routing
- **Security Orchestration**: Automated threat response, correlation, remediation
- **High Availability**: Active/passive configurations, failover automation

### Supported Platforms

- **PAN-OS Versions**: 9.1, 10.0, 10.1, 10.2, 11.0+
- **Firewall Models**: PA-220, PA-400 Series, PA-800 Series, PA-3000 Series, PA-5000 Series, PA-7000 Series
- **Panorama**: M-100, M-200, M-500, M-600, Panorama Virtual
- **VM-Series**: AWS, Azure, VMware, KVM, OpenStack

## Playbook Descriptions

### Core Configuration Playbooks

#### 1. `panos_enterprise_config.yml`
**Purpose**: Complete enterprise PAN-OS firewall configuration
**Features**:
- Interface configuration (Layer 2/3, management)
- Security zones with protection profiles
- Address objects and groups
- Security policies with advanced features
- NAT policies (SNAT, DNAT, policy-based)
- GlobalProtect VPN configuration
- High availability setup
- Administrator accounts and RBAC
- SNMP and logging configuration
- Certificate management

**Key Components**:
```yaml
# Security Zones
panos_security_zones:
- zone_name: trust
  mode: layer3
  interfaces: [ethernet1/1, ethernet1/2]
  zone_protection_profile: strict
  enable_user_identification: true

# Security Policies  
panos_security_policies:
- rule_name: "Allow-Internal-to-DMZ"
  source_zone: [trust]
  destination_zone: [dmz]
  application: [web-browsing, ssl, ssh]
  action: allow
  profile_setting: default
```

#### 2. `panos_advanced_threat_prevention.yml`
**Purpose**: Advanced threat prevention and security features
**Features**:
- WildFire analysis configuration
- DNS Security with botnet protection
- SSL decryption policies and profiles
- User-ID integration with Active Directory
- Advanced anti-malware with machine learning
- Behavioral analysis and threat correlation
- IoT security (if licensed)
- External threat intelligence feeds
- Custom application signatures
- Log correlation and automated response

**Key Components**:
```yaml
# WildFire Configuration
panos_wildfire_config:
  analysis_profiles:
  - name: "strict-analysis"
    rules:
    - applications: ["any"]
      file_types: ["pe", "pdf", "ms-office", "jar"]
      analysis_type: "public-cloud"

# SSL Decryption
panos_ssl_decryption:
  decryption_policies:
  - rule_name: "decrypt-outbound-enterprise"
    source_zones: [trust]
    dest_zones: [untrust]
    action: decrypt
    decryption_profile: "outbound-decrypt-profile"
```

#### 3. `panos_panorama_management.yml`
**Purpose**: Centralized Panorama management and orchestration
**Features**:
- Device group creation and hierarchy
- Template and template stack management
- Log collector configuration
- Distributed policy management
- Content update scheduling
- Panorama high availability
- Custom reports and dashboards
- API key management
- External services integration

**Key Components**:
```yaml
# Device Groups
panorama_device_groups:
- name: "headquarters"
  devices:
  - serial: "{{ hq_firewall_1_serial }}"
  reference_templates: ["hq-template-stack"]

# Shared Policies
panorama_shared_policies:
- device_group: "shared"
  rule_name: "Allow-DNS"
  source_zone: [trust]
  dest_zone: [untrust]
  application: [dns]
  action: allow
```

#### 4. `panos_sdwan_advanced_networking.yml`
**Purpose**: SD-WAN deployment and advanced networking features
**Features**:
- SD-WAN interface configuration
- Path quality monitoring
- Policy-based forwarding
- Advanced QoS with bandwidth guarantees
- ECMP and load balancing
- Policy-based routing
- Network segmentation and microsegmentation
- Application-based routing
- Branch office IPSec connectivity
- Advanced monitoring and analytics

**Key Components**:
```yaml
# SD-WAN Policies
panos_sdwan_policies:
- name: "critical-app-mpls"
  applications: [oracle, sap, ms-sql-db]
  action:
    forward:
      target: "ethernet1/1"
      monitor:
        ip: "8.8.8.8"

# QoS Profiles
panos_advanced_qos_profiles:
- name: "enterprise-qos-profile"
  aggregate_bandwidth_mbps: 1000
  classes:
  - name: "class1"
    priority: 1
    guaranteed_percentage: 40
```

### Security Operations Playbooks

#### 5. `panos_security_operations.yml`
**Purpose**: Security operations and incident response automation
**Features**:
- Automated threat hunting
- Dynamic security policy updates
- Incident response workflows
- Threat intelligence integration
- Security orchestration and automated response (SOAR)

#### 6. `panos_monitoring_maintenance.yml`
**Purpose**: System monitoring and maintenance automation
**Features**:
- Health checks and diagnostics
- Performance monitoring
- Log analysis and alerting
- Maintenance task automation
- Backup and restore operations

## Prerequisites

### Required Software
- Ansible Core 2.12+ or Ansible 6.0+
- Python 3.8+
- PAN-OS SDK for Python (`pan-os-python`)
- Palo Alto Networks Ansible Collection

### Installation Commands
```bash
# Install Ansible
pip install ansible

# Install PAN-OS Python SDK
pip install pan-os-python

# Install Palo Alto Networks Ansible Collection
ansible-galaxy collection install paloaltonetworks.panos

# Verify installation
ansible-galaxy collection list | grep paloaltonetworks
```

### Network Access Requirements
- HTTPS (TCP 443) access to PAN-OS devices
- SSH (TCP 22) access for device management (optional)
- SNMP (UDP 161) for monitoring (optional)

## Installation and Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd ansible-network-automation
```

### 2. Configure Ansible Vault
Create encrypted variables for sensitive data:
```bash
# Create vault file
ansible-vault create inventories/production/group_vars/vault.yml

# Add sensitive variables
vault_panos_username: admin
vault_panos_password: your_secure_password
vault_panos_api_key: your_api_key
vault_snmp_community_ro: public_readonly
vault_snmp_community_rw: private_readwrite
```

### 3. Update Inventory
Edit `inventories/production/hosts.yml`:
```yaml
all:
  children:
    palo_alto_devices:
      hosts:
        firewall-1:
          ansible_host: 192.168.1.10
        firewall-2:
          ansible_host: 192.168.1.11
    panorama_devices:
      hosts:
        panorama-1:
          ansible_host: 192.168.1.50
```

### 4. Configure Variables
Update device-specific variables in `group_vars/` and `host_vars/`:
```yaml
# group_vars/palo_alto_devices.yml
trust_ip: "10.0.1.1/24"
untrust_ip: "203.0.113.10/30"
dmz_ip: "192.168.100.1/24"
```

## Configuration Variables

### Core Variables (palo_alto_devices.yml)
```yaml
# Connection Settings
panos_provider:
  ip_address: "{{ ansible_host }}"
  username: "{{ vault_panos_username }}"
  password: "{{ vault_panos_password }}"

# Security Zones
panos_security_zones:
- zone_name: trust
  mode: layer3
  interfaces: [ethernet1/1, ethernet1/2]

# Interface Configuration
panos_interface_config:
  l3_interfaces:
  - name: ethernet1/2
    zone_name: trust
    ip: "{{ trust_ip }}"
```

### Advanced Features (pano_advanced_features.yml)
```yaml
# WildFire Configuration
panos_wildfire_config:
  global_settings:
    file_size_limit: 10
    cloud_inline_analysis: yes

# SSL Decryption
panos_ssl_decryption:
  decryption_policies:
  - rule_name: "decrypt-outbound-enterprise"
    action: decrypt

# User-ID Integration
panos_userid_config:
  agents:
  - name: "domain-controller-1"
    host: "10.10.1.100"
```

### Panorama Variables
```yaml
# Device Groups
panorama_device_groups:
- name: "headquarters"
  devices:
  - serial: "123456789"

# Templates
panorama_templates:
- name: "base-template"
  config:
    hostname_template: "$serial"
    domain: "corp.example.com"
```

## Usage Examples

### Basic Deployment
```bash
# Deploy basic firewall configuration
ansible-playbook panos_enterprise_config.yml --limit palo_alto_devices

# Check mode (dry run)
ansible-playbook panos_enterprise_config.yml --limit palo_alto_devices --check

# Deploy specific components
ansible-playbook panos_enterprise_config.yml --tags interfaces,zones
```

### Advanced Threat Prevention
```bash
# Deploy advanced threat prevention
ansible-playbook panos_advanced_threat_prevention.yml --limit palo_alto_devices

# Deploy only WildFire and DNS Security
ansible-playbook panos_advanced_threat_prevention.yml --tags wildfire,dns_security

# Deploy SSL decryption
ansible-playbook panos_advanced_threat_prevention.yml --tags ssl_decryption
```

### Panorama Management
```bash
# Configure Panorama
ansible-playbook panos_panorama_management.yml --limit panorama_devices

# Deploy device groups and templates
ansible-playbook panos_panorama_management.yml --tags device_groups,templates

# Push configuration to managed devices
ansible-playbook panos_panorama_management.yml --tags commit,push
```

### SD-WAN Deployment
```bash
# Deploy SD-WAN configuration
ansible-playbook panos_sdwan_advanced_networking.yml --limit palo_alto_devices

# Configure QoS and traffic shaping
ansible-playbook panos_sdwan_advanced_networking.yml --tags qos,traffic_shaping

# Deploy microsegmentation
ansible-playbook panos_sdwan_advanced_networking.yml --tags microsegmentation
```

### Combined Deployment
```bash
# Master orchestration (all components)
ansible-playbook master_orchestration.yml --limit palo_alto_devices

# Specific vendor deployment
ansible-playbook master_orchestration.yml --tags paloalto_config
```

## Advanced Features

### 1. WildFire Integration
Automated malware analysis and response:
```yaml
panos_wildfire_config:
  analysis_profiles:
  - name: "enterprise-wildfire"
    rules:
    - applications: ["web-browsing", "ssl", "ftp"]
      file_types: ["pe", "pdf", "ms-office", "jar", "apk"]
      direction: "both"
      analysis_type: "public-cloud"
```

### 2. SSL Decryption
Comprehensive SSL/TLS inspection:
```yaml
panos_ssl_decryption:
  decryption_policies:
  - rule_name: "decrypt-enterprise-traffic"
    source_zones: [trust]
    dest_zones: [untrust]
    url_categories: ["business-and-economy"]
    action: decrypt
    decryption_profile: "enterprise-decrypt"
```

### 3. User-ID Integration
Active Directory integration for user-based policies:
```yaml
panos_userid_config:
  agents:
  - name: "dc1-userid"
    host: "10.10.1.100"
    ntlm_auth: yes
    collector_name: "DC1-Collector"
```

### 4. SD-WAN Path Selection
Intelligent application routing:
```yaml
panos_sdwan_policies:
- name: "business-critical-mpls"
  applications: [oracle, sap, ms-exchange]
  action:
    forward:
      target: "ethernet1/1"  # MPLS interface
      monitor:
        ip: "8.8.8.8"
        disable_if_unreachable: yes
```

### 5. Microsegmentation
Zero-trust network segmentation:
```yaml
panos_microsegmentation_policies:
- rule_name: "web-to-db-allow"
  source_zone: [web-zone]
  dest_zone: [db-zone]
  source_ip: [Web-Servers]
  dest_ip: [Database-Servers]
  application: [mysql, oracle]
  action: allow
```

## Integration Examples

### 1. SIEM Integration
Forward logs to SIEM platforms:
```yaml
panos_logging_config:
  log_settings:
    system:
      server_profiles:
      - name: "splunk-syslog"
        server: "10.255.1.102"
        protocol: "SSL"
        port: 6514
        format: "IETF"
```

### 2. Threat Intelligence Feeds
External threat intelligence integration:
```yaml
panos_threat_intelligence:
  external_lists:
  - name: "corporate-threat-feed"
    type: "ip"
    url: "https://threatintel.company.com/feed.txt"
    recurring:
      frequency: "hourly"
```

### 3. Orchestration Integration
SOAR platform integration:
```yaml
panos_log_correlation:
  correlation_rules:
  - name: "malware-detection"
    actions:
    - name: "quarantine-host"
      type: "tagging"
      target: "source-address"
      timeout: 3600
```

## Troubleshooting

### Common Issues

#### 1. Connection Issues
```bash
# Test API connectivity
ansible palo_alto_devices -m panos_op -a "provider='{{ panos_provider }}' cmd='show system info'"

# Verify API key
ansible-vault view inventories/production/group_vars/vault.yml
```

#### 2. Certificate Issues
```bash
# Check certificate validity
openssl x509 -in certificate.pem -text -noout

# Import certificate
ansible-playbook panos_enterprise_config.yml --tags certificates
```

#### 3. Commit Issues
```bash
# Check commit status
ansible palo_alto_devices -m panos_op -a "provider='{{ panos_provider }}' cmd='show jobs all'"

# Force commit
ansible palo_alto_devices -m panos_commit -a "provider='{{ panos_provider }}' sync=true force=true"
```

### Debug Mode
```bash
# Enable verbose output
ansible-playbook panos_enterprise_config.yml -vvv

# Enable debug logging
export ANSIBLE_DEBUG=1
ansible-playbook panos_enterprise_config.yml
```

### Log Analysis
```bash
# Check Ansible logs
tail -f /var/log/ansible.log

# Check PAN-OS system logs
ansible palo_alto_devices -m panos_op -a "provider='{{ panos_provider }}' cmd='show log system recent'"
```

## Best Practices

### 1. Security
- Store sensitive data in Ansible Vault
- Use API keys instead of passwords when possible
- Implement role-based access control
- Regular credential rotation

### 2. Configuration Management
- Use version control for all playbooks
- Test changes in development environment
- Implement configuration backups
- Document all customizations

### 3. Deployment
- Use check mode for validation
- Deploy incrementally with tags
- Monitor device performance during deployment
- Implement rollback procedures

### 4. Monitoring
- Configure comprehensive logging
- Set up alerting for critical events
- Regular health checks
- Performance monitoring

### 5. Maintenance
- Regular content updates
- Certificate management
- License monitoring
- Backup automation

## Advanced Scenarios

### Multi-Site Deployment
```yaml
# Site-specific variables
sites:
  headquarters:
    trust_network: "10.0.0.0/16"
    dmz_network: "192.168.100.0/24"
  branch_office:
    trust_network: "10.1.0.0/16"
    dmz_network: "192.168.101.0/24"
```

### Zero-Touch Provisioning
```yaml
# Automated device onboarding
panos_ztp_config:
  bootstrap_profile: "enterprise-bootstrap"
  device_certificate: "auto-generate"
  panorama_servers: ["panorama1.corp.com", "panorama2.corp.com"]
```

### Disaster Recovery
```yaml
# HA failover configuration
panos_ha_config:
  mode: "active-passive"
  sync_enabled: yes
  preemption: yes
  heartbeat_backup: "ethernet1/8"
```

## Support and Documentation

### Resources
- [Palo Alto Networks Documentation](https://docs.paloaltonetworks.com/)
- [Ansible Palo Alto Collection](https://docs.ansible.com/ansible/latest/collections/paloaltonetworks/panos/)
- [PAN-OS SDK Documentation](https://pan-os-python.readthedocs.io/)

### Community
- [Palo Alto Networks Community](https://live.paloaltonetworks.com/)
- [Ansible Community](https://docs.ansible.com/ansible/latest/community/)

### Getting Help
For issues with these playbooks:
1. Check the troubleshooting section
2. Review Ansible and PAN-OS logs
3. Test with a minimal configuration
4. Consult vendor documentation
5. Reach out to community forums

---

**Note**: These playbooks are provided as examples and should be thoroughly tested in a development environment before production use. Always follow your organization's change management procedures and security policies.
