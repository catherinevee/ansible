#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Ansible Master Controller Launcher for Windows
.DESCRIPTION
    PowerShell launcher script for the Ansible Python automation tools.
    Provides easy access to all Ansible management functions.
.PARAMETER Action
    The action to perform (interactive, run, test, generate, vault, monitor)
.PARAMETER Playbook
    The playbook to run (when Action is 'run')
.PARAMETER Inventory
    The inventory to use (default: production)
.EXAMPLE
    .\ansible.ps1 -Action interactive
    .\ansible.ps1 -Action run -Playbook site.yml -Inventory production
    .\ansible.ps1 -Action test
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("interactive", "run", "test", "generate", "vault", "monitor", "help")]
    [string]$Action = "interactive",
    
    [Parameter(Position=1)]
    [string]$Playbook = "",
    
    [Parameter(Position=2)]
    [string]$Inventory = "production",
    
    [switch]$Help
)

# Script configuration
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScripts = Join-Path $ScriptPath "scripts"
$MasterScript = Join-Path $PythonScripts "ansible_master.py"

# Color functions for better output
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColoredOutput "ℹ $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "⚠ $Message" "Yellow"
}

# Help function
function Show-Help {
    Write-Host @"
Ansible Master Controller - PowerShell Launcher

USAGE:
    .\ansible.ps1 [ACTION] [OPTIONS]

ACTIONS:
    interactive     Start interactive menu (default)
    run            Run a specific playbook
    test           Run test suite
    generate       Generate new playbook
    vault          Manage vault operations
    monitor        Monitor playbook performance
    help           Show this help message

EXAMPLES:
    .\ansible.ps1                                    # Start interactive mode
    .\ansible.ps1 interactive                       # Start interactive mode
    .\ansible.ps1 run site.yml                     # Run site.yml with production inventory
    .\ansible.ps1 run backup_configs.yml staging   # Run backup with staging inventory
    .\ansible.ps1 test                             # Run full test suite
    .\ansible.ps1 generate                         # Interactive playbook generation
    .\ansible.ps1 vault                           # Vault management operations
    .\ansible.ps1 monitor                         # Performance monitoring

REQUIREMENTS:
    - Python 3.7 or higher
    - Required Python packages (pip install -r requirements.txt)
    - Ansible 4.0 or higher

DIRECTORIES:
    The script expects the following structure:
    ./
    ├── ansible.ps1           # This launcher script
    ├── requirements.txt      # Python dependencies
    ├── ansible.cfg          # Ansible configuration
    ├── scripts/             # Python automation scripts
    ├── playbooks/           # Ansible playbooks
    ├── inventories/         # Environment inventories
    └── vault/              # Encrypted secrets

For more information, see scripts/README.md
"@
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Python is not installed or not in PATH"
            Write-Host "Please install Python 3.7 or higher from https://python.org"
            return $false
        }
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error "Failed to check Python installation"
        return $false
    }
    
    # Check if master script exists
    if (-not (Test-Path $MasterScript)) {
        Write-Error "Master script not found: $MasterScript"
        Write-Host "Please ensure the scripts directory contains all Python files"
        return $false
    }
    Write-Success "Master script found"
    
    # Check requirements.txt
    $RequirementsFile = Join-Path $ScriptPath "requirements.txt"
    if (-not (Test-Path $RequirementsFile)) {
        Write-Warning "requirements.txt not found - some features may not work"
    }
    else {
        Write-Success "Requirements file found"
    }
    
    # Check Ansible
    try {
        $ansibleVersion = ansible --version 2>&1 | Select-Object -First 1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Ansible not found - install with: pip install ansible"
        }
        else {
            Write-Success "Ansible found: $($ansibleVersion -replace '\[.*\]', '')"
        }
    }
    catch {
        Write-Warning "Could not check Ansible installation"
    }
    
    return $true
}

# Install Python dependencies
function Install-Dependencies {
    $RequirementsFile = Join-Path $ScriptPath "requirements.txt"
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-Warning "No requirements.txt found - skipping dependency installation"
        return
    }
    
    Write-Info "Installing Python dependencies..."
    try {
        $result = pip install -r $RequirementsFile 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies installed successfully"
        }
        else {
            Write-Warning "Some dependencies may have failed to install"
            Write-Host $result
        }
    }
    catch {
        Write-Error "Failed to install dependencies: $_"
    }
}

# Main execution function
function Invoke-AnsibleMaster {
    param(
        [string]$Action,
        [string]$Playbook,
        [string]$Inventory
    )
    
    # Build Python command
    $PythonArgs = @($MasterScript)
    
    switch ($Action.ToLower()) {
        "interactive" {
            $PythonArgs += @("--interactive")
        }
        "run" {
            if ([string]::IsNullOrEmpty($Playbook)) {
                Write-Error "Playbook name is required for 'run' action"
                Write-Host "Usage: .\ansible.ps1 run <playbook_name> [inventory]"
                return 1
            }
            $PythonArgs += @("--run", $Playbook, "--inventory", $Inventory)
        }
        "test" {
            $PythonArgs += @("--test", "--inventory", $Inventory)
        }
        "generate" {
            $PythonArgs += @("--generate", "interactive")
        }
        "vault" {
            $PythonArgs += @("--vault-status")
        }
        "monitor" {
            Write-Info "Starting performance monitoring mode..."
            $PythonArgs = @((Join-Path $PythonScripts "performance_monitor.py"), "test")
            if (-not [string]::IsNullOrEmpty($Playbook)) {
                $PythonArgs += $Playbook
            }
        }
        default {
            Write-Error "Unknown action: $Action"
            Show-Help
            return 1
        }
    }
    
    # Execute Python script
    Write-Info "Executing: python $($PythonArgs -join ' ')"
    try {
        & python @PythonArgs
        return $LASTEXITCODE
    }
    catch {
        Write-Error "Failed to execute Python script: $_"
        return 1
    }
}

# Main script execution
function Main {
    # Handle help
    if ($Help -or $Action -eq "help") {
        Show-Help
        return 0
    }
    
    # Display banner
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                   Ansible Master Controller                  ║
║              PowerShell Launcher for Windows                 ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites check failed"
        return 1
    }
    
    # Offer to install dependencies
    $RequirementsFile = Join-Path $ScriptPath "requirements.txt"
    if ((Test-Path $RequirementsFile) -and $Action -eq "interactive") {
        $installDeps = Read-Host "Install/update Python dependencies? (y/N)"
        if ($installDeps -match "^[Yy]") {
            Install-Dependencies
        }
    }
    
    # Set working directory
    Push-Location $ScriptPath
    
    try {
        # Execute the requested action
        $exitCode = Invoke-AnsibleMaster -Action $Action -Playbook $Playbook -Inventory $Inventory
        return $exitCode
    }
    finally {
        Pop-Location
    }
}

# Run main function and exit with proper code
$exitCode = Main
exit $exitCode
