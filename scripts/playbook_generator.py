#!/usr/bin/env python3
"""
Ansible Playbook Generator
Dynamically generates Ansible playbooks based on templates and requirements
Supports multi-vendor network device configurations
"""

import os
import sys
import argparse
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from jinja2 import Environment, FileSystemLoader, Template
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaybookGenerator:
    """Generator for Ansible playbooks"""
    
    def __init__(self, base_path: str = None):
        self.console = Console()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.playbook_path = self.base_path / "playbooks"
        self.templates_path = self.base_path / "templates"
        self.roles_path = self.base_path / "roles"
        
        # Ensure directories exist
        self.playbook_path.mkdir(exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)
        self.roles_path.mkdir(exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Playbook templates
        self.playbook_templates = {
            "basic_config": self._basic_config_template(),
            "backup_config": self._backup_config_template(),
            "security_hardening": self._security_hardening_template(),
            "monitoring_config": self._monitoring_config_template(),
            "compliance_audit": self._compliance_audit_template(),
            "firmware_update": self._firmware_update_template(),
            "network_troubleshooting": self._troubleshooting_template(),
            "disaster_recovery": self._disaster_recovery_template()
        }
        
        # Device type configurations
        self.device_configs = {
            "cisco_ios": {
                "connection": "network_cli",
                "network_os": "ios",
                "modules": ["ios_config", "ios_command", "ios_facts", "ios_vlans", "ios_interfaces"]
            },
            "cisco_nxos": {
                "connection": "network_cli", 
                "network_os": "nxos",
                "modules": ["nxos_config", "nxos_command", "nxos_facts", "nxos_vlans", "nxos_interfaces"]
            },
            "arista_eos": {
                "connection": "httpapi",
                "network_os": "eos", 
                "modules": ["eos_config", "eos_command", "eos_facts", "eos_vlans", "eos_interfaces"]
            },
            "juniper_junos": {
                "connection": "netconf",
                "network_os": "junos",
                "modules": ["junos_config", "junos_command", "junos_facts", "junos_vlans", "junos_interfaces"]
            },
            "palo_alto": {
                "connection": "local",
                "modules": ["panos_config_element", "panos_op", "panos_facts", "panos_security_rule"]
            },
            "fortinet": {
                "connection": "httpapi",
                "modules": ["fortios_configuration_fact", "fortios_system_global", "fortios_firewall_policy"]
            }
        }
    
    def generate_playbook(self, 
                         playbook_type: str,
                         device_types: List[str],
                         playbook_name: str,
                         custom_vars: Dict = None) -> bool:
        """Generate a playbook based on type and device configuration"""
        
        if playbook_type not in self.playbook_templates:
            self.console.print(f"[red]Unknown playbook type: {playbook_type}[/red]")
            return False
        
        # Get template
        template_content = self.playbook_templates[playbook_type]
        
        # Prepare variables
        template_vars = {
            "device_types": device_types,
            "device_configs": self.device_configs,
            "playbook_name": playbook_name,
            "custom_vars": custom_vars or {}
        }
        
        # Render template
        try:
            template = Template(template_content)
            playbook_content = template.render(**template_vars)
            
            # Write playbook file
            playbook_file = self.playbook_path / f"{playbook_name}.yml"
            with open(playbook_file, 'w') as f:
                f.write(playbook_content)
            
            self.console.print(f"[green]✓ Generated playbook: {playbook_file}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error generating playbook: {str(e)}[/red]")
            return False
    
    def _basic_config_template(self) -> str:
        """Basic device configuration template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  
  vars:
    ansible_command_timeout: 60
    ansible_connect_timeout: 60
{% if custom_vars %}
{% for key, value in custom_vars.items() %}
    {{ key }}: {{ value }}
{% endfor %}
{% endif %}

  tasks:
    - name: Gather device facts
      {{ device_configs[device_types[0]]['modules'][2] }}:
      register: device_facts
      when: ansible_network_os == "{{ device_configs[device_types[0]]['network_os'] }}"

    - name: Display device information
      debug:
        msg: "Device {{ '{{ inventory_hostname }}' }} is running {{ '{{ device_facts.ansible_facts.ansible_net_version }}' }}"
      when: device_facts is defined

{% for device_type in device_types %}
    - name: Configure {{ device_type }} devices
      block:
        - name: Apply basic configuration
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - hostname {{ '{{ inventory_hostname }}' }}
              - no ip domain-lookup
              - ip domain-name {{ '{{ domain_name | default("example.com") }}' }}
              - ntp server {{ '{{ ntp_server | default("pool.ntp.org") }}' }}
            save_when: changed
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
          
        - name: Verify configuration
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show running-config | include hostname
              - show running-config | include ntp
          register: config_verification
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
          
      rescue:
        - name: Configuration failed for {{ device_type }}
          debug:
            msg: "Failed to configure {{ '{{ inventory_hostname }}' }} - {{ device_type }}"
{% endfor %}

    - name: Generate configuration report
      template:
        src: config_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_config_report.txt"
      delegate_to: localhost
      vars:
        timestamp: "{{ '{{ ansible_date_time.iso8601 }}' }}"
        hostname: "{{ '{{ inventory_hostname }}' }}"
        device_type: "{{ '{{ ansible_network_os }}' }}"
        configuration_status: "{{ '{{ config_verification.stdout if config_verification is defined else \"Not verified\" }}' }}"
"""

    def _backup_config_template(self) -> str:
        """Configuration backup template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  
  vars:
    backup_dir: "./backups/{{ '{{ ansible_date_time.date }}' }}"
    ansible_command_timeout: 60

  tasks:
    - name: Create backup directory
      file:
        path: "{{ '{{ backup_dir }}' }}"
        state: directory
      delegate_to: localhost
      run_once: true

{% for device_type in device_types %}
    - name: Backup {{ device_type }} configuration
      block:
        - name: Get running configuration
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show running-config
          register: running_config
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Save configuration backup
          copy:
            content: "{{ '{{ running_config.stdout[0] }}' }}"
            dest: "{{ '{{ backup_dir }}' }}/{{ '{{ inventory_hostname }}' }}_{{ device_type }}_config.txt"
          delegate_to: localhost
          when: running_config is defined and running_config.stdout is defined

        - name: Create configuration metadata
          copy:
            content: |
              Device: {{ '{{ inventory_hostname }}' }}
              Type: {{ device_type }}
              Backup Date: {{ '{{ ansible_date_time.iso8601 }}' }}
              OS Version: {{ '{{ ansible_net_version | default("Unknown") }}' }}
              Serial Number: {{ '{{ ansible_net_serialnum | default("Unknown") }}' }}
            dest: "{{ '{{ backup_dir }}' }}/{{ '{{ inventory_hostname }}' }}_{{ device_type }}_metadata.txt"
          delegate_to: localhost
          when: running_config is defined
{% endfor %}

    - name: Create backup summary
      template:
        src: backup_summary.j2
        dest: "{{ '{{ backup_dir }}' }}/backup_summary.txt"
      delegate_to: localhost
      run_once: true
      vars:
        total_devices: "{{ '{{ groups.all | length }}' }}"
        backup_timestamp: "{{ '{{ ansible_date_time.iso8601 }}' }}"
"""

    def _security_hardening_template(self) -> str:
        """Security hardening template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  
  vars:
    security_banner: |
      **************************************************************************
      * WARNING: This system is for authorized use only. All activity may be  *
      * monitored and recorded. Unauthorized access is prohibited.            *
      **************************************************************************

  tasks:
{% for device_type in device_types %}
    - name: Apply security hardening for {{ device_type }}
      block:
        - name: Configure login banner
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - banner login ^{{ '{{ security_banner }}' }}^
            save_when: changed
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Disable unused services
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - no ip http server
              - no ip http secure-server
              - no service tcp-small-servers
              - no service udp-small-servers
              - no service finger
              - no ip bootp server
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - device_configs[device_type].get('network_os') in ['ios', 'nxos']

        - name: Configure password policies
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - service password-encryption
              - security passwords min-length 8
              - login block-for 120 attempts 3 within 60
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - device_configs[device_type].get('network_os') in ['ios', 'nxos']

        - name: Configure SSH security
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - ip ssh version 2
              - ip ssh time-out 60
              - ip ssh authentication-retries 2
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - device_configs[device_type].get('network_os') in ['ios', 'nxos']

        - name: Verify security settings
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show running-config | include banner
              - show running-config | include service password-encryption
              - show ip ssh
          register: security_verification
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
{% endfor %}

    - name: Generate security compliance report
      template:
        src: security_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_security_report.txt"
      delegate_to: localhost
      vars:
        security_check_results: "{{ '{{ security_verification.stdout if security_verification is defined else [] }}' }}"
"""

    def _monitoring_config_template(self) -> str:
        """Monitoring configuration template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  
  vars:
    snmp_community: "{{ '{{ vault_snmp_community | default(\"public\") }}' }}"
    syslog_server: "{{ '{{ syslog_server | default(\"192.168.1.100\") }}' }}"
    ntp_servers:
      - "{{ '{{ ntp_server1 | default(\"0.pool.ntp.org\") }}' }}"
      - "{{ '{{ ntp_server2 | default(\"1.pool.ntp.org\") }}' }}"

  tasks:
{% for device_type in device_types %}
    - name: Configure monitoring for {{ device_type }}
      block:
        - name: Configure SNMP
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - snmp-server community {{ '{{ snmp_community }}' }} RO
              - snmp-server location {{ '{{ site_location | default("Datacenter") }}' }}
              - snmp-server contact {{ '{{ admin_contact | default("admin@example.com") }}' }}
              - snmp-server enable traps
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - device_configs[device_type].get('network_os') in ['ios', 'nxos']

        - name: Configure syslog
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - logging {{ '{{ syslog_server }}' }}
              - logging trap informational
              - logging source-interface Loopback0
              - service timestamps log datetime msec
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - device_configs[device_type].get('network_os') in ['ios', 'nxos']

        - name: Configure NTP
          {{ device_configs[device_type]['modules'][0] }}:
            lines: |
              {% raw %}
              {% for ntp_server in ntp_servers %}
              ntp server {{ ntp_server }}
              {% endfor %}
              {% endraw %}
              ntp update-calendar
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - device_configs[device_type].get('network_os') in ['ios', 'nxos']

        - name: Verify monitoring configuration
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show snmp community
              - show logging
              - show ntp status
          register: monitoring_verification
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
{% endfor %}

    - name: Create monitoring report
      template:
        src: monitoring_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_monitoring_report.txt"
      delegate_to: localhost
      vars:
        monitoring_status: "{{ '{{ monitoring_verification.stdout if monitoring_verification is defined else [] }}' }}"
"""

    def _compliance_audit_template(self) -> str:
        """Compliance audit template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: true
  connection: "{{ '{{ ansible_connection }}' }}"
  
  vars:
    compliance_checks:
      - name: "Password encryption"
        command: "show running-config | include service password-encryption"
        expected: "service password-encryption"
      - name: "SSH version"
        command: "show ip ssh"
        expected: "SSH version 2.0"
      - name: "Banner configuration"
        command: "show running-config | include banner"
        expected: "banner"

  tasks:
{% for device_type in device_types %}
    - name: Run compliance audit for {{ device_type }}
      block:
        - name: Execute compliance checks
          {{ device_configs[device_type]['modules'][1] }}:
            commands: "{{ '{{ item.command }}' }}"
          register: compliance_results
          loop: "{{ '{{ compliance_checks }}' }}"
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Evaluate compliance results
          set_fact:
            compliance_status: |
              {% raw %}
              {% set compliance_list = [] %}
              {% for result in compliance_results.results %}
                {% set check = compliance_checks[loop.index0] %}
                {% set status = "PASS" if check.expected in result.stdout[0] else "FAIL" %}
                {% set compliance_item = {
                  'check': check.name,
                  'status': status,
                  'expected': check.expected,
                  'actual': result.stdout[0][:100] + '...' if result.stdout[0]|length > 100 else result.stdout[0]
                } %}
                {{ compliance_list.append(compliance_item) }}
              {% endfor %}
              {{ compliance_list }}
              {% endraw %}
          when: compliance_results is defined
{% endfor %}

    - name: Generate compliance report
      template:
        src: compliance_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_compliance_report.json"
      delegate_to: localhost
      vars:
        device_info:
          hostname: "{{ '{{ inventory_hostname }}' }}"
          device_type: "{{ '{{ ansible_network_os }}' }}"
          version: "{{ '{{ ansible_net_version | default("Unknown") }}' }}"
          audit_date: "{{ '{{ ansible_date_time.iso8601 }}' }}"
        audit_results: "{{ '{{ compliance_status | default([]) }}' }}"
"""

    def _firmware_update_template(self) -> str:
        """Firmware update template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  serial: 1  # Update one device at a time
  
  vars:
    firmware_server: "{{ '{{ firmware_server | default(\"tftp://192.168.1.100\") }}' }}"
    backup_dir: "./backups/firmware_update_{{ '{{ ansible_date_time.date }}' }}"

  tasks:
    - name: Create backup directory
      file:
        path: "{{ '{{ backup_dir }}' }}"
        state: directory
      delegate_to: localhost
      run_once: true

{% for device_type in device_types %}
    - name: Firmware update for {{ device_type }}
      block:
        - name: Check current firmware version
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show version
          register: current_version
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Backup current configuration
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show running-config
          register: running_config
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Save pre-update backup
          copy:
            content: |
              Pre-update backup for {{ '{{ inventory_hostname }}' }}
              Date: {{ '{{ ansible_date_time.iso8601 }}' }}
              Current Version: {{ '{{ current_version.stdout[0] }}' }}
              
              Running Configuration:
              {{ '{{ running_config.stdout[0] }}' }}
            dest: "{{ '{{ backup_dir }}' }}/{{ '{{ inventory_hostname }}' }}_pre_update_backup.txt"
          delegate_to: localhost
          when: running_config is defined

        - name: Copy firmware image
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - copy {{ '{{ firmware_server }}' }}/{{ '{{ firmware_image }}' }} bootflash:
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - firmware_image is defined

        - name: Set boot image
          {{ device_configs[device_type]['modules'][0] }}:
            lines:
              - boot system bootflash:{{ '{{ firmware_image }}' }}
            save_when: changed
          when: 
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
            - firmware_image is defined

        - name: Verify firmware installation
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show boot
              - dir bootflash: | include {{ '{{ firmware_image }}' }}
          register: firmware_verification
          when: firmware_image is defined
{% endfor %}

    - name: Generate firmware update report
      template:
        src: firmware_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_firmware_report.txt"
      delegate_to: localhost
      vars:
        pre_update_version: "{{ '{{ current_version.stdout[0] if current_version is defined else \"Unknown\" }}' }}"
        firmware_status: "{{ '{{ firmware_verification.stdout if firmware_verification is defined else [] }}' }}"
"""

    def _troubleshooting_template(self) -> str:
        """Network troubleshooting template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  
  tasks:
{% for device_type in device_types %}
    - name: Troubleshooting for {{ device_type }}
      block:
        - name: Collect system information
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show version
              - show processes cpu
              - show memory summary
              - show environment all
          register: system_info
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Collect interface status
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show interfaces status
              - show interfaces description
              - show ip interface brief
          register: interface_info
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Collect routing information
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show ip route summary
              - show ip protocols
              - show ip bgp summary
          register: routing_info
          ignore_errors: true
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Collect logs
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show logging | last 50
              - show logging | include ERROR
              - show logging | include WARN
          register: log_info
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
{% endfor %}

    - name: Generate troubleshooting report
      template:
        src: troubleshooting_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_troubleshooting_report.txt"
      delegate_to: localhost
      vars:
        system_status: "{{ '{{ system_info.stdout if system_info is defined else [] }}' }}"
        interface_status: "{{ '{{ interface_info.stdout if interface_info is defined else [] }}' }}"
        routing_status: "{{ '{{ routing_info.stdout if routing_info is defined else [] }}' }}"
        log_entries: "{{ '{{ log_info.stdout if log_info is defined else [] }}' }}"
"""

    def _disaster_recovery_template(self) -> str:
        """Disaster recovery template"""
        return """---
- name: {{ playbook_name | title }}
  hosts: "{{ '{{ target_hosts | default(\"all\") }}' }}"
  gather_facts: false
  connection: "{{ '{{ ansible_connection }}' }}"
  
  vars:
    recovery_config_path: "{{ '{{ recovery_config_path | default(\"./recovery_configs\") }}' }}"
    
  tasks:
    - name: Create recovery directory
      file:
        path: "{{ '{{ recovery_config_path }}' }}"
        state: directory
      delegate_to: localhost
      run_once: true

{% for device_type in device_types %}
    - name: Disaster recovery for {{ device_type }}
      block:
        - name: Check if recovery config exists
          stat:
            path: "{{ '{{ recovery_config_path }}' }}/{{ '{{ inventory_hostname }}' }}_recovery.cfg"
          register: recovery_file
          delegate_to: localhost

        - name: Load recovery configuration
          {{ device_configs[device_type]['modules'][0] }}:
            src: "{{ '{{ recovery_config_path }}' }}/{{ '{{ inventory_hostname }}' }}_recovery.cfg"
            save_when: changed
          when: 
            - recovery_file.stat.exists
            - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"

        - name: Restore from backup if no recovery config
          block:
            - name: Find latest backup
              find:
                paths: "./backups"
                patterns: "{{ '{{ inventory_hostname }}' }}_*_config.txt"
                file_type: file
              register: backup_files
              delegate_to: localhost

            - name: Load latest backup
              {{ device_configs[device_type]['modules'][0] }}:
                src: "{{ '{{ (backup_files.files | sort(attribute=\"mtime\") | last).path }}' }}"
                save_when: changed
              when: 
                - backup_files.files | length > 0
                - ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
          when: not recovery_file.stat.exists

        - name: Verify recovery
          {{ device_configs[device_type]['modules'][1] }}:
            commands:
              - show running-config | include hostname
              - show ip interface brief
              - show ip route summary
          register: recovery_verification
          when: ansible_network_os == "{{ device_configs[device_type].get('network_os', device_type) }}"
{% endfor %}

    - name: Generate recovery report
      template:
        src: recovery_report.j2
        dest: "./reports/{{ '{{ inventory_hostname }}' }}_recovery_report.txt"
      delegate_to: localhost
      vars:
        recovery_timestamp: "{{ '{{ ansible_date_time.iso8601 }}' }}"
        recovery_status: "{{ '{{ recovery_verification.stdout if recovery_verification is defined else [] }}' }}"
"""

    def interactive_generator(self):
        """Interactive playbook generator"""
        self.console.print(Panel.fit("[bold blue]Ansible Playbook Generator[/bold blue]"))
        
        # Get playbook type
        playbook_types = list(self.playbook_templates.keys())
        self.console.print("\n[bold]Available Playbook Types:[/bold]")
        for i, ptype in enumerate(playbook_types, 1):
            self.console.print(f"  {i}. {ptype.replace('_', ' ').title()}")
        
        type_choice = IntPrompt.ask(
            "Select playbook type",
            choices=[str(i) for i in range(1, len(playbook_types) + 1)]
        )
        
        playbook_type = playbook_types[type_choice - 1]
        
        # Get device types
        device_types = list(self.device_configs.keys())
        self.console.print("\n[bold]Available Device Types:[/bold]")
        for i, dtype in enumerate(device_types, 1):
            self.console.print(f"  {i}. {dtype.replace('_', ' ').title()}")
        
        device_choices = Prompt.ask(
            "Select device types (comma-separated numbers)",
            default="1"
        )
        
        selected_devices = []
        for choice in device_choices.split(','):
            idx = int(choice.strip()) - 1
            if 0 <= idx < len(device_types):
                selected_devices.append(device_types[idx])
        
        # Get playbook name
        playbook_name = Prompt.ask(
            "Enter playbook name",
            default=f"{playbook_type}_{len(selected_devices)}_devices"
        )
        
        # Custom variables
        custom_vars = {}
        if Confirm.ask("Add custom variables?"):
            while True:
                var_name = Prompt.ask("Variable name (empty to finish)", default="")
                if not var_name:
                    break
                var_value = Prompt.ask(f"Value for {var_name}")
                custom_vars[var_name] = var_value
        
        # Generate playbook
        success = self.generate_playbook(
            playbook_type=playbook_type,
            device_types=selected_devices,
            playbook_name=playbook_name,
            custom_vars=custom_vars
        )
        
        if success:
            self.console.print(f"\n[green]✓ Playbook generated successfully![/green]")
            self.console.print(f"Location: {self.playbook_path / f'{playbook_name}.yml'}")
        
        return success
    
    def list_templates(self):
        """List available playbook templates"""
        table = Table(title="Available Playbook Templates")
        table.add_column("Template", style="cyan")
        table.add_column("Description", style="white")
        
        descriptions = {
            "basic_config": "Basic device configuration and setup",
            "backup_config": "Configuration backup and archival",
            "security_hardening": "Security configuration and hardening",
            "monitoring_config": "SNMP, syslog, and NTP configuration",
            "compliance_audit": "Security and compliance auditing",
            "firmware_update": "Firmware upgrade procedures",
            "network_troubleshooting": "Network diagnostics and troubleshooting",
            "disaster_recovery": "Disaster recovery and restoration"
        }
        
        for template_name in self.playbook_templates.keys():
            description = descriptions.get(template_name, "No description available")
            table.add_row(template_name, description)
        
        self.console.print(table)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Ansible Playbook Generator")
    parser.add_argument("--base-path", help="Base path for Ansible project")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a playbook")
    generate_parser.add_argument("--type", choices=["basic_config", "backup_config", "security_hardening", 
                                                   "monitoring_config", "compliance_audit", "firmware_update",
                                                   "network_troubleshooting", "disaster_recovery"],
                                help="Playbook type")
    generate_parser.add_argument("--devices", nargs="+", 
                                choices=["cisco_ios", "cisco_nxos", "arista_eos", "juniper_junos", 
                                        "palo_alto", "fortinet"],
                                help="Device types")
    generate_parser.add_argument("--name", help="Playbook name")
    generate_parser.add_argument("--vars", help="Custom variables (JSON format)")
    
    # Interactive command
    subparsers.add_parser("interactive", help="Interactive playbook generation")
    
    # List command
    subparsers.add_parser("list", help="List available templates")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize generator
    generator = PlaybookGenerator(args.base_path)
    
    try:
        if args.command == "generate":
            if not all([args.type, args.devices, args.name]):
                generator.console.print("[red]--type, --devices, and --name are required for generate command[/red]")
                sys.exit(1)
            
            custom_vars = {}
            if args.vars:
                custom_vars = json.loads(args.vars)
            
            success = generator.generate_playbook(
                playbook_type=args.type,
                device_types=args.devices,
                playbook_name=args.name,
                custom_vars=custom_vars
            )
            
            sys.exit(0 if success else 1)
        
        elif args.command == "interactive":
            success = generator.interactive_generator()
            sys.exit(0 if success else 1)
        
        elif args.command == "list":
            generator.list_templates()
    
    except Exception as e:
        generator.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
