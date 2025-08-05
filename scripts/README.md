# Ansible Python Scripts

Python scripts for managing Ansible operations. These scripts provide a unified interface for playbook execution, testing, performance monitoring, and automation management.

## Why These Scripts Exist

Managing network automation at scale requires more than basic Ansible commands. These scripts address common pain points:

- **Monitoring**: Know when long-running playbooks will finish
- **Testing**: Catch configuration errors before they hit production  
- **Vault Management**: Simplify credential handling across multiple files
- **Playbook Generation**: Reduce copy-paste errors with templates
- **Unified Interface**: Single command for complex operations

## Overview

The Python scripts provide:

- **Unified Management**: Single interface for Ansible operations
- **Performance Monitoring**: Real-time monitoring and analysis of playbook execution  
- **Automated Testing**: Test suites for playbooks and infrastructure
- **Dynamic Generation**: Template-based playbook creation
- **Vault Management**: Simplified Ansible Vault operations
- **Console Interface**: Terminal interface with progress bars and tables

## Scripts

### 1. `ansible_master.py` - Master Controller
Main orchestration script providing unified interface to all other tools.

Use this when you want one command to handle multiple operations or when training new team members.

**Features:**
- Interactive menu-driven interface  
- Direct CLI commands for automation
- Integrated performance monitoring
- Test execution
- Unified vault management

**Usage:**
```powershell
# Interactive mode
python ansible_master.py --interactive

# Direct commands
python ansible_master.py --run site.yml --inventory production
python ansible_master.py --test
python ansible_master.py --connectivity
```

### 2. `ansible_runner.py` - Playbook Execution
Execute Ansible playbooks with monitoring options.

Useful for scheduled deployments or when you need detailed execution metrics.

**Features:**
- Playbook execution with custom parameters
- Ad-hoc command execution
- Connectivity testing
- Inventory validation and visualization
- Real-time progress monitoring

**Usage:**
```powershell
# Run a playbook
python ansible_runner.py playbook backup_configs.yml -i production --verbose 2

# Ad-hoc commands
python ansible_runner.py adhoc all -m ping -i production

# Check connectivity
python ansible_runner.py ping -i production --timeout 30

# List available resources
python ansible_runner.py list-playbooks
python ansible_runner.py list-inventories
```

### 3. `vault_manager.py` - Ansible Vault Management
Ansible Vault operations with simplified usability.

**Features:**
- File encryption/decryption
- String encryption
- Vault file creation with templates
- Bulk vault operations
- Vault health monitoring

**Usage:**
```powershell
# Create new vault file
python vault_manager.py create vault/credentials.yml --template credentials

# Encrypt existing file
python vault_manager.py encrypt group_vars/production/secrets.yml

# View encrypted file
python vault_manager.py view vault/api_keys.yml

# Show vault status
python vault_manager.py status
```

### 4. `playbook_generator.py` - Dynamic Playbook Generation
Generate Ansible playbooks from templates based on requirements.

**Features:**
- Template-based playbook generation
- Multi-vendor device support
- Interactive playbook builder
- Custom variable injection
- Best practices integration

**Usage:**
```powershell
# Interactive generation
python playbook_generator.py interactive

# Direct generation
python playbook_generator.py generate --type security_hardening --devices cisco_ios arista_eos --name security_audit

# List available templates
python playbook_generator.py list
```

### 5. `ansible_tester.py` - Testing Framework
Run various tests on Ansible playbooks and infrastructure.

**Features:**
- Syntax validation
- Dry run testing
- Inventory validation
- Connectivity testing
- Role structure validation
- Parallel test execution

**Usage:**
```powershell
# Full test suite
python ansible_tester.py suite --inventory production

# Specific tests
python ansible_tester.py syntax site.yml
python ansible_tester.py connectivity -i production
python ansible_tester.py dry-run backup_configs.yml
```

### 6. `performance_monitor.py` - Performance Analysis
Monitor and analyze Ansible playbook performance.

**Features:**
- Real-time resource monitoring
- Performance metrics collection
- Optimization recommendations
- Historical performance analysis
- Detailed reporting

**Usage:**
```powershell
# Performance test
python performance_monitor.py test site.yml --iterations 3 --save perf_results.json

# Monitor specific command
python performance_monitor.py monitor ansible-playbook site.yml -i production
```

## Installation

1. **Install Python Dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Install Ansible Collections (if needed):**
```powershell
ansible-galaxy install -r requirements.yml
```

