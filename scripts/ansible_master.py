#!/usr/bin/env python3
"""
Ansible Master Controller
Main orchestration script that provides a unified interface to all Ansible Python tools
Includes inventory management, playbook execution, testing, and performance monitoring
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.tree import Tree

# Import our custom modules
sys.path.append(str(Path(__file__).parent))

try:
    from ansible_runner import AnsibleRunner
    from vault_manager import AnsibleVaultManager
    from playbook_generator import PlaybookGenerator
    from ansible_tester import AnsibleTester
    from performance_monitor import AnsiblePerformanceMonitor
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all Python scripts are in the same directory")
    sys.exit(1)

class AnsibleMasterController:
    """Master controller for all Ansible operations"""
    
    def __init__(self, base_path: str = None):
        self.console = Console()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
        # Initialize all components
        self.runner = AnsibleRunner(base_path)
        self.vault_manager = AnsibleVaultManager(base_path)
        self.playbook_generator = PlaybookGenerator(base_path)
        self.tester = AnsibleTester(base_path)
        self.performance_monitor = AnsiblePerformanceMonitor(base_path)
        
        # Ensure directory structure
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self):
        """Ensure all required directories exist"""
        required_dirs = [
            "playbooks",
            "inventories", 
            "inventories/production",
            "inventories/staging",
            "inventories/development",
            "roles",
            "group_vars",
            "host_vars",
            "vault",
            "templates",
            "files",
            "reports",
            "backups",
            "scripts"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            dir_path.mkdir(exist_ok=True)
    
    def display_main_menu(self):
        """Display the main interactive menu"""
        self.console.clear()
        
        # Header
        header = Panel.fit(
            "[bold blue]Ansible Master Controller[/bold blue]\n"
            "[dim]Comprehensive Ansible automation and management toolkit[/dim]",
            border_style="blue"
        )
        self.console.print(header)
        
        # Menu options
        menu_table = Table(show_header=False, box=None)
        menu_table.add_column("Option", style="cyan", width=8)
        menu_table.add_column("Description", style="white")
        
        menu_items = [
            ("1", "Run Playbook - Execute Ansible playbooks with monitoring"),
            ("2", "Generate Playbook - Create new playbooks from templates"),
            ("3", "Test Suite - Run comprehensive tests on playbooks and inventory"),
            ("4", "Vault Management - Encrypt/decrypt sensitive data"),
            ("5", "Performance Analysis - Monitor and analyze playbook performance"),
            ("6", "Inventory Management - View and validate inventory"),
            ("7", "System Status - Check connectivity and system health"),
            ("8", "Bulk Operations - Perform operations across multiple playbooks"),
            ("9", "Reports - Generate and view reports"),
            ("0", "Exit")
        ]
        
        for option, description in menu_items:
            menu_table.add_row(f"[bold]{option}[/bold]", description)
        
        self.console.print(menu_table)
        
        return Prompt.ask(
            "\n[bold]Select an option[/bold]",
            choices=[str(i) for i in range(10)],
            default="0"
        )
    
    def run_playbook_menu(self):
        """Interactive playbook execution menu"""
        self.console.print("[bold blue]Playbook Execution[/bold blue]")
        
        # List available playbooks
        playbooks = self.runner.list_playbooks()
        if not playbooks:
            self.console.print("[red]No playbooks found![/red]")
            return
        
        self.console.print("\n[bold]Available Playbooks:[/bold]")
        for i, playbook in enumerate(playbooks, 1):
            self.console.print(f"  {i}. {playbook}")
        
        # Select playbook
        choice = IntPrompt.ask(
            "Select playbook",
            choices=[str(i) for i in range(1, len(playbooks) + 1)]
        )
        
        selected_playbook = playbooks[choice - 1]
        
        # Select inventory
        inventories = self.runner.list_inventories()
        inventory = "production"
        if inventories:
            self.console.print(f"\n[bold]Available Inventories:[/bold] {', '.join(inventories)}")
            inventory = Prompt.ask("Select inventory", default="production")
        
        # Additional options
        limit = Prompt.ask("Limit to specific hosts (optional)", default="")
        tags = Prompt.ask("Run only specific tags (optional)", default="")
        dry_run = Confirm.ask("Run in check mode (dry run)?", default=False)
        verbose = IntPrompt.ask("Verbosity level (0-4)", default=0, choices=[str(i) for i in range(5)])
        
        # Performance monitoring
        monitor_performance = Confirm.ask("Monitor performance during execution?", default=True)
        
        # Execute playbook
        if monitor_performance:
            self.console.print("[blue]Starting monitored playbook execution...[/blue]")
            
            # Build command for monitoring
            cmd = ["ansible-playbook", str(self.base_path / "playbooks" / selected_playbook)]
            inventory_path = self.base_path / "inventories" / inventory / "hosts.yml"
            if inventory_path.exists():
                cmd.extend(["-i", str(inventory_path)])
            
            if limit:
                cmd.extend(["--limit", limit])
            if tags:
                cmd.extend(["--tags", tags])
            if dry_run:
                cmd.append("--check")
            if verbose > 0:
                cmd.append("-" + "v" * verbose)
            
            # Monitor execution
            metrics, stdout, stderr, return_code = self.performance_monitor.monitor_playbook_execution(cmd)
            
            # Display results
            if return_code == 0:
                self.console.print("[green]✓ Playbook executed successfully![/green]")
            else:
                self.console.print(f"[red]✗ Playbook failed with return code {return_code}[/red]")
                if stderr:
                    self.console.print(Panel(stderr, title="Error Output", border_style="red"))
            
            # Show performance summary
            self.console.print(f"\n[bold]Performance Summary:[/bold]")
            self.console.print(f"Duration: {metrics.duration:.2f} seconds")
            self.console.print(f"CPU Usage: {metrics.cpu_usage_avg:.1f}% avg, {metrics.cpu_usage_max:.1f}% peak")
            self.console.print(f"Memory Usage: {metrics.memory_usage_avg:.1f}% avg, {metrics.memory_usage_max:.1f}% peak")
            self.console.print(f"Tasks: {metrics.task_count}, Success Rate: {metrics.success_rate:.1f}%")
            
        else:
            # Regular execution
            result = self.runner.run_playbook(
                playbook_name=selected_playbook,
                inventory=inventory,
                limit=limit if limit else None,
                tags=tags if tags else None,
                dry_run=dry_run,
                verbose=verbose
            )
            
            if result["success"]:
                self.console.print("[green]✓ Playbook executed successfully![/green]")
            else:
                self.console.print("[red]✗ Playbook execution failed![/red]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def generate_playbook_menu(self):
        """Interactive playbook generation menu"""
        self.console.print("[bold blue]Playbook Generation[/bold blue]")
        
        success = self.playbook_generator.interactive_generator()
        
        if success:
            if Confirm.ask("Test the generated playbook?"):
                # Get the generated playbook name
                playbooks = self.playbook_generator.list_playbooks()
                if playbooks:
                    latest_playbook = sorted(playbooks)[-1]  # Get the most recent
                    result = self.tester.syntax_check_playbook(latest_playbook)
                    
                    if result["status"] == "PASS":
                        self.console.print("[green]✓ Generated playbook passed syntax check![/green]")
                    else:
                        self.console.print(f"[red]✗ Syntax check failed: {result['message']}[/red]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def test_suite_menu(self):
        """Interactive test suite menu"""
        self.console.print("[bold blue]Test Suite[/bold blue]")
        
        # Test options
        test_options = {
            "1": "syntax",
            "2": "inventory", 
            "3": "roles",
            "4": "connectivity",
            "5": "dry_run",
            "6": "all"
        }
        
        self.console.print("\n[bold]Available Tests:[/bold]")
        for key, test_type in test_options.items():
            if test_type == "all":
                self.console.print(f"  {key}. Run all tests")
            else:
                self.console.print(f"  {key}. {test_type.replace('_', ' ').title()} tests")
        
        choice = Prompt.ask(
            "Select test type",
            choices=list(test_options.keys()),
            default="6"
        )
        
        if choice == "6":
            test_types = ["syntax", "inventory", "roles", "connectivity"]
        else:
            test_types = [test_options[choice]]
        
        # Select inventory for tests
        inventories = self.runner.list_inventories()
        inventory = "production"
        if inventories:
            self.console.print(f"\n[bold]Available Inventories:[/bold] {', '.join(inventories)}")
            inventory = Prompt.ask("Select inventory for testing", default="production")
        
        # Run tests
        self.console.print(f"\n[blue]Running test suite...[/blue]")
        results = self.tester.run_test_suite(
            test_types=test_types,
            inventory=inventory,
            parallel=True
        )
        
        # Display results
        self.tester.display_test_results(results)
        
        Prompt.ask("\nPress Enter to continue")
    
    def vault_management_menu(self):
        """Interactive vault management menu"""
        self.console.print("[bold blue]Vault Management[/bold blue]")
        
        vault_options = {
            "1": "Create new vault file",
            "2": "Encrypt existing file",
            "3": "Decrypt file",
            "4": "Edit encrypted file",
            "5": "View encrypted file",
            "6": "Show vault status",
            "7": "Encrypt string"
        }
        
        self.console.print("\n[bold]Vault Operations:[/bold]")
        for key, description in vault_options.items():
            self.console.print(f"  {key}. {description}")
        
        choice = Prompt.ask(
            "Select operation",
            choices=list(vault_options.keys())
        )
        
        if choice == "1":
            # Create new vault file
            file_path = Prompt.ask("Enter vault file path (relative to vault/)", default="credentials.yml")
            full_path = self.base_path / "vault" / file_path
            
            template_type = Prompt.ask(
                "Select template type",
                choices=["credentials", "api_keys", "certificates"],
                default="credentials"
            )
            
            # Create and encrypt
            template_content = self.vault_manager.create_vault_template(template_type)
            with open(full_path, 'w') as f:
                f.write(template_content)
            
            success = self.vault_manager.encrypt_file(str(full_path))
            if success:
                self.console.print(f"[green]✓ Created and encrypted vault file: {full_path}[/green]")
        
        elif choice == "2":
            # Encrypt existing file
            file_path = Prompt.ask("Enter file path to encrypt")
            success = self.vault_manager.encrypt_file(file_path)
        
        elif choice == "3":
            # Decrypt file
            file_path = Prompt.ask("Enter encrypted file path")
            output_file = Prompt.ask("Output file (optional)", default="")
            success = self.vault_manager.decrypt_file(
                file_path, 
                output_file=output_file if output_file else None
            )
        
        elif choice == "4":
            # Edit encrypted file
            file_path = Prompt.ask("Enter encrypted file path")
            success = self.vault_manager.edit_file(file_path)
        
        elif choice == "5":
            # View encrypted file
            file_path = Prompt.ask("Enter encrypted file path")
            success = self.vault_manager.view_file(file_path)
        
        elif choice == "6":
            # Show vault status
            self.vault_manager.display_vault_status()
        
        elif choice == "7":
            # Encrypt string
            string_value = Prompt.ask("Enter string to encrypt")
            var_name = Prompt.ask("Variable name (optional)", default="")
            
            encrypted = self.vault_manager.encrypt_string(
                string_value,
                variable_name=var_name if var_name else None
            )
            
            if encrypted:
                self.console.print(Panel(encrypted, title="Encrypted String"))
        
        Prompt.ask("\nPress Enter to continue")
    
    def performance_analysis_menu(self):
        """Interactive performance analysis menu"""
        self.console.print("[bold blue]Performance Analysis[/bold blue]")
        
        playbooks = self.runner.list_playbooks()
        if not playbooks:
            self.console.print("[red]No playbooks found![/red]")
            Prompt.ask("Press Enter to continue")
            return
        
        self.console.print("\n[bold]Available Playbooks:[/bold]")
        for i, playbook in enumerate(playbooks, 1):
            self.console.print(f"  {i}. {playbook}")
        
        choice = IntPrompt.ask(
            "Select playbook for performance testing",
            choices=[str(i) for i in range(1, len(playbooks) + 1)]
        )
        
        selected_playbook = playbooks[choice - 1]
        
        # Test parameters
        iterations = IntPrompt.ask("Number of test iterations", default=1)
        inventory = Prompt.ask("Inventory to use", default="production")
        
        # Run performance test
        self.console.print(f"\n[blue]Running performance test on {selected_playbook}...[/blue]")
        
        metrics_list = self.performance_monitor.run_performance_test(
            playbook_name=selected_playbook,
            inventory=inventory,
            iterations=iterations
        )
        
        # Analyze and display results
        analysis = self.performance_monitor.analyze_performance(metrics_list)
        self.performance_monitor.display_performance_report(analysis, metrics_list)
        
        # Save results
        if Confirm.ask("Save performance metrics to file?"):
            filename = Prompt.ask("Filename", default=f"perf_test_{selected_playbook}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            self.performance_monitor.save_metrics(metrics_list, filename)
        
        Prompt.ask("\nPress Enter to continue")
    
    def inventory_management_menu(self):
        """Interactive inventory management menu"""
        self.console.print("[bold blue]Inventory Management[/bold blue]")
        
        inventories = self.runner.list_inventories()
        
        if not inventories:
            self.console.print("[red]No inventories found![/red]")
            Prompt.ask("Press Enter to continue")
            return
        
        self.console.print(f"\n[bold]Available Inventories:[/bold] {', '.join(inventories)}")
        
        inventory = Prompt.ask("Select inventory", default="production")
        
        # Inventory operations
        inv_options = {
            "1": "View inventory tree",
            "2": "Validate inventory",
            "3": "List all hosts",
            "4": "Show inventory statistics"
        }
        
        self.console.print("\n[bold]Inventory Operations:[/bold]")
        for key, description in inv_options.items():
            self.console.print(f"  {key}. {description}")
        
        choice = Prompt.ask("Select operation", choices=list(inv_options.keys()))
        
        if choice == "1":
            self.runner.display_inventory_tree(inventory)
        elif choice == "2":
            self.runner.validate_inventory(inventory)
        elif choice == "3":
            result = self.runner.run_ad_hoc_command("all", "debug", "msg='{{ inventory_hostname }}'", inventory)
        elif choice == "4":
            # Show statistics
            result = self.runner.run_ad_hoc_command("all", "setup", "filter=ansible_distribution*", inventory)
        
        Prompt.ask("\nPress Enter to continue")
    
    def system_status_menu(self):
        """System status and health check menu"""
        self.console.print("[bold blue]System Status[/bold blue]")
        
        inventories = self.runner.list_inventories()
        inventory = "production"
        
        if inventories:
            self.console.print(f"\n[bold]Available Inventories:[/bold] {', '.join(inventories)}")
            inventory = Prompt.ask("Select inventory for health check", default="production")
        
        # Run connectivity check
        self.console.print(f"\n[blue]Checking connectivity to {inventory} inventory...[/blue]")
        connectivity_result = self.runner.check_connectivity(inventory)
        
        # Run basic system info gathering
        if connectivity_result["successful_hosts"]:
            self.console.print("\n[blue]Gathering system information from reachable hosts...[/blue]")
            
            system_info = self.runner.run_ad_hoc_command(
                "all",
                "setup",
                "filter=ansible_system*",
                inventory
            )
        
        Prompt.ask("\nPress Enter to continue")
    
    def run_interactive_mode(self):
        """Run the interactive menu system"""
        while True:
            try:
                choice = self.display_main_menu()
                
                if choice == "0":
                    self.console.print("[blue]Goodbye![/blue]")
                    break
                elif choice == "1":
                    self.run_playbook_menu()
                elif choice == "2":
                    self.generate_playbook_menu()
                elif choice == "3":
                    self.test_suite_menu()
                elif choice == "4":
                    self.vault_management_menu()
                elif choice == "5":
                    self.performance_analysis_menu()
                elif choice == "6":
                    self.inventory_management_menu()
                elif choice == "7":
                    self.system_status_menu()
                elif choice == "8":
                    self.console.print("[yellow]Bulk operations coming soon![/yellow]")
                    Prompt.ask("Press Enter to continue")
                elif choice == "9":
                    self.console.print("[yellow]Reports feature coming soon![/yellow]")
                    Prompt.ask("Press Enter to continue")
                
            except KeyboardInterrupt:
                self.console.print("\n[blue]Operation cancelled by user[/blue]")
                if Confirm.ask("Exit application?"):
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
                if not Confirm.ask("Continue?"):
                    break

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Ansible Master Controller")
    parser.add_argument("--base-path", help="Base path for Ansible project")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    
    # Direct command options
    parser.add_argument("--run", help="Run a specific playbook")
    parser.add_argument("--inventory", default="production", help="Inventory to use")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    parser.add_argument("--generate", help="Generate a playbook of specified type")
    parser.add_argument("--vault-status", action="store_true", help="Show vault status")
    parser.add_argument("--connectivity", action="store_true", help="Check host connectivity")
    
    args = parser.parse_args()
    
    # Initialize controller
    controller = AnsibleMasterController(args.base_path)
    
    try:
        if args.interactive or not any([args.run, args.test, args.generate, args.vault_status, args.connectivity]):
            # Start interactive mode
            controller.run_interactive_mode()
        else:
            # Handle direct commands
            if args.run:
                result = controller.runner.run_playbook(args.run, args.inventory)
                sys.exit(0 if result["success"] else 1)
            
            elif args.test:
                results = controller.tester.run_test_suite(inventory=args.inventory)
                controller.tester.display_test_results(results)
                sys.exit(0 if results["summary"]["success_rate"] >= 90 else 1)
            
            elif args.generate:
                success = controller.playbook_generator.interactive_generator()
                sys.exit(0 if success else 1)
            
            elif args.vault_status:
                controller.vault_manager.display_vault_status()
            
            elif args.connectivity:
                controller.runner.check_connectivity(args.inventory)
    
    except Exception as e:
        controller.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
