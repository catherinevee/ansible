# Network Automation with Ansible

Ansible-based network automation framework for managing multi-vendor network infrastructure, security compliance, and operational workflows across 661 production devices.

## Architecture

Automation framework supporting:

- **Multi-vendor platforms**: Cisco IOS/IOS-XE, Arista EOS, Juniper Junos, Palo Alto PAN-OS, Fortinet FortiOS
- **State management**: Declarative configuration with idempotent operations  
- **Security compliance**: Encrypted vault storage, audit trails, hardening baselines
- **Operational reporting**: HTML compliance reports with scoring metrics
- **Disaster recovery**: Automated config backup/restore with validation
- **Workflow orchestration**: Site-wide deployment coordination

## Directory Structure

```
ansible/
├── ansible.cfg                          # Network timeouts and connection settings
├── inventories/                         # Production device inventory
│   └── production/
│       ├── hosts_complete_enterprise.yml # 661 devices across 5 vendors
├── group_vars/                          # Configuration variables by device group
│   ├── multi_vendor_basic_config.yml   # Common baseline settings
│   ├── cisco_datacenter_config.yml     # EVPN-VXLAN fabric variables
│   ├── cisco_sp_config.yml             # Service provider BGP/MPLS config
│   └── juniper_devices/
│       └── juniper_mx_acx_config.yml   # MX/ACX router variables
├── playbooks/                           # Automation workflows
│   ├── site.yml                        # Main orchestration playbook
│   ├── multi_vendor_basic_config.yml   # Cross-vendor baseline config
│   ├── cisco_basic_config.yml          # Cisco IOS/NX-OS baseline
│   ├── juniper_basic_config.yml        # Junos device baseline
│   ├── arista_basic_config.yml         # EOS switch baseline
│   ├── fortinet_basic_config.yml       # FortiGate firewall baseline
│   ├── paloalto_basic_config.yml       # PAN-OS firewall baseline
│   ├── deploy_vlans.yml                # VLAN provisioning and EVPN setup
│   ├── deploy_interfaces.yml           # Interface configuration
│   ├── deploy_bgp.yml                  # BGP routing protocols
│   ├── deploy_acls.yml                 # Access control lists
│   ├── deploy_security_policies.yml    # Firewall and security rules
│   ├── backup_configs.yml              # Configuration backup jobs
│   ├── network_health_check.yml        # Operational status monitoring
│   ├── network_troubleshooting.yml     # Diagnostic workflows
│   ├── compliance_audit.yml            # Security posture validation
│   └── disaster_recovery.yml           # Backup/restore procedures
├── roles/                               # Reusable configuration modules
│   ├── cisco_base_config/              # Cisco device hardening
│   ├── panos_security_baseline/        # PAN-OS security templates
│   ├── network_monitoring/             # SNMP/syslog setup
│   └── security_hardening/             # Network security hardening
├── templates/                           # Jinja2 reporting templates
├── BASIC_CONFIG_GUIDE.md               # Basic configuration guide for new setups
├── ENTERPRISE_FRAMEWORK_COMPLETE.md   # Framework documentation and deployment notes
├── config_standards.yml               # Configuration compliance standards
└── playbooks/
    └── PANOS_ADVANCED_GUIDE.md        # Palo Alto automation guide
│   ├── deployment_summary.j2           # Deployment summary reports
│   ├── bgp_deployment_report.j2        # BGP deployment reports
│   ├── interface_deployment_report.j2  # Interface deployment reports
│   ├── acl_deployment_report.j2        # ACL deployment reports
│   ├── network_diagnostics_report.j2   # Network diagnostic reports
│   ├── compliance_audit_report.j2      # Compliance audit reports
│   ├── disaster_recovery_report.j2     # Disaster recovery reports
│   ├── health_report.j2                # Health check reports
│   └── orchestration_summary.j2        # Orchestration summary reports
├── vault/                               # Encrypted credential storage
│   └── secrets.yml                     # Encrypted device credentials
├── scripts/                             # Utility scripts and tools
│   ├── generate_complete_inventory.py  # Complete inventory generator
│   ├── discover_devices.py             # Network device discovery
│   └── validate_config.py              # Configuration validation
├── reports/                             # Generated reports directory (empty)
├── backups/                             # Configuration backups (empty)
├── config_standards.yml                # Network configuration standards
├── requirements.txt                     # Python dependencies
└── ENTERPRISE_FRAMEWORK_COMPLETE.md    # Complete deployment guide
```

## Quick Start

