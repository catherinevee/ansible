# Arista Network Automation Playbooks

This directory contains comprehensive Arista-specific Ansible playbooks for enterprise network automation across campus, data center, and cloud environments using Arista EOS.

## Playbook Overview

### 1. arista_enterprise_config.yml
**Purpose**: Complete enterprise network configuration for Arista EOS devices
**Target Devices**: All Arista switches (7000, 7050, 7280, 7320, 7500 series)
**Key Features**:
- System configuration (hostname, domain, NTP, management)
- VLAN configuration and SVI creation with advanced spanning tree
- Interface configuration (L2/L3 with comprehensive settings)
- Port-Channel and MLAG configuration for high availability
- VXLAN overlay network configuration
- BGP configuration for EVPN with peer groups and neighbors
- VRF configuration for multi-tenancy
- Routing protocols (OSPF, ISIS, static routes)
- Quality of Service configuration
- Security features (ACLs, AAA, RADIUS integration)
- Monitoring and logging (SNMP, sFlow, syslog)
- CloudVision Portal integration with TerminAttr
- Comprehensive verification and reporting

### 2. arista_datacenter_spine_leaf.yml
**Purpose**: Automated deployment of spine-leaf data center architecture
**Target Devices**: Arista spine switches (7000/7500 series) and leaf switches (7050/7280/7320 series)
**Key Features**:
- Role-based configuration (spine vs leaf switches)
- BGP underlay configuration with dynamic peer discovery
- BGP EVPN overlay configuration with route reflectors
- MLAG configuration for leaf pairs with peer-link and domain setup
- VXLAN configuration with VNI mapping and multi-tenancy
- Tenant VLAN and VRF provisioning
- BGP EVPN VNI advertisement and route target configuration
- Server-facing access port configuration with MLAG
- Data center QoS configuration
- Advanced monitoring with LANZ and streaming telemetry
- CloudVision integration for centralized management
- Comprehensive spine-leaf verification and reporting

### 3. arista_cvp_integration.yml
**Purpose**: CloudVision Portal integration with advanced telemetry and automation
**Target Devices**: All CVP-managed Arista devices
**Key Features**:
- TerminAttr daemon configuration and management
- Streaming telemetry configuration (gNMI, OpenConfig)
- LANZ (Latency Analyzer) configuration for performance monitoring
- Configuration compliance and validation automation
- Change control integration with rollback capabilities
- Network health monitoring with automated alerting
- Performance and capacity monitoring
- Security and compliance monitoring
- Automated remediation for common issues
- Event handler configuration for proactive management
- Webhook integration for external system notifications
- Comprehensive CVP integration verification and reporting

## Group Variables Integration

All playbooks integrate seamlessly with your comprehensive group_vars configuration:

### Required Group Variables Files:
- `group_vars/arista_devices.yml` - Main Arista device configuration
- `group_vars/arista_datacenter_devices.yml` - Data center specific configuration
- `group_vars/arista_spines.yml` - Spine switch configuration
- `group_vars/arista_leaves.yml` - Leaf switch configuration
- `group_vars/vault.yml` - Encrypted credentials and secrets

### Key Configuration Categories:
```yaml
# System Configuration
arista_system_config:
  hostname: "{{ inventory_hostname }}"
  domain_name: "company.local"
  timezone:
    name: "America/New_York"
    offset: "-5"

# MLAG Configuration
arista_mlag_config:
  domain_id: "MLAG_DOMAIN_01"
  local_interface: "Vlan4094"
  peer_ip: "169.254.0.2"
  peer_link: "Port-Channel1000"

# VXLAN Configuration
arista_vxlan_config:
  source_interface: "Loopback1"
  udp_port: 4789
  vlan_vni_mapping:
    - vlan_id: 10
      vni: 10010
    - vlan_id: 20
      vni: 10020

# BGP Configuration
arista_bgp_config:
  as_number: "65001"
  router_id: "{{ arista_dc_config.loopback0_ip }}"
  peer_groups:
    - name: "UNDERLAY_PEERS"
      remote_as: "65000"
      update_source: "Loopback0"

# CloudVision Configuration
arista_cvp_config:
  cvp_servers:
    - "cvp1.company.local:9910"
    - "cvp2.company.local:9910"
  auth_method: "token"
  vrf: "MGMT"
  compression: "gzip"
```

## Usage Examples

### Enterprise Configuration
```bash
# Deploy complete enterprise configuration
ansible-playbook arista_enterprise_config.yml --limit arista_devices

# Configure MLAG and VXLAN features
ansible-playbook arista_enterprise_config.yml --tags mlag,vxlan

# Dry run for BGP and EVPN configuration
ansible-playbook arista_enterprise_config.yml --tags bgp,evpn --check
```

### Data Center Spine-Leaf Deployment
```bash
# Deploy complete spine-leaf architecture
ansible-playbook arista_datacenter_spine_leaf.yml --limit arista_datacenter_devices

# Configure spine switches only
ansible-playbook arista_datacenter_spine_leaf.yml --limit arista_spines --tags spine,underlay

# Configure leaf switches with VXLAN and MLAG
ansible-playbook arista_datacenter_spine_leaf.yml --limit arista_leaves --tags leaf,vxlan,mlag

# Verify EVPN overlay status
ansible-playbook arista_datacenter_spine_leaf.yml --tags verification,evpn
```

### CloudVision Portal Integration
```bash
# Deploy complete CVP integration
ansible-playbook arista_cvp_integration.yml --limit arista_devices

# Configure telemetry and monitoring only
ansible-playbook arista_cvp_integration.yml --tags telemetry,monitoring

# Set up automated remediation
ansible-playbook arista_cvp_integration.yml --tags remediation --check
```