3. **Set up directory structure** (automatic on first run):
   - The scripts will automatically create required directories
   - Inventories, playbooks, vault files, and reports will be organized

## Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
ANSIBLE_HOST_KEY_CHECKING=False
ANSIBLE_TIMEOUT=60
```

### Ansible Configuration
The scripts work with your existing `ansible.cfg` configuration.

## Quick Start

1. **Start the Master Controller:**
```powershell
python scripts/ansible_master.py --interactive
```

2. **Generate your first playbook:**
   - Select option 2 (Generate Playbook)
   - Choose a template type
   - Select target device types
   - Customize variables

3. **Test the playbook:**
   - Select option 3 (Test Suite)
   - Run syntax and dry-run tests

4. **Execute with monitoring:**
   - Select option 1 (Run Playbook)
   - Enable performance monitoring
   - Review results and recommendations

## Features

### Bulk Operations
```powershell
# Test all playbooks
python ansible_tester.py suite --tests syntax inventory connectivity

# Generate multiple playbooks
for device_type in cisco_ios arista_eos juniper_junos; do
    python playbook_generator.py generate --type basic_config --devices $device_type --name "basic_$device_type"
done
```

### Performance Analysis
```powershell
# Compare performance across inventories
python performance_monitor.py test site.yml --iterations 5 --save prod_perf.json
python performance_monitor.py test site.yml --iterations 5 --inventory staging --save staging_perf.json
```

### Automated Testing Pipeline
```powershell
# Complete validation pipeline
python ansible_tester.py suite --tests syntax inventory roles
python ansible_tester.py connectivity --inventory production
python ansible_tester.py dry-run site.yml --limit "test_hosts"
```

## Directory Structure

```
ansible/
├── scripts/                    # Python automation scripts
│   ├── ansible_master.py      # Main controller
│   ├── ansible_runner.py      # Playbook execution
│   ├── vault_manager.py       # Vault operations
│   ├── playbook_generator.py  # Playbook generation
│   ├── ansible_tester.py      # Testing framework
│   └── performance_monitor.py # Performance monitoring
├── playbooks/                 # Generated and custom playbooks
├── inventories/               # Environment inventories
│   ├── production/
│   ├── staging/
│   └── development/
├── vault/                     # Encrypted secrets
├── reports/                   # Generated reports
├── backups/                   # Configuration backups
└── templates/                 # Jinja2 templates
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Ansible Testing
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Ansible tests
        run: python scripts/ansible_tester.py suite --no-parallel
```

### PowerShell Automation
```powershell
# Daily maintenance script
$playbooks = @("backup_configs.yml", "health_check.yml", "compliance_audit.yml")
foreach ($playbook in $playbooks) {
    python scripts/ansible_runner.py playbook $playbook -i production --verbose 1
}

# Generate daily report
python scripts/performance_monitor.py test site.yml --save "daily_perf_$(Get-Date -Format 'yyyyMMdd').json"
```

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure all Python scripts are in the same directory
   - Install required dependencies: `pip install -r requirements.txt`

2. **Permission Errors:**
   - Ensure proper file permissions for vault files
   - Check SSH key permissions for remote connections

3. **Performance Issues:**
   - Increase the `forks` setting in ansible.cfg for large inventories
   - Use `--limit` to test on smaller host groups first

4. **Connectivity Issues:**
   - Verify inventory host addresses
   - Check SSH connectivity manually
   - Validate DNS resolution

### Debug Mode
All scripts support verbose logging:
```powershell
# Enable debug logging
$env:PYTHONPATH = "."
python -v scripts/ansible_master.py --interactive
```

## Best Practices

1. **Always test first:** Use dry-run mode before executing on production
2. **Monitor performance:** Enable monitoring for long-running playbooks
3. **Use version control:** Keep generated playbooks in git
4. **Regular backups:** Run configuration backups before changes
5. **Validate inventory:** Test connectivity before major deployments
6. **Secure secrets:** Use Ansible Vault for all sensitive data

## Contributing

To extend these scripts:

1. **Add new playbook templates** in `playbook_generator.py`
2. **Extend test cases** in `ansible_tester.py`
3. **Add monitoring metrics** in `performance_monitor.py`
4. **Create new menu options** in `ansible_master.py`

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Ansible documentation
3. Check script logs in the reports directory
4. Use the interactive help in `ansible_master.py`