### Prerequisites

```bash
# Install required Ansible collections
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install arista.eos
ansible-galaxy collection install junipernetworks.junos
ansible-galaxy collection install paloaltonetworks.panos
ansible-galaxy collection install fortinet.fortios

# Install Python dependencies
pip install -r requirements.txt
```

### Initial Setup

1. **Configure Credentials**:
   ```bash
   # Create and encrypt vault file
   ansible-vault create vault/secrets.yml
   ```

2. **Update Inventory**:
   - Edit `inventories/production/hosts_complete_enterprise.yml` with your device information
   - Configure group variables for your environment

3. **Test Connectivity**:
   ```bash
   ansible all -m ping -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass
   ```

### Using the Python Scripts

The included Python scripts simplify common Ansible operations:

#### **Interactive Mode**
```powershell
# Windows PowerShell
.\ansible.ps1 interactive

# Direct Python execution
python scripts/ansible_master.py --interactive
```

#### **Command Line Operations**
```powershell
# Run playbook with monitoring  
.\ansible.ps1 run site.yml production

# Generate new playbook
.\ansible.ps1 generate

# Run tests
.\ansible.ps1 test

# Check connectivity
python scripts/ansible_runner.py ping --inventory production
```

## How to Use Ansible

### Understanding Ansible Basics

#### **Inventory Files**
Inventory files define which devices Ansible manages:

```yaml
# inventories/production/hosts.yml
all:
  children:
    cisco_devices:
      hosts:
        sw-core-01:
          ansible_host: 192.168.1.10
          ansible_network_os: ios
        rtr-edge-01:
          ansible_host: 192.168.1.20
          ansible_network_os: ios
    arista_devices:
      hosts:
        sw-leaf-01:
          ansible_host: 192.168.1.30
          ansible_network_os: eos
```

#### **Playbooks Structure**
Playbooks define automation tasks:

```yaml
# playbooks/basic_config.yml
---
- name: Configure Basic Settings
  hosts: cisco_devices
  gather_facts: false
  tasks:
    - name: Set hostname
      cisco.ios.ios_config:
        lines:
          - hostname {{ inventory_hostname }}
        save_when: changed
```

#### **Variables and Group Variables**
Define configuration data in group_vars:

```yaml
# group_vars/cisco_devices.yml
snmp_community: "public"
ntp_servers:
  - "pool.ntp.org"
  - "time.google.com"
dns_servers:
  - "8.8.8.8"
  - "8.8.4.4"
```

### Essential Ansible Commands

#### **Basic Playbook Execution**
```bash
# Run a playbook
ansible-playbook playbooks/site.yml -i inventories/production/hosts.yml

# Run with specific inventory
ansible-playbook playbooks/backup_configs.yml -i inventories/staging/hosts.yml

# Run in check mode (dry run)
ansible-playbook playbooks/deploy_vlans.yml -i inventories/production/hosts.yml --check

# Run with extra variables
ansible-playbook playbooks/deploy_bgp.yml -i inventories/production/hosts.yml -e "bgp_asn=65001"
```

#### **Target Specific Hosts**
```bash
# Limit to specific hosts
ansible-playbook playbooks/health_check.yml -i inventories/production/hosts.yml --limit "sw-core-01,sw-core-02"

# Limit to host groups
ansible-playbook playbooks/security_hardening.yml -i inventories/production/hosts.yml --limit "cisco_routers"

# Limit by pattern
ansible-playbook playbooks/firmware_update.yml -i inventories/production/hosts.yml --limit "sw-*"
```

#### **Ad-hoc Commands**
```bash
# Check connectivity
ansible all -m ping -i inventories/production/hosts.yml

# Gather facts
ansible cisco_devices -m ios_facts -i inventories/production/hosts.yml

# Execute commands
ansible cisco_routers -m ios_command -a "commands='show version'" -i inventories/production/hosts.yml

# Copy files
ansible all -m copy -a "src=config.txt dest=/tmp/config.txt" -i inventories/production/hosts.yml
```

#### **Inventory Management**
```bash
# List all hosts
ansible-inventory -i inventories/production/hosts.yml --list

# Show host details
ansible-inventory -i inventories/production/hosts.yml --host sw-core-01

# Graph inventory structure
ansible-inventory -i inventories/production/hosts.yml --graph
```

### Additional Ansible Operations

