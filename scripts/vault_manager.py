#!/usr/bin/env python3
"""
Ansible Vault Manager
Comprehensive Python script for managing Ansible Vault operations
Supports encryption, decryption, editing, and key rotation
"""

import os
import sys
import argparse
import subprocess
import yaml
import json
import getpass
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnsibleVaultManager:
    """Manager for Ansible Vault operations"""
    
    def __init__(self, base_path: str = None):
        self.console = Console()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.vault_path = self.base_path / "vault"
        self.group_vars_path = self.base_path / "group_vars"
        self.host_vars_path = self.base_path / "host_vars"
        
        # Ensure vault directory exists
        self.vault_path.mkdir(exist_ok=True)
        self.group_vars_path.mkdir(exist_ok=True)
        self.host_vars_path.mkdir(exist_ok=True)
    
    def encrypt_file(self, file_path: str, vault_id: str = None) -> bool:
        """Encrypt a file with ansible-vault"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return False
        
        # Check if already encrypted
        if self.is_encrypted(file_path):
            self.console.print(f"[yellow]File {file_path} is already encrypted[/yellow]")
            return True
        
        cmd = ["ansible-vault", "encrypt"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        cmd.append(str(file_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.console.print(f"[green]✓ Successfully encrypted {file_path}[/green]")
                return True
            else:
                self.console.print(f"[red]✗ Failed to encrypt {file_path}: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error encrypting file: {str(e)}[/red]")
            return False
    
    def decrypt_file(self, file_path: str, vault_id: str = None, output_file: str = None) -> bool:
        """Decrypt a file with ansible-vault"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return False
        
        if not self.is_encrypted(file_path):
            self.console.print(f"[yellow]File {file_path} is not encrypted[/yellow]")
            return True
        
        cmd = ["ansible-vault", "decrypt"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        if output_file:
            cmd.extend(["--output", output_file])
        
        cmd.append(str(file_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                output_path = output_file if output_file else file_path
                self.console.print(f"[green]✓ Successfully decrypted to {output_path}[/green]")
                return True
            else:
                self.console.print(f"[red]✗ Failed to decrypt {file_path}: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error decrypting file: {str(e)}[/red]")
            return False
    
    def view_file(self, file_path: str, vault_id: str = None) -> bool:
        """View encrypted file content without decrypting to disk"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return False
        
        cmd = ["ansible-vault", "view"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        cmd.append(str(file_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                text=True
            )
            
            return result.returncode == 0
                
        except Exception as e:
            self.console.print(f"[red]Error viewing file: {str(e)}[/red]")
            return False
    
    def edit_file(self, file_path: str, vault_id: str = None) -> bool:
        """Edit encrypted file with ansible-vault edit"""
        file_path = Path(file_path)
        
        cmd = ["ansible-vault", "edit"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        cmd.append(str(file_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path
            )
            
            if result.returncode == 0:
                self.console.print(f"[green]✓ Successfully edited {file_path}[/green]")
                return True
            else:
                self.console.print(f"[red]✗ Failed to edit {file_path}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error editing file: {str(e)}[/red]")
            return False
    
    def rekey_file(self, file_path: str, vault_id: str = None, new_vault_id: str = None) -> bool:
        """Change the vault password for a file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return False
        
        cmd = ["ansible-vault", "rekey"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        if new_vault_id:
            cmd.extend(["--new-vault-id", new_vault_id])
        
        cmd.append(str(file_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.console.print(f"[green]✓ Successfully rekeyed {file_path}[/green]")
                return True
            else:
                self.console.print(f"[red]✗ Failed to rekey {file_path}: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error rekeying file: {str(e)}[/red]")
            return False
    
    def is_encrypted(self, file_path: Path) -> bool:
        """Check if a file is encrypted with ansible-vault"""
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
                return first_line.startswith('$ANSIBLE_VAULT;')
        except Exception:
            return False
    
    def create_vault_file(self, file_path: str, vault_id: str = None) -> bool:
        """Create a new encrypted vault file"""
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ["ansible-vault", "create"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        cmd.append(str(file_path))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path
            )
            
            if result.returncode == 0:
                self.console.print(f"[green]✓ Successfully created vault file {file_path}[/green]")
                return True
            else:
                self.console.print(f"[red]✗ Failed to create vault file {file_path}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error creating vault file: {str(e)}[/red]")
            return False
    
    def encrypt_string(self, string_value: str, variable_name: str = None, vault_id: str = None) -> str:
        """Encrypt a string value"""
        cmd = ["ansible-vault", "encrypt_string"]
        
        if vault_id:
            cmd.extend(["--vault-id", vault_id])
        
        if variable_name:
            cmd.extend(["--name", variable_name])
        
        cmd.append(string_value)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                input=string_value
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.console.print(f"[red]✗ Failed to encrypt string: {result.stderr}[/red]")
                return None
                
        except Exception as e:
            self.console.print(f"[red]Error encrypting string: {str(e)}[/red]")
            return None
    
    def list_vault_files(self) -> List[Path]:
        """List all vault files in the project"""
        vault_files = []
        
        # Search in common locations
        search_paths = [
            self.vault_path,
            self.group_vars_path,
            self.host_vars_path,
            self.base_path / "inventories"
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                for file_path in search_path.rglob("*"):
                    if file_path.is_file() and self.is_encrypted(file_path):
                        vault_files.append(file_path)
        
        return sorted(vault_files)
    
    def display_vault_status(self):
        """Display status of all vault files"""
        vault_files = self.list_vault_files()
        
        if not vault_files:
            self.console.print("[yellow]No encrypted vault files found[/yellow]")
            return
        
        table = Table(title="Vault Files Status")
        table.add_column("File Path", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Size", justify="right")
        
        for file_path in vault_files:
            relative_path = file_path.relative_to(self.base_path)
            size = file_path.stat().st_size
            status = "[green]Encrypted[/green]" if self.is_encrypted(file_path) else "[red]Not Encrypted[/red]"
            
            table.add_row(str(relative_path), status, f"{size} bytes")
        
        self.console.print(table)
    
    def create_vault_template(self, template_type: str = "credentials") -> str:
        """Create vault file templates"""
        templates = {
            "credentials": {
                "vault_cisco_username": "admin",
                "vault_cisco_password": "changeme",
                "vault_cisco_enable_password": "changeme",
                "vault_arista_username": "admin", 
                "vault_arista_password": "changeme",
                "vault_juniper_username": "admin",
                "vault_juniper_password": "changeme",
                "vault_panos_username": "admin",
                "vault_panos_password": "changeme",
                "vault_fortigate_username": "admin",
                "vault_fortigate_password": "changeme",
                "vault_fortigate_api_token": "changeme"
            },
            "api_keys": {
                "vault_aws_access_key": "AKIA...",
                "vault_aws_secret_key": "changeme",
                "vault_azure_client_id": "changeme",
                "vault_azure_client_secret": "changeme",
                "vault_gcp_service_account_key": "changeme"
            },
            "certificates": {
                "vault_ssl_private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
                "vault_ssl_certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
                "vault_ca_certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
            }
        }
        
        if template_type in templates:
            return yaml.dump(templates[template_type], default_flow_style=False)
        else:
            return yaml.dump(templates["credentials"], default_flow_style=False)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Ansible Vault Manager")
    parser.add_argument("--base-path", help="Base path for Ansible project")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    encrypt_parser.add_argument("file", help="File to encrypt")
    encrypt_parser.add_argument("--vault-id", help="Vault ID to use")
    
    # Decrypt command
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    decrypt_parser.add_argument("file", help="File to decrypt")
    decrypt_parser.add_argument("--vault-id", help="Vault ID to use")
    decrypt_parser.add_argument("--output", help="Output file path")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View encrypted file")
    view_parser.add_argument("file", help="File to view")
    view_parser.add_argument("--vault-id", help="Vault ID to use")
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit encrypted file")
    edit_parser.add_argument("file", help="File to edit")
    edit_parser.add_argument("--vault-id", help="Vault ID to use")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new vault file")
    create_parser.add_argument("file", help="File to create")
    create_parser.add_argument("--vault-id", help="Vault ID to use")
    create_parser.add_argument("--template", choices=["credentials", "api_keys", "certificates"], 
                              default="credentials", help="Template type")
    
    # Rekey command
    rekey_parser = subparsers.add_parser("rekey", help="Change vault password")
    rekey_parser.add_argument("file", help="File to rekey")
    rekey_parser.add_argument("--vault-id", help="Current vault ID")
    rekey_parser.add_argument("--new-vault-id", help="New vault ID")
    
    # Encrypt string command
    encrypt_string_parser = subparsers.add_parser("encrypt-string", help="Encrypt a string")
    encrypt_string_parser.add_argument("string", help="String to encrypt")
    encrypt_string_parser.add_argument("--name", help="Variable name")
    encrypt_string_parser.add_argument("--vault-id", help="Vault ID to use")
    
    # Status command
    subparsers.add_parser("status", help="Show vault files status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = AnsibleVaultManager(args.base_path)
    
    try:
        if args.command == "encrypt":
            success = manager.encrypt_file(args.file, args.vault_id)
            sys.exit(0 if success else 1)
        
        elif args.command == "decrypt":
            success = manager.decrypt_file(args.file, args.vault_id, args.output)
            sys.exit(0 if success else 1)
        
        elif args.command == "view":
            success = manager.view_file(args.file, args.vault_id)
            sys.exit(0 if success else 1)
        
        elif args.command == "edit":
            success = manager.edit_file(args.file, args.vault_id)
            sys.exit(0 if success else 1)
        
        elif args.command == "create":
            # Create template file first
            file_path = Path(args.file)
            if not file_path.exists():
                template_content = manager.create_vault_template(args.template)
                with open(file_path, 'w') as f:
                    f.write(template_content)
                manager.console.print(f"[blue]Created template file: {file_path}[/blue]")
            
            success = manager.encrypt_file(args.file, args.vault_id)
            sys.exit(0 if success else 1)
        
        elif args.command == "rekey":
            success = manager.rekey_file(args.file, args.vault_id, args.new_vault_id)
            sys.exit(0 if success else 1)
        
        elif args.command == "encrypt-string":
            encrypted = manager.encrypt_string(args.string, args.name, args.vault_id)
            if encrypted:
                manager.console.print(encrypted)
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.command == "status":
            manager.display_vault_status()
    
    except Exception as e:
        manager.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
