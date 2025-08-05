# Enterprise Network Automation Framework

Ansible-based network automation framework for managing multi-vendor network infrastructure, security compliance, and operational workflows across 661 production devices.

## Architecture

Production-ready automation supporting:

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
├── BASIC_CONFIG_GUIDE.md               # Comprehensive basic configuration guide
├── ENTERPRISE_FRAMEWORK_COMPLETE.md   # Complete framework documentation
├── config_standards.yml               # Configuration compliance standards
└── playbooks/
    └── PANOS_ADVANCED_GUIDE.md        # Advanced Palo Alto automation guide
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

## 🚀 Quick Start

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

## 🎯 Core Operations

### Network Health Monitoring
```bash
# Comprehensive health check
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

## 🔧 Advanced Configuration

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

Enable comprehensive security hardening:

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

## 📊 Reporting and Analytics

### Generated Reports

All operations generate comprehensive reports:

- **HTML Reports**: Interactive compliance dashboards with scoring
- **Text Reports**: Detailed operational summaries
- **JSON Analytics**: Structured data for integration with monitoring systems

### Report Locations

- Compliance Reports: `reports/compliance_<device>_<date>.html`
- Health Check Reports: `reports/health_<device>_<date>.txt`
- DR Reports: `reports/dr_report_<device>_<date>.txt`
- Orchestration Summaries: `reports/orchestration_<mode>_<date>.txt`

## 🛡️ Security Features

### Credential Management
- All passwords encrypted with ansible-vault
- No hardcoded credentials in configurations
- Support for certificate-based authentication

### Secure Communications
- SSH version 2 enforcement
- HTTPS/TLS for API communications
- Connection encryption for all protocols

### Audit Trail
- Comprehensive logging of all operations
- Change tracking and version control integration
- Compliance reporting with evidence collection

## 🔄 Best Practices

### Change Management
1. Always test in development environment first
2. Create configuration backups before changes
3. Use serial execution for critical deployments
4. Implement proper rollback procedures

### Error Handling
- All playbooks include comprehensive error handling
- Failed operations trigger automatic rollback
- Detailed error logging for troubleshooting

### Performance Optimization
- Parallel execution where safe
- Connection persistence for efficiency
- Fact caching to reduce overhead

## 🚨 Troubleshooting

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

## 📚 Additional Resources

- [Ansible Network Automation Documentation](https://docs.ansible.com/ansible/latest/network/index.html)
- [Network Configuration Standards](docs/configuration_standards.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Playbook Execution Guide](docs/playbook_guide.md)

## 🤝 Contributing

1. Follow existing code structure and naming conventions
2. Test all changes in lab environment
3. Update documentation for new features
4. Ensure security best practices are maintained

## 📄 License

This network automation framework is provided under enterprise licensing terms. See LICENSE file for details.

## 📞 Support

For technical support and questions:
- Network Operations Team: [Your NOC Contact]
- Automation Engineering: [Your Team Contact]
- Emergency Support: [Your Emergency Contact]

---

**Generated by**: Enterprise Network Automation Framework v2.0  
**Last Updated**: December 2024  
**Framework Status**: Production Ready