#### **Using Tags**
```bash
# Run only tasks with specific tags
ansible-playbook playbooks/site.yml -i inventories/production/hosts.yml --tags "backup,health_check"

# Skip specific tags
ansible-playbook playbooks/site.yml -i inventories/production/hosts.yml --skip-tags "firmware_update"

# List available tags
ansible-playbook playbooks/site.yml -i inventories/production/hosts.yml --list-tags
```

#### **Vault Operations**
```bash
# Create encrypted file
ansible-vault create vault/secrets.yml

# Edit encrypted file
ansible-vault edit vault/secrets.yml

# View encrypted file
ansible-vault view vault/secrets.yml

# Encrypt existing file
ansible-vault encrypt group_vars/production/passwords.yml

# Decrypt file
ansible-vault decrypt vault/secrets.yml

# Change vault password
ansible-vault rekey vault/secrets.yml
```

#### **Using Multiple Inventories**
```bash
# Combine multiple inventory sources
ansible-playbook playbooks/multi_site.yml -i inventories/site1/hosts.yml -i inventories/site2/hosts.yml

# Use dynamic inventory
ansible-playbook playbooks/cloud_deploy.yml -i inventory_script.py
```

#### **Parallel Execution Control**
```bash
# Control parallelism
ansible-playbook playbooks/mass_config.yml -i inventories/production/hosts.yml --forks 20

# Serial execution (one host at a time)
ansible-playbook playbooks/firmware_update.yml -i inventories/production/hosts.yml --serial 1

# Batch execution (specific number)
ansible-playbook playbooks/rolling_update.yml -i inventories/production/hosts.yml --serial 25%
```

### Network-Specific Ansible Usage

#### **Network Device Connections**
```yaml
# Connection types for different vendors
vars:
  # Cisco IOS/NX-OS
  ansible_connection: network_cli
  ansible_network_os: ios
  ansible_user: admin
  ansible_password: "{{ vault_password }}"
  
  # Arista EOS (HTTPS API)
  ansible_connection: httpapi
  ansible_network_os: eos
  ansible_httpapi_use_ssl: true
  
  # Juniper Junos (NETCONF)
  ansible_connection: netconf
  ansible_network_os: junos
```

#### **Common Network Tasks**
```bash
# Backup configurations
ansible-playbook playbooks/backup_configs.yml -i inventories/production/hosts.yml

# Deploy VLANs
ansible-playbook playbooks/deploy_vlans.yml -i inventories/production/hosts.yml -e "vlan_id=100 vlan_name=PRODUCTION"

# Update firmware
ansible-playbook playbooks/firmware_update.yml -i inventories/production/hosts.yml --limit "test_devices" --check

# Security compliance check
ansible-playbook playbooks/compliance_audit.yml -i inventories/production/hosts.yml
```

#### **Error Handling and Debugging**
```bash
# Verbose output levels
ansible-playbook playbooks/debug_issues.yml -v      # Basic verbose
ansible-playbook playbooks/debug_issues.yml -vv     # More verbose
ansible-playbook playbooks/debug_issues.yml -vvv    # Very verbose
ansible-playbook playbooks/debug_issues.yml -vvvv   # Debug level

# Continue on errors
ansible-playbook playbooks/mass_update.yml --ignore-errors

# Start at specific task
ansible-playbook playbooks/long_playbook.yml --start-at-task "Configure SNMP"

# Use step mode (confirm each task)
ansible-playbook playbooks/critical_update.yml --step
```

### Python Script Integration

#### **Playbook Execution**
```bash
# Run with performance monitoring
python scripts/ansible_runner.py playbook site.yml --inventory production --verbose 2

# Generate performance reports
python scripts/performance_monitor.py test backup_configs.yml --iterations 3 --save backup_perf.json

# Full testing suite
python scripts/ansible_tester.py suite --inventory production --tests syntax connectivity dry_run
```

#### **Dynamic Playbook Generation**
```bash
# Interactive playbook creation
python scripts/playbook_generator.py interactive

# Generate specific playbook types
python scripts/playbook_generator.py generate --type security_hardening --devices cisco_ios arista_eos --name security_audit_2025

# List available templates
python scripts/playbook_generator.py list
```

#### **Vault Management**
```bash
# Create vault with template
python scripts/vault_manager.py create vault/api_keys.yml --template api_keys

# Encrypt multiple files
python scripts/vault_manager.py encrypt group_vars/production/*.yml

# Show vault status
python scripts/vault_manager.py status
```

## Core Operations

### Common Ansible Workflows

