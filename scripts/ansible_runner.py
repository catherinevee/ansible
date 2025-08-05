#!/usr/bin/env python3
"""
Ansible Runner Script
A comprehensive Python script for running Ansible playbooks with various configurations
Supports inventory management, vault operations, and execution monitoring
"""

import os
import sys
import argparse
import subprocess
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import concurrent.futures
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ansible_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnsibleRunner:
    """Main class for running Ansible operations"""
    
    def __init__(self, base_path: str = None):
        self.console = Console()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.inventory_path = self.base_path / "inventories"
        self.playbook_path = self.base_path / "playbooks"
        self.vault_path = self.base_path / "vault"
        
        # Ensure required directories exist
        self.inventory_path.mkdir(exist_ok=True)
        self.playbook_path.mkdir(exist_ok=True)
        self.vault_path.mkdir(exist_ok=True)
    
    def run_playbook(self, 
                    playbook_name: str,
                    inventory: str = "production",
                    limit: str = None,
                    tags: str = None,
                    skip_tags: str = None,
                    extra_vars: Dict = None,
                    dry_run: bool = False,
                    verbose: int = 0) -> Dict:
        """
        Run an Ansible playbook with specified parameters
        
        Args:
            playbook_name: Name of the playbook to run
            inventory: Inventory to use (default: production)
            limit: Limit execution to specific hosts
            tags: Run only tasks with these tags
            skip_tags: Skip tasks with these tags
            extra_vars: Extra variables to pass to playbook
            dry_run: Run in check mode
            verbose: Verbosity level (0-4)
        
        Returns:
            Dict with execution results
        """
        
        # Build ansible-playbook command
        cmd = ["ansible-playbook"]
        
        # Playbook path
        playbook_path = self.playbook_path / playbook_name
        if not playbook_path.exists():
            raise FileNotFoundError(f"Playbook {playbook_name} not found at {playbook_path}")
        cmd.append(str(playbook_path))
        
        # Inventory
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        else:
            cmd.extend(["-i", inventory])
        
        # Optional parameters
        if limit:
            cmd.extend(["--limit", limit])
        if tags:
            cmd.extend(["--tags", tags])
        if skip_tags:
            cmd.extend(["--skip-tags", skip_tags])
        if dry_run:
            cmd.append("--check")
        if verbose > 0:
            cmd.append("-" + "v" * min(verbose, 4))
        
        # Extra variables
        if extra_vars:
            for key, value in extra_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        # Execute command
        self.console.print(f"[bold blue]Executing:[/bold blue] {' '.join(cmd)}")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Running playbook...", total=None)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.base_path
                )
                
                progress.update(task, completed=True)
            
            execution_result = {
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Display results
            if result.returncode == 0:
                self.console.print("[bold green]✓ Playbook executed successfully[/bold green]")
            else:
                self.console.print(f"[bold red]✗ Playbook failed with return code {result.returncode}[/bold red]")
                self.console.print(f"[red]Error: {result.stderr}[/red]")
            
            # Log execution
            logger.info(f"Playbook {playbook_name} executed with return code {result.returncode}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing playbook: {str(e)}")
            raise
    
    def run_ad_hoc_command(self,
                          hosts: str,
                          module: str,
                          args: str = "",
                          inventory: str = "production",
                          become: bool = False) -> Dict:
        """
        Run an ad-hoc Ansible command
        
        Args:
            hosts: Target hosts pattern
            module: Ansible module to use
            args: Module arguments
            inventory: Inventory to use
            become: Use privilege escalation
        
        Returns:
            Dict with execution results
        """
        
        cmd = ["ansible", hosts, "-m", module]
        
        if args:
            cmd.extend(["-a", args])
        
        # Inventory
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        else:
            cmd.extend(["-i", inventory])
        
        if become:
            cmd.append("--become")
        
        self.console.print(f"[bold blue]Executing ad-hoc command:[/bold blue] {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            execution_result = {
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            if result.returncode == 0:
                self.console.print("[bold green]✓ Ad-hoc command executed successfully[/bold green]")
                self.console.print(result.stdout)
            else:
                self.console.print(f"[bold red]✗ Command failed[/bold red]")
                self.console.print(f"[red]{result.stderr}[/red]")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing ad-hoc command: {str(e)}")
            raise
    
    def list_playbooks(self) -> List[str]:
        """List available playbooks"""
        playbooks = []
        for file in self.playbook_path.glob("*.yml"):
            playbooks.append(file.name)
        for file in self.playbook_path.glob("*.yaml"):
            playbooks.append(file.name)
        return sorted(playbooks)
    
    def list_inventories(self) -> List[str]:
        """List available inventories"""
        inventories = []
        for directory in self.inventory_path.iterdir():
            if directory.is_dir():
                hosts_file = directory / "hosts.yml"
                if hosts_file.exists():
                    inventories.append(directory.name)
        return sorted(inventories)
    
    def validate_inventory(self, inventory: str = "production") -> bool:
        """Validate inventory syntax"""
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        
        if not inventory_path.exists():
            self.console.print(f"[red]Inventory file not found: {inventory_path}[/red]")
            return False
        
        try:
            with open(inventory_path, 'r') as f:
                yaml.safe_load(f)
            self.console.print(f"[green]✓ Inventory {inventory} is valid[/green]")
            return True
        except yaml.YAMLError as e:
            self.console.print(f"[red]✗ Inventory {inventory} has YAML errors: {e}[/red]")
            return False
    
    def check_connectivity(self, 
                          inventory: str = "production",
                          limit: str = None,
                          timeout: int = 10) -> Dict:
        """Check connectivity to all hosts in inventory"""
        
        cmd = ["ansible", "all", "-m", "ping", "-f", "20", "--timeout", str(timeout)]
        
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        else:
            cmd.extend(["-i", inventory])
        
        if limit:
            cmd.extend(["--limit", limit])
        
        self.console.print(f"[bold blue]Checking connectivity...[/bold blue]")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            # Parse results
            lines = result.stdout.split('\n')
            successful_hosts = []
            failed_hosts = []
            
            for line in lines:
                if 'SUCCESS' in line:
                    host = line.split()[0]
                    successful_hosts.append(host)
                elif 'UNREACHABLE' in line or 'FAILED' in line:
                    host = line.split()[0]
                    failed_hosts.append(host)
            
            # Display results table
            table = Table(title="Connectivity Check Results")
            table.add_column("Status", style="bold")
            table.add_column("Count", justify="right")
            table.add_column("Hosts")
            
            table.add_row(
                "[green]✓ Reachable[/green]", 
                str(len(successful_hosts)),
                ", ".join(successful_hosts[:10]) + ("..." if len(successful_hosts) > 10 else "")
            )
            table.add_row(
                "[red]✗ Unreachable[/red]", 
                str(len(failed_hosts)),
                ", ".join(failed_hosts[:10]) + ("..." if len(failed_hosts) > 10 else "")
            )
            
            self.console.print(table)
            
            return {
                "successful_hosts": successful_hosts,
                "failed_hosts": failed_hosts,
                "total_hosts": len(successful_hosts) + len(failed_hosts),
                "success_rate": len(successful_hosts) / (len(successful_hosts) + len(failed_hosts)) * 100 if (successful_hosts or failed_hosts) else 0
            }
            
        except Exception as e:
            logger.error(f"Error checking connectivity: {str(e)}")
            raise
    
    def display_inventory_tree(self, inventory: str = "production"):
        """Display inventory structure as a tree"""
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        
        if not inventory_path.exists():
            self.console.print(f"[red]Inventory file not found: {inventory_path}[/red]")
            return
        
        try:
            with open(inventory_path, 'r') as f:
                inventory_data = yaml.safe_load(f)
            
            tree = Tree(f"[bold blue]Inventory: {inventory}[/bold blue]")
            
            def add_group_to_tree(parent_node, group_name, group_data):
                if isinstance(group_data, dict):
                    group_node = parent_node.add(f"[yellow]{group_name}[/yellow]")
                    
                    if 'hosts' in group_data:
                        hosts_node = group_node.add("[green]hosts[/green]")
                        for host_name in group_data['hosts']:
                            hosts_node.add(f"[cyan]{host_name}[/cyan]")
                    
                    if 'children' in group_data:
                        children_node = group_node.add("[magenta]children[/magenta]")
                        for child_name, child_data in group_data['children'].items():
                            add_group_to_tree(children_node, child_name, child_data)
                    
                    if 'vars' in group_data:
                        vars_node = group_node.add("[blue]vars[/blue]")
                        for var_name in group_data['vars']:
                            vars_node.add(f"{var_name}")
            
            if 'all' in inventory_data:
                add_group_to_tree(tree, 'all', inventory_data['all'])
            else:
                for group_name, group_data in inventory_data.items():
                    add_group_to_tree(tree, group_name, group_data)
            
            self.console.print(tree)
            
        except Exception as e:
            self.console.print(f"[red]Error reading inventory: {e}[/red]")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Ansible Runner - Execute Ansible operations")
    parser.add_argument("--base-path", help="Base path for Ansible project")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Playbook command
    playbook_parser = subparsers.add_parser("playbook", help="Run a playbook")
    playbook_parser.add_argument("name", help="Playbook name")
    playbook_parser.add_argument("-i", "--inventory", default="production", help="Inventory to use")
    playbook_parser.add_argument("-l", "--limit", help="Limit execution to specific hosts")
    playbook_parser.add_argument("-t", "--tags", help="Run only tasks with these tags")
    playbook_parser.add_argument("--skip-tags", help="Skip tasks with these tags")
    playbook_parser.add_argument("-e", "--extra-vars", action="append", help="Extra variables (key=value)")
    playbook_parser.add_argument("-c", "--check", action="store_true", help="Run in check mode")
    playbook_parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output")
    
    # Ad-hoc command
    adhoc_parser = subparsers.add_parser("adhoc", help="Run ad-hoc command")
    adhoc_parser.add_argument("hosts", help="Target hosts pattern")
    adhoc_parser.add_argument("-m", "--module", required=True, help="Ansible module")
    adhoc_parser.add_argument("-a", "--args", default="", help="Module arguments")
    adhoc_parser.add_argument("-i", "--inventory", default="production", help="Inventory to use")
    adhoc_parser.add_argument("-b", "--become", action="store_true", help="Use privilege escalation")
    
    # List commands
    subparsers.add_parser("list-playbooks", help="List available playbooks")
    subparsers.add_parser("list-inventories", help="List available inventories")
    
    # Inventory commands
    inventory_parser = subparsers.add_parser("inventory", help="Inventory operations")
    inventory_parser.add_argument("action", choices=["validate", "tree"], help="Inventory action")
    inventory_parser.add_argument("-i", "--inventory", default="production", help="Inventory name")
    
    # Connectivity check
    ping_parser = subparsers.add_parser("ping", help="Check host connectivity")
    ping_parser.add_argument("-i", "--inventory", default="production", help="Inventory to use")
    ping_parser.add_argument("-l", "--limit", help="Limit to specific hosts")
    ping_parser.add_argument("--timeout", type=int, default=10, help="Connection timeout")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize runner
    runner = AnsibleRunner(args.base_path)
    
    try:
        if args.command == "playbook":
            extra_vars = {}
            if args.extra_vars:
                for var in args.extra_vars:
                    key, value = var.split("=", 1)
                    extra_vars[key] = value
            
            result = runner.run_playbook(
                playbook_name=args.name,
                inventory=args.inventory,
                limit=args.limit,
                tags=args.tags,
                skip_tags=args.skip_tags,
                extra_vars=extra_vars,
                dry_run=args.check,
                verbose=args.verbose
            )
            
            sys.exit(0 if result["success"] else 1)
        
        elif args.command == "adhoc":
            result = runner.run_ad_hoc_command(
                hosts=args.hosts,
                module=args.module,
                args=args.args,
                inventory=args.inventory,
                become=args.become
            )
            
            sys.exit(0 if result["success"] else 1)
        
        elif args.command == "list-playbooks":
            playbooks = runner.list_playbooks()
            runner.console.print("[bold blue]Available Playbooks:[/bold blue]")
            for playbook in playbooks:
                runner.console.print(f"  • {playbook}")
        
        elif args.command == "list-inventories":
            inventories = runner.list_inventories()
            runner.console.print("[bold blue]Available Inventories:[/bold blue]")
            for inventory in inventories:
                runner.console.print(f"  • {inventory}")
        
        elif args.command == "inventory":
            if args.action == "validate":
                runner.validate_inventory(args.inventory)
            elif args.action == "tree":
                runner.display_inventory_tree(args.inventory)
        
        elif args.command == "ping":
            runner.check_connectivity(args.inventory, args.limit, args.timeout)
    
    except Exception as e:
        runner.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