## Advanced Features

### Spine-Leaf Architecture Support
- **Automatic Role Detection**: Playbooks automatically configure devices based on `device_role` variable
- **BGP Underlay**: Full eBGP underlay with dynamic peer discovery
- **EVPN Overlay**: BGP EVPN with route reflectors and VNI advertisement
- **Multi-Tenancy**: VRF-based tenant isolation with L2/L3 VNI support

### MLAG High Availability
- **Peer-Link Configuration**: Automatic peer-link setup with trunk configuration
- **MLAG Domain**: Domain configuration with peer keepalive
- **Dual-Attached Servers**: MLAG port-channel configuration for server connectivity
- **Reload Delays**: Configurable reload delays for graceful failover

### VXLAN Overlay Networks
- **Dynamic VNI Assignment**: Automatic VLAN to VNI mapping
- **Multi-Tenancy**: VRF-based tenant separation
- **EVPN Integration**: Full BGP EVPN integration with route targets
- **Anycast Gateway**: Distributed anycast gateway configuration

### CloudVision Integration
- **TerminAttr Agent**: Automated agent deployment and configuration
- **Streaming Telemetry**: gNMI and OpenConfig telemetry streams
- **Change Control**: Integration with CVP change control workflows
- **Automated Compliance**: Configuration compliance checking and remediation

## Monitoring and Telemetry

### Performance Monitoring
```yaml
arista_telemetry_config:
  gnmi_enabled: true
  lanz_enabled: true
  openconfig_paths:
    - {provider: "eos-native", path: "/interfaces/interface/state"}
    - {provider: "openconfig", path: "/network-instances/network-instance"}
```

### Health Monitoring
```yaml
arista_monitoring_config:
  critical_interfaces:
    - {interface: "Ethernet1", threshold: 80}
    - {interface: "Port-Channel1", threshold: 90}
  lanz_enabled: true
  bandwidth_interfaces:
    - {interface: "Ethernet1", interval: 30}
```

### Automated Alerting
```yaml
arista_cvp_config:
  alert_webhook: "https://monitoring.company.local/webhook"
  security_webhook: "https://security.company.local/alerts"
  cpu_threshold: 80
  mac_aging_time: 300
```

## Troubleshooting

### Common Issues
1. **MLAG Issues**: Check peer-link connectivity and VLAN consistency
2. **VXLAN Problems**: Verify underlay reachability and VNI configuration
3. **BGP EVPN**: Check route reflector configuration and address families
4. **CVP Connectivity**: Verify management network and authentication

### Debug Commands
```bash
# MLAG status
show mlag
show mlag config-sanity

# VXLAN status
show vxlan config-sanity
show vxlan address-table

# BGP EVPN status
show bgp evpn summary
show bgp evpn

# CVP status
show daemon TerminAttr
show management cvx
```

### Verification Steps
- Interface status and descriptions
- MLAG peer status and consistency
- VXLAN configuration sanity checks
- BGP neighbor relationships (underlay and overlay)
- EVPN route advertisement and learning
- CloudVision connectivity and streaming status

## Integration with Master Orchestration

These Arista playbooks integrate with the master orchestration framework:
```bash
# Execute via master orchestration
ansible-playbook master_orchestration.yml --limit arista_devices --tags arista_config

# Data center specific deployment
ansible-playbook master_orchestration.yml --limit arista_datacenter_devices --tags datacenter_config
```

## Prerequisites

### Required Collections
```bash
ansible-galaxy collection install arista.eos
ansible-galaxy collection install ansible.netcommon
ansible-galaxy collection install community.general
```

### Device Requirements
- Arista EOS 4.20+ (recommended 4.24+)
- API access enabled (eAPI or gNMI)
- SSH or HTTPS management access
- CloudVision Portal integration (optional)
- Appropriate user privileges (network-admin role)

### Control Node Requirements
- Ansible 4.0+ (ansible-core 2.11+)
- Python 3.8+
- Arista EOS collection
- CloudVision Portal API access (for CVP integration)

## Data Center Architecture Examples

### Spine Configuration
```yaml
device_role: spine
arista_dc_config:
  bgp_asn: "65000"
  loopback0_ip: "1.1.1.1"
  
arista_spine_config:
  bgp_listen_range: "172.16.0.0/16"
  evpn_listen_range: "1.1.1.0/24"
```

### Leaf Configuration
```yaml
device_role: leaf
arista_leaf_config:
  bgp_asn: "65001"
  
arista_tenant_config:
  vlans:
    - vlan_id: 10
      name: "WEB_SERVERS"
      vni: 10010
      gateway_ip: "10.1.10.1"
      vrf: "TENANT_A"
  vrfs:
    - name: "TENANT_A"
      vni: 50001
```

## Contributing

When extending these playbooks:
1. Follow Arista EOS best practices
2. Use role-based conditional logic for spine-leaf deployments
3. Include comprehensive error handling and validation
4. Add appropriate tags for selective execution
5. Update documentation and examples
6. Test with CloudVision Portal integration

## Support

For issues and questions:
- Review playbook logs and device reports
- Check Arista EOS collection documentation
- Verify device compatibility and software versions
- Test configurations in lab environment first
- Consult Arista CloudVision Portal documentation for CVP integration

---

*These playbooks provide production-ready Arista network automation with advanced data center features, MLAG high availability, VXLAN overlays, BGP EVPN, and comprehensive CloudVision Portal integration.*