#### **Daily Operations Workflow**
```bash
# 1. Check system health
python scripts/ansible_runner.py ping --inventory production

# 2. Run health checks
ansible-playbook playbooks/network_health_check.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 3. Create configuration backups
ansible-playbook playbooks/backup_configs.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 4. Generate reports
python scripts/ansible_master.py --connectivity --inventory production
```

#### **Change Management Workflow**
```bash
# 1. Test changes in dry-run mode
ansible-playbook playbooks/deploy_vlans.yml --check -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 2. Test on limited hosts first
ansible-playbook playbooks/deploy_vlans.yml --limit "test-sw-01" -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 3. Deploy to production with monitoring
python scripts/performance_monitor.py monitor ansible-playbook playbooks/deploy_vlans.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 4. Verify deployment
ansible-playbook playbooks/network_health_check.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass
```

#### **Troubleshooting Workflow**
```bash
# 1. Gather diagnostic information
ansible-playbook playbooks/network_troubleshooting.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 2. Check specific device connectivity
ansible-playbook playbooks/network_health_check.yml --limit "problematic-device" -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# 3. Run tests
python scripts/ansible_tester.py suite --inventory production --tests connectivity syntax

# 4. Generate detailed reports
python scripts/ansible_master.py --interactive  # Select Reports option
```

### Network Health Monitoring
```bash
# Health check
ansible-playbook playbooks/network_health_check.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# Specific device group health check
ansible-playbook playbooks/network_health_check.yml -i inventories/production/hosts_complete_enterprise.yml -l cisco_switches --ask-vault-pass
```

### Configuration Deployment
```bash
# Deploy VLANs across switching infrastructure
ansible-playbook playbooks/deploy_vlans.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# Deploy BGP routing configuration
ansible-playbook playbooks/deploy_bgp.yml -i inventories/production/hosts_complete_enterprise.yml -l routers --ask-vault-pass

# Deploy security policies
ansible-playbook playbooks/deploy_security_policies.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass
```

### Compliance Auditing
```bash
# Full compliance audit
ansible-playbook playbooks/compliance_audit.yml -i inventories/production/hosts_complete_enterprise.yml --ask-vault-pass

# Security-focused audit
ansible-playbook playbooks/compliance_audit.yml -i inventories/production/hosts_complete_enterprise.yml -e "audit_scope=security" --ask-vault-pass
```

### Disaster Recovery Operations
```bash
# Create configuration backups
ansible-playbook playbooks/disaster_recovery.yml -i inventories/production/hosts_complete_enterprise.yml -e "dr_operation=backup" --ask-vault-pass

# Test DR procedures
ansible-playbook playbooks/disaster_recovery.yml -i inventories/production/hosts_complete_enterprise.yml -e "dr_operation=test" --ask-vault-pass

# Execute failover
ansible-playbook playbooks/disaster_recovery.yml -i inventories/production/hosts_complete_enterprise.yml -e "dr_operation=failover" --ask-vault-pass
```

### Orchestrated Operations
```bash
# Master orchestration - validation mode
ansible-playbook playbooks/orchestration.yml -i inventories/production/hosts_complete_enterprise.yml -e "mode=validate" --ask-vault-pass

# Master orchestration - audit mode
ansible-playbook playbooks/orchestration.yml -i inventories/production/hosts_complete_enterprise.yml -e "mode=audit" --ask-vault-pass

# Master orchestration - deployment mode
ansible-playbook playbooks/orchestration.yml -i inventories/production/hosts_complete_enterprise.yml -e "mode=deploy phase=vlans" --ask-vault-pass
```

## Extended Configuration

### Custom Variables

Configure environment-specific settings in group_vars:

```yaml
# group_vars/cisco_devices.yml
cisco_snmp_community: "your_community_string"
cisco_ntp_servers:
  - "ntp1.example.com"
  - "ntp2.example.com"

# Custom VLAN configurations
vlans:
  - id: 100
    name: "PRODUCTION"
    state: present
  - id: 200
    name: "DEVELOPMENT"
    state: present
```

### Security Hardening

Enable security hardening:

```yaml
# group_vars/all.yml
security_hardening_enabled: true
enable_ssh_version2_only: true
disable_telnet: true
enable_aaa_authentication: true
configure_login_banners: true
```

### Monitoring Integration

Configure external monitoring systems:

```yaml
# group_vars/all.yml
snmp_monitoring:
  enabled: true
  community: "!vault |..."
  trap_servers:
    - "monitoring.example.com"

syslog_monitoring:
  enabled: true
  servers:
    - host: "syslog.example.com"
      port: 514
```

