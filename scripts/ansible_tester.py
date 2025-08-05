#!/usr/bin/env python3
"""
Ansible Test Runner
Comprehensive testing framework for Ansible playbooks and configurations
Supports syntax checking, dry runs, and validation tests
"""

import os
import sys
import argparse
import subprocess
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.tree import Tree
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnsibleTester:
    """Comprehensive Ansible testing framework"""
    
    def __init__(self, base_path: str = None):
        self.console = Console()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.playbook_path = self.base_path / "playbooks"
        self.inventory_path = self.base_path / "inventories"
        self.test_results = []
        
    def syntax_check_playbook(self, playbook_name: str) -> Dict:
        """Check playbook syntax"""
        playbook_path = self.playbook_path / playbook_name
        
        if not playbook_path.exists():
            return {
                "test": "syntax_check",
                "playbook": playbook_name,
                "status": "FAIL",
                "message": f"Playbook not found: {playbook_path}",
                "duration": 0
            }
        
        start_time = time.time()
        
        cmd = ["ansible-playbook", "--syntax-check", str(playbook_path)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    "test": "syntax_check",
                    "playbook": playbook_name,
                    "status": "PASS",
                    "message": "Syntax check passed",
                    "duration": duration
                }
            else:
                return {
                    "test": "syntax_check",
                    "playbook": playbook_name,
                    "status": "FAIL",
                    "message": result.stderr,
                    "duration": duration
                }
                
        except Exception as e:
            return {
                "test": "syntax_check",
                "playbook": playbook_name,
                "status": "ERROR",
                "message": str(e),
                "duration": time.time() - start_time
            }
    
    def dry_run_playbook(self, 
                        playbook_name: str, 
                        inventory: str = "production",
                        limit: str = None) -> Dict:
        """Run playbook in check mode (dry run)"""
        playbook_path = self.playbook_path / playbook_name
        
        if not playbook_path.exists():
            return {
                "test": "dry_run",
                "playbook": playbook_name,
                "status": "FAIL",
                "message": f"Playbook not found: {playbook_path}",
                "duration": 0
            }
        
        start_time = time.time()
        
        cmd = ["ansible-playbook", "--check", str(playbook_path)]
        
        # Add inventory
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        else:
            cmd.extend(["-i", inventory])
        
        # Add limit if specified
        if limit:
            cmd.extend(["--limit", limit])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    "test": "dry_run",
                    "playbook": playbook_name,
                    "status": "PASS",
                    "message": "Dry run completed successfully",
                    "duration": duration,
                    "output": result.stdout
                }
            else:
                return {
                    "test": "dry_run",
                    "playbook": playbook_name,
                    "status": "FAIL",
                    "message": result.stderr,
                    "duration": duration,
                    "output": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                "test": "dry_run",
                "playbook": playbook_name,
                "status": "TIMEOUT",
                "message": "Dry run timed out after 5 minutes",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "test": "dry_run",
                "playbook": playbook_name,
                "status": "ERROR",
                "message": str(e),
                "duration": time.time() - start_time
            }
    
    def validate_inventory(self, inventory: str = "production") -> Dict:
        """Validate inventory file"""
        start_time = time.time()
        
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        
        if not inventory_path.exists():
            return {
                "test": "inventory_validation",
                "inventory": inventory,
                "status": "FAIL",
                "message": f"Inventory file not found: {inventory_path}",
                "duration": time.time() - start_time
            }
        
        try:
            # Check YAML syntax
            with open(inventory_path, 'r') as f:
                yaml.safe_load(f)
            
            # Test inventory with ansible-inventory
            cmd = ["ansible-inventory", "-i", str(inventory_path), "--list"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                inventory_data = json.loads(result.stdout)
                host_count = len(inventory_data.get('_meta', {}).get('hostvars', {}))
                
                return {
                    "test": "inventory_validation",
                    "inventory": inventory,
                    "status": "PASS",
                    "message": f"Inventory valid with {host_count} hosts",
                    "duration": duration,
                    "host_count": host_count
                }
            else:
                return {
                    "test": "inventory_validation",
                    "inventory": inventory,
                    "status": "FAIL",
                    "message": result.stderr,
                    "duration": duration
                }
                
        except yaml.YAMLError as e:
            return {
                "test": "inventory_validation",
                "inventory": inventory,
                "status": "FAIL",
                "message": f"YAML syntax error: {str(e)}",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "test": "inventory_validation",
                "inventory": inventory,
                "status": "ERROR",
                "message": str(e),
                "duration": time.time() - start_time
            }
    
    def test_host_connectivity(self, 
                              inventory: str = "production",
                              limit: str = None,
                              timeout: int = 10) -> Dict:
        """Test connectivity to inventory hosts"""
        start_time = time.time()
        
        cmd = ["ansible", "all", "-m", "ping", "-f", "20", "--timeout", str(timeout)]
        
        inventory_path = self.inventory_path / inventory / "hosts.yml"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        else:
            cmd.extend(["-i", inventory])
        
        if limit:
            cmd.extend(["--limit", limit])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=timeout * 2  # Allow extra time for overall command
            )
            
            duration = time.time() - start_time
            
            # Parse results
            lines = result.stdout.split('\n')
            successful_hosts = []
            failed_hosts = []
            
            for line in lines:
                if 'SUCCESS' in line:
                    host = line.split()[0]
                    successful_hosts.append(host)
                elif 'UNREACHABLE' in line or 'FAILED' in line:
                    host = line.split()[0] if line.split() else 'unknown'
                    failed_hosts.append(host)
            
            total_hosts = len(successful_hosts) + len(failed_hosts)
            success_rate = (len(successful_hosts) / total_hosts * 100) if total_hosts > 0 else 0
            
            status = "PASS" if success_rate >= 90 else "WARN" if success_rate >= 50 else "FAIL"
            
            return {
                "test": "connectivity",
                "inventory": inventory,
                "status": status,
                "message": f"{len(successful_hosts)}/{total_hosts} hosts reachable ({success_rate:.1f}%)",
                "duration": duration,
                "successful_hosts": successful_hosts,
                "failed_hosts": failed_hosts,
                "success_rate": success_rate
            }
            
        except subprocess.TimeoutExpired:
            return {
                "test": "connectivity",
                "inventory": inventory,
                "status": "TIMEOUT",
                "message": f"Connectivity test timed out after {timeout * 2} seconds",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "test": "connectivity",
                "inventory": inventory,
                "status": "ERROR",
                "message": str(e),
                "duration": time.time() - start_time
            }
    
    def validate_roles(self) -> List[Dict]:
        """Validate all roles in the roles directory"""
        results = []
        
        if not self.roles_path.exists():
            return [{
                "test": "role_validation",
                "role": "N/A",
                "status": "SKIP",
                "message": "No roles directory found",
                "duration": 0
            }]
        
        roles = [d for d in self.roles_path.iterdir() if d.is_dir()]
        
        for role_path in roles:
            start_time = time.time()
            role_name = role_path.name
            
            # Check role structure
            required_dirs = ['tasks', 'handlers', 'vars', 'defaults', 'meta', 'templates', 'files']
            missing_dirs = []
            
            for req_dir in required_dirs:
                if not (role_path / req_dir).exists():
                    missing_dirs.append(req_dir)
            
            # Check main.yml files
            main_files = ['tasks/main.yml', 'handlers/main.yml', 'vars/main.yml', 
                         'defaults/main.yml', 'meta/main.yml']
            missing_main_files = []
            invalid_yaml_files = []
            
            for main_file in main_files:
                file_path = role_path / main_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            yaml.safe_load(f)
                    except yaml.YAMLError:
                        invalid_yaml_files.append(main_file)
                else:
                    if main_file in ['tasks/main.yml', 'meta/main.yml']:  # Required files
                        missing_main_files.append(main_file)
            
            duration = time.time() - start_time
            
            # Determine status
            if missing_main_files or invalid_yaml_files:
                status = "FAIL"
                message_parts = []
                if missing_main_files:
                    message_parts.append(f"Missing required files: {', '.join(missing_main_files)}")
                if invalid_yaml_files:
                    message_parts.append(f"Invalid YAML files: {', '.join(invalid_yaml_files)}")
                message = "; ".join(message_parts)
            elif missing_dirs:
                status = "WARN"
                message = f"Missing optional directories: {', '.join(missing_dirs)}"
            else:
                status = "PASS"
                message = "Role structure valid"
            
            results.append({
                "test": "role_validation",
                "role": role_name,
                "status": status,
                "message": message,
                "duration": duration
            })
        
        return results
    
    def run_test_suite(self, 
                      test_types: List[str] = None,
                      inventory: str = "production",
                      parallel: bool = True) -> Dict:
        """Run comprehensive test suite"""
        
        if test_types is None:
            test_types = ["syntax", "inventory", "roles", "connectivity", "dry_run"]
        
        all_results = []
        
        with Progress(console=self.console) as progress:
            main_task = progress.add_task("Running test suite...", total=len(test_types))
            
            # Run tests
            if "syntax" in test_types:
                progress.console.print("[blue]Running syntax checks...[/blue]")
                syntax_results = self._run_syntax_tests(parallel=parallel)
                all_results.extend(syntax_results)
                progress.advance(main_task)
            
            if "inventory" in test_types:
                progress.console.print("[blue]Validating inventory...[/blue]")
                inventory_result = self.validate_inventory(inventory)
                all_results.append(inventory_result)
                progress.advance(main_task)
            
            if "roles" in test_types:
                progress.console.print("[blue]Validating roles...[/blue]")
                role_results = self.validate_roles()
                all_results.extend(role_results)
                progress.advance(main_task)
            
            if "connectivity" in test_types:
                progress.console.print("[blue]Testing connectivity...[/blue]")
                connectivity_result = self.test_host_connectivity(inventory)
                all_results.append(connectivity_result)
                progress.advance(main_task)
            
            if "dry_run" in test_types:
                progress.console.print("[blue]Running dry run tests...[/blue]")
                dry_run_results = self._run_dry_run_tests(inventory, parallel=parallel)
                all_results.extend(dry_run_results)
                progress.advance(main_task)
        
        # Calculate summary
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r["status"] == "PASS"])
        failed_tests = len([r for r in all_results if r["status"] == "FAIL"])
        error_tests = len([r for r in all_results if r["status"] == "ERROR"])
        warn_tests = len([r for r in all_results if r["status"] == "WARN"])
        
        return {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "warnings": warn_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "results": all_results
        }
    
    def _run_syntax_tests(self, parallel: bool = True) -> List[Dict]:
        """Run syntax tests on all playbooks"""
        playbooks = list(self.playbook_path.glob("*.yml")) + list(self.playbook_path.glob("*.yaml"))
        results = []
        
        if not playbooks:
            return [{
                "test": "syntax_check",
                "playbook": "N/A",
                "status": "SKIP",
                "message": "No playbooks found",
                "duration": 0
            }]
        
        if parallel and len(playbooks) > 1:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_playbook = {
                    executor.submit(self.syntax_check_playbook, pb.name): pb.name 
                    for pb in playbooks
                }
                
                for future in as_completed(future_to_playbook):
                    result = future.result()
                    results.append(result)
        else:
            for playbook in playbooks:
                result = self.syntax_check_playbook(playbook.name)
                results.append(result)
        
        return results
    
    def _run_dry_run_tests(self, inventory: str, parallel: bool = True) -> List[Dict]:
        """Run dry run tests on selected playbooks"""
        # Only test a subset of playbooks for dry runs to avoid overwhelming tests
        critical_playbooks = [
            "site.yml",
            "backup_configs.yml", 
            "security_hardening.yml",
            "network_health_check.yml"
        ]
        
        existing_playbooks = []
        for pb_name in critical_playbooks:
            pb_path = self.playbook_path / pb_name
            if pb_path.exists():
                existing_playbooks.append(pb_name)
        
        if not existing_playbooks:
            # Fall back to first few playbooks
            all_playbooks = list(self.playbook_path.glob("*.yml"))[:3]
            existing_playbooks = [pb.name for pb in all_playbooks]
        
        results = []
        
        if not existing_playbooks:
            return [{
                "test": "dry_run",
                "playbook": "N/A", 
                "status": "SKIP",
                "message": "No playbooks available for dry run",
                "duration": 0
            }]
        
        if parallel and len(existing_playbooks) > 1:
            with ThreadPoolExecutor(max_workers=2) as executor:  # Limit to 2 for dry runs
                future_to_playbook = {
                    executor.submit(self.dry_run_playbook, pb, inventory, "localhost"): pb 
                    for pb in existing_playbooks[:2]  # Limit to 2 playbooks
                }
                
                for future in as_completed(future_to_playbook):
                    result = future.result()
                    results.append(result)
        else:
            for playbook in existing_playbooks[:2]:  # Limit to 2 playbooks
                result = self.dry_run_playbook(playbook, inventory, "localhost")
                results.append(result)
        
        return results
    
    def display_test_results(self, test_results: Dict):
        """Display test results in a formatted table"""
        
        # Display summary
        summary = test_results["summary"]
        summary_table = Table(title="Test Suite Summary")
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Count", justify="right")
        summary_table.add_column("Percentage", justify="right")
        
        total = summary["total"]
        summary_table.add_row("Total Tests", str(total), "100.0%")
        summary_table.add_row("[green]Passed[/green]", str(summary["passed"]), 
                             f"{summary['passed']/total*100:.1f}%" if total > 0 else "0%")
        summary_table.add_row("[red]Failed[/red]", str(summary["failed"]),
                             f"{summary['failed']/total*100:.1f}%" if total > 0 else "0%")
        summary_table.add_row("[yellow]Warnings[/yellow]", str(summary["warnings"]),
                             f"{summary['warnings']/total*100:.1f}%" if total > 0 else "0%")
        summary_table.add_row("[magenta]Errors[/magenta]", str(summary["errors"]),
                             f"{summary['errors']/total*100:.1f}%" if total > 0 else "0%")
        
        self.console.print(summary_table)
        self.console.print()
        
        # Display detailed results
        results_table = Table(title="Detailed Test Results")
        results_table.add_column("Test Type", style="cyan")
        results_table.add_column("Target", style="white")
        results_table.add_column("Status", style="bold")
        results_table.add_column("Duration", justify="right")
        results_table.add_column("Message", style="dim")
        
        for result in test_results["results"]:
            status_color = {
                "PASS": "[green]PASS[/green]",
                "FAIL": "[red]FAIL[/red]", 
                "ERROR": "[magenta]ERROR[/magenta]",
                "WARN": "[yellow]WARN[/yellow]",
                "SKIP": "[blue]SKIP[/blue]",
                "TIMEOUT": "[red]TIMEOUT[/red]"
            }.get(result["status"], result["status"])
            
            target = result.get("playbook", result.get("inventory", result.get("role", "N/A")))
            duration = f"{result['duration']:.2f}s"
            message = result["message"][:80] + "..." if len(result["message"]) > 80 else result["message"]
            
            results_table.add_row(
                result["test"],
                target,
                status_color,
                duration,
                message
            )
        
        self.console.print(results_table)
        
        # Show overall status
        if summary["success_rate"] >= 90:
            self.console.print(f"\n[bold green]✓ Test suite passed ({summary['success_rate']:.1f}% success rate)[/bold green]")
        elif summary["success_rate"] >= 70:
            self.console.print(f"\n[bold yellow]⚠ Test suite completed with warnings ({summary['success_rate']:.1f}% success rate)[/bold yellow]")
        else:
            self.console.print(f"\n[bold red]✗ Test suite failed ({summary['success_rate']:.1f}% success rate)[/bold red]")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Ansible Test Runner")
    parser.add_argument("--base-path", help="Base path for Ansible project")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test suite command
    suite_parser = subparsers.add_parser("suite", help="Run full test suite")
    suite_parser.add_argument("--tests", nargs="+", 
                             choices=["syntax", "inventory", "roles", "connectivity", "dry_run"],
                             default=["syntax", "inventory", "roles", "connectivity"],
                             help="Test types to run")
    suite_parser.add_argument("-i", "--inventory", default="production", help="Inventory to test")
    suite_parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    
    # Individual test commands
    syntax_parser = subparsers.add_parser("syntax", help="Check playbook syntax")
    syntax_parser.add_argument("playbook", nargs="?", help="Specific playbook to check")
    
    inventory_parser = subparsers.add_parser("inventory", help="Validate inventory")
    inventory_parser.add_argument("-i", "--inventory", default="production", help="Inventory to validate")
    
    connectivity_parser = subparsers.add_parser("connectivity", help="Test host connectivity")
    connectivity_parser.add_argument("-i", "--inventory", default="production", help="Inventory to test")
    connectivity_parser.add_argument("-l", "--limit", help="Limit to specific hosts")
    connectivity_parser.add_argument("--timeout", type=int, default=10, help="Connection timeout")
    
    dry_run_parser = subparsers.add_parser("dry-run", help="Run playbook in check mode")
    dry_run_parser.add_argument("playbook", help="Playbook to test")
    dry_run_parser.add_argument("-i", "--inventory", default="production", help="Inventory to use")
    dry_run_parser.add_argument("-l", "--limit", help="Limit to specific hosts")
    
    subparsers.add_parser("roles", help="Validate roles")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize tester
    tester = AnsibleTester(args.base_path)
    
    try:
        if args.command == "suite":
            results = tester.run_test_suite(
                test_types=args.tests,
                inventory=args.inventory,
                parallel=not args.no_parallel
            )
            tester.display_test_results(results)
            
            # Exit with appropriate code
            if results["summary"]["success_rate"] >= 90:
                sys.exit(0)
            elif results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
                sys.exit(1)
            else:
                sys.exit(0)  # Warnings are OK
        
        elif args.command == "syntax":
            if args.playbook:
                result = tester.syntax_check_playbook(args.playbook)
                status_color = "[green]PASS[/green]" if result["status"] == "PASS" else "[red]FAIL[/red]"
                tester.console.print(f"Syntax check: {status_color} - {result['message']}")
                sys.exit(0 if result["status"] == "PASS" else 1)
            else:
                results = tester._run_syntax_tests()
                for result in results:
                    status_color = "[green]PASS[/green]" if result["status"] == "PASS" else "[red]FAIL[/red]"
                    tester.console.print(f"{result['playbook']}: {status_color} - {result['message']}")
                
                failed = any(r["status"] != "PASS" for r in results)
                sys.exit(1 if failed else 0)
        
        elif args.command == "inventory":
            result = tester.validate_inventory(args.inventory)
            status_color = "[green]PASS[/green]" if result["status"] == "PASS" else "[red]FAIL[/red]"
            tester.console.print(f"Inventory validation: {status_color} - {result['message']}")
            sys.exit(0 if result["status"] == "PASS" else 1)
        
        elif args.command == "connectivity":
            result = tester.test_host_connectivity(args.inventory, args.limit, args.timeout)
            status_colors = {
                "PASS": "[green]PASS[/green]",
                "WARN": "[yellow]WARN[/yellow]", 
                "FAIL": "[red]FAIL[/red]"
            }
            status_color = status_colors.get(result["status"], result["status"])
            tester.console.print(f"Connectivity test: {status_color} - {result['message']}")
            sys.exit(0 if result["status"] in ["PASS", "WARN"] else 1)
        
        elif args.command == "dry-run":
            result = tester.dry_run_playbook(args.playbook, args.inventory, args.limit)
            status_color = "[green]PASS[/green]" if result["status"] == "PASS" else "[red]FAIL[/red]"
            tester.console.print(f"Dry run: {status_color} - {result['message']}")
            if result.get("output"):
                tester.console.print(Panel(result["output"], title="Dry Run Output"))
            sys.exit(0 if result["status"] == "PASS" else 1)
        
        elif args.command == "roles":
            results = tester.validate_roles()
            for result in results:
                status_colors = {
                    "PASS": "[green]PASS[/green]",
                    "WARN": "[yellow]WARN[/yellow]",
                    "FAIL": "[red]FAIL[/red]"
                }
                status_color = status_colors.get(result["status"], result["status"])
                tester.console.print(f"{result['role']}: {status_color} - {result['message']}")
            
            failed = any(r["status"] == "FAIL" for r in results)
            sys.exit(1 if failed else 0)
    
    except Exception as e:
        tester.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