## Reporting and Analytics

### Generated Reports

All operations generate reports:

- **HTML Reports**: Interactive compliance dashboards with scoring
- **Text Reports**: Detailed operational summaries
- **JSON Analytics**: Structured data for integration with monitoring systems

### Report Locations

- Compliance Reports: `reports/compliance_<device>_<date>.html`
- Health Check Reports: `reports/health_<device>_<date>.txt`
- DR Reports: `reports/dr_report_<device>_<date>.txt`
- Orchestration Summaries: `reports/orchestration_<mode>_<date>.txt`

## Security Features

### Credential Management
- All passwords encrypted with ansible-vault
- No hardcoded credentials in configurations  
- Support for certificate-based authentication

### Secure Communications
- SSH version 2 enforcement
- HTTPS/TLS for API communications
- Connection encryption for all protocols

### Audit Trail
- Detailed logging of all operations
- Change tracking and version control integration
- Compliance reporting with evidence collection

## Best Practices

### Ansible Development Guidelines

These patterns emerged from managing production networks with frequent changes and strict compliance requirements.

#### **Playbook Organization**
```yaml
# Use descriptive names and clear task structure
# This helps during 3am troubleshooting calls
---
- name: Configure Network Security Baseline
  hosts: network_devices
  gather_facts: false  # Skip facts gathering for network devices - they don't support it
  vars:
    security_banner: |
      ******************************************
      * Authorized access only               *
      * All activity monitored and recorded  *
      ******************************************
  
  tasks:
    - name: Apply login banner
      cisco.ios.ios_banner:
        banner: login
        text: "{{ security_banner }}"
        state: present
      when: ansible_network_os == "ios"
      
    - name: Disable unused services  # Common security requirement
      cisco.ios.ios_config:
        lines:
          - no ip http server
          - no ip http secure-server
        save_when: changed  # Only save if changes were made
      when: ansible_network_os == "ios"
```

#### **Error Handling Patterns**
```yaml
# Use blocks for error handling - learned this the hard way after late-night rollbacks
tasks:
  - name: Configuration deployment block
    block:
      - name: Deploy VLAN configuration
        cisco.ios.ios_vlans:
          config:
            - vlan_id: "{{ vlan.id }}"
              name: "{{ vlan.name }}"
              state: active
        loop: "{{ vlans }}"
        loop_control:
          loop_var: vlan
          
    rescue:
      - name: Log configuration failure
        debug:
          msg: "VLAN configuration failed for {{ inventory_hostname }}"
          
      - name: Attempt rollback  # Because production networks don't forgive mistakes
        cisco.ios.ios_config:
          lines:
            - no vlan {{ vlan.id }}
          save_when: changed
        loop: "{{ vlans }}"
        loop_control:
          loop_var: vlan
        ignore_errors: true  # Continue even if rollback fails
        
    always:
      - name: Generate deployment report  # Always document what happened
        template:
          src: deployment_report.j2
          dest: "./reports/{{ inventory_hostname }}_deployment.txt"
        delegate_to: localhost
```

#### **Variable Management**
```yaml
# Use group_vars for device-specific settings
# group_vars/cisco_switches/main.yml
switch_config:
  spanning_tree:
    mode: rapid-pvst
    portfast_default: true  # Enable portfast by default - saves time during deployments
  snmp:
    community: "{{ vault_snmp_community }}"  # Always use vault for secrets
    location: "{{ site_location }}"
    contact: "{{ admin_contact }}"
    
# host_vars/sw-core-01.yml - for device-specific overrides
device_specific:
  management_ip: "192.168.1.10"
  mgmt_vlan: 100
  uplink_interfaces:  # Document critical interfaces
    - GigabitEthernet0/1
    - GigabitEthernet0/2
```

#### **Idempotency Patterns**
```yaml
# Ensure tasks are idempotent - can run multiple times safely
- name: Configure VLANs (idempotent)
  cisco.ios.ios_vlans:
    config:
      - vlan_id: 100
        name: PRODUCTION
        state: active
      - vlan_id: 200
        name: DEVELOPMENT
        state: active
    state: merged  # Only add/modify, don't remove existing VLANs

# Use proper state management - avoid unexpected removals
- name: Ensure interface is configured
  cisco.ios.ios_interfaces:
    config:
      - name: GigabitEthernet0/1
        description: "Uplink to Core"
        enabled: true
        speed: 1000
        duplex: full
    state: merged  # Much safer than 'replaced' in production
```

### Change Management
1. Always test in development environment first - production surprises hurt
2. Create configuration backups before changes - saved us multiple times
3. Use serial execution for critical deployments - rolling updates prevent outages
4. Implement proper rollback procedures - because things go wrong

### Error Handling
- All playbooks include error handling - learned from painful experience
- Failed operations trigger automatic rollback - minimizes downtime
- Detailed error logging for troubleshooting - helps with 3am calls

### Performance Optimization
- Parallel execution where safe - but not for core switches
- Connection persistence for efficiency - reduces SSH overhead
- Fact caching to reduce overhead - network devices are slow

## Troubleshooting

### Common Ansible Issues and Solutions

#### **Connection Problems**

**Issue**: SSH connection timeouts
```bash
# Error: "SSH connection timeout"
# Solution: Increase timeout values
```

**Fix in ansible.cfg**:
```ini
[defaults]
timeout = 60
host_key_checking = False

[ssh_connection]
ssh_args = -o ConnectTimeout=60 -o ConnectionAttempts=3
pipelining = True
```

**Issue**: Authentication failures
```bash
# Error: "Authentication failed"
# Check credentials and connectivity
ansible-vault view vault/secrets.yml
ansible all -m ping --ask-vault-pass -vvv
```

**Issue**: Network device connection failures
```bash
# Error: "Unable to connect to network device"
# Test individual device connectivity
ansible sw-core-01 -m ios_facts -i inventories/production/hosts.yml --ask-vault-pass -vvv

# Verify network_cli settings
ansible-inventory -i inventories/production/hosts.yml --host sw-core-01
```

#### **Playbook Execution Issues**

**Issue**: Module not found errors
```bash
# Error: "Module cisco.ios.ios_config not found"
# Install missing collections
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install arista.eos
ansible-galaxy collection install junipernetworks.junos

# List installed collections
ansible-galaxy collection list
```

**Issue**: Variable undefined errors
```bash
# Error: "Variable 'vault_password' is undefined"
# Check variable definitions
ansible-playbook playbooks/site.yml --list-vars
ansible-inventory -i inventories/production/hosts.yml --list --yaml

# Verify vault file access
ansible-vault view vault/secrets.yml
```

**Issue**: Syntax errors in playbooks
```bash
# Check playbook syntax
ansible-playbook playbooks/site.yml --syntax-check

# Use Python scripts for testing
python scripts/ansible_tester.py syntax site.yml
python scripts/ansible_tester.py suite --tests syntax
```

#### **Performance Issues**

**Issue**: Slow playbook execution
```bash
# Enable connection persistence
# In ansible.cfg:
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True

# Increase parallelism
ansible-playbook playbooks/site.yml --forks 20

# Use performance monitoring
python scripts/performance_monitor.py test site.yml --iterations 1
```

**Issue**: Memory usage problems
```bash
# Disable fact gathering if not needed
gather_facts: false

# Use explicit fact gathering
- name: Gather minimal facts
  ios_facts:
    gather_subset: min
```

#### **Vault Issues**

**Issue**: Vault password problems
```bash
# Create vault password file
echo "your_vault_password" > .vault_pass
chmod 600 .vault_pass

# Update ansible.cfg
[defaults]
vault_password_file = .vault_pass

# Or use environment variable
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
```

**Issue**: Encrypted file corruption
```bash
# Verify vault file integrity
ansible-vault view vault/secrets.yml

# Rekey if necessary
ansible-vault rekey vault/secrets.yml

# Use Python vault manager for complex operations
python scripts/vault_manager.py status
python scripts/vault_manager.py view vault/secrets.yml
```

#### **Inventory Problems**

**Issue**: Host not found errors
```bash
# Verify inventory structure
ansible-inventory -i inventories/production/hosts.yml --list --yaml

# Check specific host
ansible-inventory -i inventories/production/hosts.yml --host sw-core-01

# Validate inventory with Python tools
python scripts/ansible_runner.py inventory validate --inventory production
```

**Issue**: Group variables not loading
```bash
# Check group_vars structure
ls -la group_vars/
ls -la group_vars/cisco_devices/

# Verify variable precedence
ansible-playbook playbooks/site.yml --list-vars --limit sw-core-01
```

### Debug Mode and Logging

#### **Verbose Output Levels**
```bash
# Basic verbose output
ansible-playbook playbooks/site.yml -v

# Connection debugging
ansible-playbook playbooks/site.yml -vv

# Task execution details
ansible-playbook playbooks/site.yml -vvv

# Full debug including SSH details
ansible-playbook playbooks/site.yml -vvvv
```

#### **Targeted Debugging**
```bash
# Debug specific task
ansible-playbook playbooks/site.yml --start-at-task "Configure VLANs"

# Step through tasks interactively
ansible-playbook playbooks/site.yml --step

# Continue on errors for debugging
ansible-playbook playbooks/site.yml --ignore-errors
```

#### **Log Analysis**
```bash
# Enable detailed logging in ansible.cfg
[defaults]
log_path = /var/log/ansible.log
display_skipped_hosts = False
display_ok_hosts = False

# Use Python scripts for log analysis
python scripts/ansible_master.py --interactive  # Select Reports option
```

### Network-Specific Troubleshooting

#### **Device Connection Issues**
```bash
# Test basic connectivity
ansible network_devices -m ping

# Test network module connectivity
ansible cisco_devices -m ios_facts -a "gather_subset=min"

# Check device accessibility
ansible cisco_devices -m ios_command -a "commands='show version'"
```

#### **Configuration Issues**
```bash
# Verify configuration before applying
ansible-playbook playbooks/deploy_vlans.yml --check --diff

# Test on single device first
ansible-playbook playbooks/deploy_vlans.yml --limit "test-device"

# Backup before changes
ansible-playbook playbooks/backup_configs.yml
```

### Using Python Scripts for Troubleshooting

#### **System Check**
```bash
# Run full diagnostic suite
python scripts/ansible_tester.py suite --inventory production

# Check connectivity status
python scripts/ansible_runner.py ping --inventory production --timeout 30

# Performance analysis
python scripts/performance_monitor.py test health_check.yml
```

#### **Interactive Troubleshooting**
```bash
# Start interactive mode for guided troubleshooting
python scripts/ansible_master.py --interactive

# Use system status menu for health checks
# Select option 7: System Status
```

### Common Issues

1. **Connection Timeouts**:
   ```bash
   # Increase timeout values in ansible.cfg
   [defaults]
   timeout = 60
   ```

2. **Authentication Failures**:
   ```bash
   # Verify vault password and credentials
   ansible-vault view vault/secrets.yml
   ```

3. **Module Not Found**:
   ```bash
   # Install missing collections
   ansible-galaxy collection install cisco.ios
   ```

### Debug Mode
```bash
# Run with verbose output
ansible-playbook -vvv playbooks/network_health_check.yml
```

## Resources and References

### Official Ansible Documentation
- **[Ansible Documentation](https://docs.ansible.com/)** - Complete official documentation
- **[Ansible Galaxy](https://galaxy.ansible.com/)** - Community collections and roles
- **[Ansible Network Modules](https://docs.ansible.com/ansible/latest/collections/cisco/index.html)** - Network device collections
- **[Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)** - Official best practices guide

### Network Automation Resources
- **[Network to Code](https://networktocode.com/blog/)** - Network automation blog and tutorials
- **[Cisco DevNet](https://developer.cisco.com/learning/devnet-express/network-automation/)** - Cisco network automation learning
- **[Arista EOS Automation](https://aristanetworks.github.io/ansible-avd/)** - Arista AVD framework
- **[Juniper Automation](https://juniper.github.io/contrail-ansible/)** - Juniper automation tools

### Python and Automation
- **[Rich Library](https://rich.readthedocs.io/)** - Used in our Python scripts for beautiful console output
- **[Jinja2 Templates](https://jinja.palletsprojects.com/)** - Template engine for dynamic playbooks
- **[YAML Syntax](https://yaml.org/spec/1.2/spec.html)** - YAML specification for Ansible playbooks

### Learning Paths

#### **Beginner Level**
1. Start with basic Ansible concepts and ad-hoc commands
2. Learn YAML syntax and basic playbook structure
3. Practice with local inventory and simple tasks
4. Use our Python scripts for guided exploration:
   ```bash
   python scripts/ansible_master.py --interactive
   ```

#### **Intermediate Level**
1. Understand inventory management and variables
2. Learn about roles, handlers, and playbook patterns
3. Practice with network device configurations
4. Implement vault for credential management
5. Use testing and performance monitoring tools

#### **Expert Level**
1. Custom module development
2. Complex multi-vendor network automation
3. CI/CD integration with Ansible
4. Performance optimization and scaling
5. Contributing to community collections

### Support

#### **Forums and Communities**
- **[Ansible Reddit](https://www.reddit.com/r/ansible/)** - Community discussions
- **[Network to Code Slack](https://networktocode.slack.com/)** - Network automation community
- **[Ansible Google Groups](https://groups.google.com/forum/#!forum/ansible-project)** - Official mailing list

#### **Training and Certification**
- **[Red Hat Ansible Automation Platform Training](https://www.redhat.com/en/services/training/do407-automation-ansible-i)** - Official training
- **[Network Automation Professional Certification](https://www.networktocode.com/training/)** - Professional certification program

### Tools and Integrations

#### **IDEs and Editors**
- **VS Code** with Ansible extension
- **PyCharm** with Ansible plugin
- **Vim** with ansible-vim plugin

#### **Testing Tools**
- **Molecule** - Testing framework for Ansible roles
- **Ansible Lint** - Best practices linter
- **yamllint** - YAML syntax checker

#### **Monitoring and Observability**
- **Ansible Tower/AWX** - Web-based UI and API
- **Grafana** - Metrics visualization
- **ELK Stack** - Log analysis

### Quick Reference Cards

#### **Essential Commands Cheat Sheet**
```bash
# Inventory and hosts
ansible-inventory --list
ansible all --list-hosts

# Playbook operations
ansible-playbook playbook.yml --check --diff
ansible-playbook playbook.yml --limit "group_name"
ansible-playbook playbook.yml --tags "configuration"

# Vault operations
ansible-vault create secret.yml
ansible-vault edit secret.yml
ansible-vault view secret.yml

# Facts and variables
ansible hostname -m setup
ansible-playbook playbook.yml --list-vars

# Testing and debugging
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook.yml -vvv
```

#### **Network Module Examples**
```yaml
# Cisco IOS
- name: Configure interface
  cisco.ios.ios_config:
    lines:
      - description "Configured by Ansible"
      - no shutdown
    parents: interface GigabitEthernet0/1

# Arista EOS
- name: Configure VLAN
  arista.eos.eos_vlans:
    config:
      - vlan_id: 100
        name: "DATA_VLAN"
    state: merged

# Juniper
- name: Configure BGP
  junipernetworks.junos.junos_config:
    lines:
      - set protocols bgp group external neighbor 192.168.1.1 peer-as 65001
```

### Contributing to This Repository

#### **How to Contribute**
1. Fork the repository
2. Create a feature branch
3. Add your improvements or fixes
4. Test thoroughly with our Python tools
5. Submit a pull request

#### **Development Guidelines**
- Follow existing code style and patterns
- Update documentation for any new features
- Test all changes with multiple device types
- Use our testing framework for validation

#### **Reporting Issues**
- Use GitHub Issues for bug reports
- Include Ansible version and device details
- Provide playbook examples that reproduce issues
- Include verbose output when relevant

## Additional Resources

- [Ansible Network Automation Documentation](https://docs.ansible.com/ansible/latest/network/index.html)
- [Network Configuration Standards](docs/configuration_standards.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Playbook Execution Guide](docs/playbook_guide.md)

## Contributing

1. Follow existing code structure and naming conventions
2. Test all changes in lab environment
3. Update documentation for new features
4. Ensure security best practices are maintained
5. Use our Python tools for testing and validation

Contributions welcome:
- Bug fixes and improvements
- New playbook templates
- Additional device support
- Documentation enhancements
- Python script improvements

Please see our development guidelines above.

## License

This network automation framework is provided under enterprise licensing terms. See LICENSE file for details.

## Support

For technical support and questions:

### Getting Help
1. **Check Documentation**: Review this guide and troubleshooting section
2. **Use Interactive Tools**: Try our Python scripts with `--interactive` mode for guided assistance
3. **Community Resources**: Join the forums and communities listed above
4. **Issue Tracking**: Create detailed issues in this repository for specific problems

### Contact Information  
- **Network Operations Team**: [Your NOC Contact]
- **Automation Engineering**: [Your Team Contact]  
- **Emergency Support**: [Your Emergency Contact]

### Self-Service Resources
```bash
# Get system status and diagnostics
python scripts/ansible_master.py --interactive

# Run health checks
python scripts/ansible_tester.py suite --inventory production

# Check performance and optimization suggestions  
python scripts/performance_monitor.py analyze --recommendations
```

---

**Happy automating!**

*This network automation framework manages multi-vendor infrastructures across 661 production devices. The included Python tools simplify common operations while maintaining enterprise security and compliance standards.*

---

**Generated by**: Network Automation Framework v2.0  
**Last Updated**: December 2024  
**Status**: Production Ready  
**Tools**: Python Scripts Included
