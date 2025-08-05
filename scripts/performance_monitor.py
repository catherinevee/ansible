#!/usr/bin/env python3
"""
Ansible Performance Monitor
Monitor and analyze performance of Ansible playbook executions
Provides metrics, timing analysis, and optimization recommendations
"""

import os
import sys
import time
import json
import argparse
import subprocess
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics"""
    start_time: str
    end_time: str
    duration: float
    cpu_usage_avg: float
    cpu_usage_max: float
    memory_usage_avg: float
    memory_usage_max: float
    network_io: Dict[str, int]
    disk_io: Dict[str, int]
    task_count: int
    host_count: int
    success_rate: float

class AnsiblePerformanceMonitor:
    """Monitor Ansible playbook performance"""
    
    def __init__(self, base_path: str = None):
        self.console = Console()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.monitoring = False
        self.metrics = []
        
    def monitor_playbook_execution(self, 
                                  command: List[str],
                                  sample_interval: float = 1.0) -> PerformanceMetrics:
        """Monitor a playbook execution and collect performance metrics"""
        
        # Initialize metrics tracking
        cpu_samples = []
        memory_samples = []
        start_network = psutil.net_io_counters()
        start_disk = psutil.disk_io_counters()
        
        start_time = datetime.now()
        
        # Start the Ansible process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.base_path
        )
        
        # Monitor system resources
        def collect_metrics():
            while self.monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    
                    cpu_samples.append(cpu_percent)
                    memory_samples.append(memory.percent)
                    
                    time.sleep(sample_interval)
                except:
                    break
        
        # Start monitoring thread
        self.monitoring = True
        monitor_thread = threading.Thread(target=collect_metrics)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Wait for process to complete
        stdout, stderr = process.communicate()
        
        # Stop monitoring
        self.monitoring = False
        monitor_thread.join(timeout=1)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Collect final network and disk stats
        end_network = psutil.net_io_counters()
        end_disk = psutil.disk_io_counters()
        
        # Parse Ansible output for task and host information
        task_count, host_count, success_rate = self._parse_ansible_output(stdout, stderr)
        
        # Create performance metrics
        metrics = PerformanceMetrics(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration=duration,
            cpu_usage_avg=sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0,
            cpu_usage_max=max(cpu_samples) if cpu_samples else 0,
            memory_usage_avg=sum(memory_samples) / len(memory_samples) if memory_samples else 0,
            memory_usage_max=max(memory_samples) if memory_samples else 0,
            network_io={
                "bytes_sent": end_network.bytes_sent - start_network.bytes_sent,
                "bytes_recv": end_network.bytes_recv - start_network.bytes_recv,
                "packets_sent": end_network.packets_sent - start_network.packets_sent,
                "packets_recv": end_network.packets_recv - start_network.packets_recv
            },
            disk_io={
                "read_bytes": end_disk.read_bytes - start_disk.read_bytes if end_disk and start_disk else 0,
                "write_bytes": end_disk.write_bytes - start_disk.write_bytes if end_disk and start_disk else 0,
                "read_count": end_disk.read_count - start_disk.read_count if end_disk and start_disk else 0,
                "write_count": end_disk.write_count - start_disk.write_count if end_disk and start_disk else 0
            },
            task_count=task_count,
            host_count=host_count,
            success_rate=success_rate
        )
        
        return metrics, stdout, stderr, process.returncode
    
    def _parse_ansible_output(self, stdout: str, stderr: str) -> tuple:
        """Parse Ansible output to extract task and host information"""
        task_count = 0
        host_count = 0
        success_rate = 0.0
        
        lines = stdout.split('\n')
        
        # Count tasks (lines starting with "TASK [")
        task_count = len([line for line in lines if line.strip().startswith('TASK [')])
        
        # Look for play recap section
        in_recap = False
        successful_hosts = 0
        total_hosts = 0
        
        for line in lines:
            if 'PLAY RECAP' in line:
                in_recap = True
                continue
            
            if in_recap:
                # Parse recap lines like: "hostname : ok=5 changed=0 failed=0 skipped=0"
                if ':' in line and ('ok=' in line or 'failed=' in line):
                    total_hosts += 1
                    if 'failed=0' in line and 'unreachable=0' in line:
                        successful_hosts += 1
        
        host_count = total_hosts
        if total_hosts > 0:
            success_rate = (successful_hosts / total_hosts) * 100
        
        return task_count, host_count, success_rate
    
    def run_performance_test(self, 
                           playbook_name: str,
                           inventory: str = "production",
                           iterations: int = 1,
                           sample_interval: float = 1.0) -> List[PerformanceMetrics]:
        """Run performance test with multiple iterations"""
        
        playbook_path = self.base_path / "playbooks" / playbook_name
        if not playbook_path.exists():
            raise FileNotFoundError(f"Playbook not found: {playbook_path}")
        
        inventory_path = self.base_path / "inventories" / inventory / "hosts.yml"
        
        # Build command
        cmd = ["ansible-playbook", str(playbook_path)]
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        else:
            cmd.extend(["-i", inventory])
        
        results = []
        
        with Progress(console=self.console) as progress:
            task = progress.add_task(f"Running performance test ({iterations} iterations)...", total=iterations)
            
            for i in range(iterations):
                progress.console.print(f"[blue]Running iteration {i+1}/{iterations}...[/blue]")
                
                metrics, stdout, stderr, return_code = self.monitor_playbook_execution(
                    cmd, sample_interval
                )
                
                results.append(metrics)
                progress.advance(task)
                
                # Brief pause between iterations
                if i < iterations - 1:
                    time.sleep(2)
        
        return results
    
    def analyze_performance(self, metrics_list: List[PerformanceMetrics]) -> Dict:
        """Analyze performance metrics and provide insights"""
        
        if not metrics_list:
            return {"error": "No metrics to analyze"}
        
        # Calculate averages and statistics
        durations = [m.duration for m in metrics_list]
        cpu_avgs = [m.cpu_usage_avg for m in metrics_list]
        cpu_maxs = [m.cpu_usage_max for m in metrics_list]
        memory_avgs = [m.memory_usage_avg for m in metrics_list]
        memory_maxs = [m.memory_usage_max for m in metrics_list]
        
        analysis = {
            "execution_stats": {
                "iterations": len(metrics_list),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "duration_variance": self._calculate_variance(durations)
            },
            "resource_usage": {
                "cpu": {
                    "avg_usage": sum(cpu_avgs) / len(cpu_avgs),
                    "max_usage": max(cpu_maxs),
                    "avg_peak": sum(cpu_maxs) / len(cpu_maxs)
                },
                "memory": {
                    "avg_usage": sum(memory_avgs) / len(memory_avgs),
                    "max_usage": max(memory_maxs),
                    "avg_peak": sum(memory_maxs) / len(memory_maxs)
                }
            },
            "network_io": {
                "total_bytes_sent": sum(m.network_io["bytes_sent"] for m in metrics_list),
                "total_bytes_recv": sum(m.network_io["bytes_recv"] for m in metrics_list),
                "avg_bytes_sent": sum(m.network_io["bytes_sent"] for m in metrics_list) / len(metrics_list),
                "avg_bytes_recv": sum(m.network_io["bytes_recv"] for m in metrics_list) / len(metrics_list)
            },
            "playbook_stats": {
                "avg_tasks": sum(m.task_count for m in metrics_list) / len(metrics_list),
                "avg_hosts": sum(m.host_count for m in metrics_list) / len(metrics_list),
                "avg_success_rate": sum(m.success_rate for m in metrics_list) / len(metrics_list)
            }
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, metrics_list)
        analysis["recommendations"] = recommendations
        
        return analysis
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _generate_recommendations(self, analysis: Dict, metrics_list: List[PerformanceMetrics]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Duration recommendations
        avg_duration = analysis["execution_stats"]["avg_duration"]
        if avg_duration > 300:  # 5 minutes
            recommendations.append("Consider breaking down long-running playbooks into smaller, focused playbooks")
        
        variance = analysis["execution_stats"]["duration_variance"]
        if variance > 100:  # High variance
            recommendations.append("Execution time varies significantly - investigate inconsistent task performance")
        
        # CPU recommendations
        avg_cpu = analysis["resource_usage"]["cpu"]["avg_usage"]
        max_cpu = analysis["resource_usage"]["cpu"]["max_usage"]
        
        if avg_cpu > 80:
            recommendations.append("High CPU usage detected - consider running playbooks during off-peak hours")
        if max_cpu > 95:
            recommendations.append("CPU usage peaked very high - consider increasing parallelism limits")
        
        # Memory recommendations
        avg_memory = analysis["resource_usage"]["memory"]["avg_usage"]
        max_memory = analysis["resource_usage"]["memory"]["max_usage"]
        
        if avg_memory > 80:
            recommendations.append("High memory usage - consider reducing gather_facts or using explicit fact gathering")
        if max_memory > 90:
            recommendations.append("Memory usage peaked critically high - monitor for memory leaks")
        
        # Network recommendations
        avg_bytes = analysis["network_io"]["avg_bytes_sent"] + analysis["network_io"]["avg_bytes_recv"]
        if avg_bytes > 100 * 1024 * 1024:  # 100MB
            recommendations.append("High network usage - consider optimizing file transfers and template sizes")
        
        # Performance recommendations based on task/host ratio
        if len(metrics_list) > 0:
            avg_tasks = analysis["playbook_stats"]["avg_tasks"]
            avg_hosts = analysis["playbook_stats"]["avg_hosts"]
            
            if avg_hosts > 50 and avg_duration > 180:
                recommendations.append("Consider increasing 'forks' setting to improve parallelism for large inventories")
            
            if avg_tasks > 100:
                recommendations.append("Large number of tasks detected - consider using roles or includes for better organization")
        
        # Success rate recommendations
        success_rate = analysis["playbook_stats"]["avg_success_rate"]
        if success_rate < 100:
            recommendations.append(f"Success rate is {success_rate:.1f}% - investigate failing hosts and tasks")
        
        if not recommendations:
            recommendations.append("Performance looks good! No immediate optimizations needed.")
        
        return recommendations
    
    def display_performance_report(self, analysis: Dict, metrics_list: List[PerformanceMetrics]):
        """Display comprehensive performance report"""
        
        # Execution Statistics
        exec_stats = analysis["execution_stats"]
        stats_table = Table(title="Execution Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Iterations", str(exec_stats["iterations"]))
        stats_table.add_row("Average Duration", f"{exec_stats['avg_duration']:.2f} seconds")
        stats_table.add_row("Fastest Run", f"{exec_stats['min_duration']:.2f} seconds")
        stats_table.add_row("Slowest Run", f"{exec_stats['max_duration']:.2f} seconds")
        stats_table.add_row("Duration Variance", f"{exec_stats['duration_variance']:.2f}")
        
        self.console.print(stats_table)
        self.console.print()
        
        # Resource Usage
        resource_stats = analysis["resource_usage"]
        resource_table = Table(title="Resource Usage")
        resource_table.add_column("Resource", style="cyan")
        resource_table.add_column("Average", style="white")
        resource_table.add_column("Peak", style="white")
        resource_table.add_column("Status", style="bold")
        
        # CPU status
        cpu_avg = resource_stats["cpu"]["avg_usage"]
        cpu_status = "[green]Good[/green]" if cpu_avg < 50 else "[yellow]Moderate[/yellow]" if cpu_avg < 80 else "[red]High[/red]"
        resource_table.add_row("CPU Usage", f"{cpu_avg:.1f}%", f"{resource_stats['cpu']['max_usage']:.1f}%", cpu_status)
        
        # Memory status
        mem_avg = resource_stats["memory"]["avg_usage"]
        mem_status = "[green]Good[/green]" if mem_avg < 50 else "[yellow]Moderate[/yellow]" if mem_avg < 80 else "[red]High[/red]"
        resource_table.add_row("Memory Usage", f"{mem_avg:.1f}%", f"{resource_stats['memory']['max_usage']:.1f}%", mem_status)
        
        self.console.print(resource_table)
        self.console.print()
        
        # Network I/O
        network_stats = analysis["network_io"]
        network_table = Table(title="Network I/O")
        network_table.add_column("Direction", style="cyan")
        network_table.add_column("Total", style="white")
        network_table.add_column("Average per Run", style="white")
        
        network_table.add_row("Bytes Sent", self._format_bytes(network_stats["total_bytes_sent"]), 
                             self._format_bytes(network_stats["avg_bytes_sent"]))
        network_table.add_row("Bytes Received", self._format_bytes(network_stats["total_bytes_recv"]),
                             self._format_bytes(network_stats["avg_bytes_recv"]))
        
        self.console.print(network_table)
        self.console.print()
        
        # Playbook Statistics
        playbook_stats = analysis["playbook_stats"]
        playbook_table = Table(title="Playbook Statistics")
        playbook_table.add_column("Metric", style="cyan")
        playbook_table.add_column("Average", style="white")
        
        playbook_table.add_row("Tasks per Run", f"{playbook_stats['avg_tasks']:.0f}")
        playbook_table.add_row("Hosts per Run", f"{playbook_stats['avg_hosts']:.0f}")
        playbook_table.add_row("Success Rate", f"{playbook_stats['avg_success_rate']:.1f}%")
        
        self.console.print(playbook_table)
        self.console.print()
        
        # Recommendations
        recommendations = analysis["recommendations"]
        rec_panel = Panel(
            "\n".join(f"• {rec}" for rec in recommendations),
            title="[bold blue]Performance Recommendations[/bold blue]",
            border_style="blue"
        )
        self.console.print(rec_panel)
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"
    
    def save_metrics(self, metrics_list: List[PerformanceMetrics], filename: str):
        """Save metrics to JSON file"""
        metrics_data = [asdict(metric) for metric in metrics_list]
        
        reports_dir = self.base_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        output_file = reports_dir / filename
        with open(output_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        self.console.print(f"[green]Metrics saved to: {output_file}[/green]")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Ansible Performance Monitor")
    parser.add_argument("--base-path", help="Base path for Ansible project")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Performance test command
    test_parser = subparsers.add_parser("test", help="Run performance test")
    test_parser.add_argument("playbook", help="Playbook to test")
    test_parser.add_argument("-i", "--inventory", default="production", help="Inventory to use")
    test_parser.add_argument("--iterations", type=int, default=1, help="Number of test iterations")
    test_parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    test_parser.add_argument("--save", help="Save metrics to JSON file")
    
    # Monitor command (for monitoring existing executions)
    monitor_parser = subparsers.add_parser("monitor", help="Monitor playbook execution")
    monitor_parser.add_argument("command", nargs="+", help="Ansible command to monitor")
    monitor_parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize monitor
    monitor = AnsiblePerformanceMonitor(args.base_path)
    
    try:
        if args.command == "test":
            monitor.console.print(f"[blue]Starting performance test for {args.playbook}...[/blue]")
            
            metrics_list = monitor.run_performance_test(
                playbook_name=args.playbook,
                inventory=args.inventory,
                iterations=args.iterations,
                sample_interval=args.interval
            )
            
            # Analyze results
            analysis = monitor.analyze_performance(metrics_list)
            
            # Display report
            monitor.display_performance_report(analysis, metrics_list)
            
            # Save metrics if requested
            if args.save:
                monitor.save_metrics(metrics_list, args.save)
        
        elif args.command == "monitor":
            monitor.console.print(f"[blue]Monitoring command: {' '.join(args.command)}[/blue]")
            
            metrics, stdout, stderr, return_code = monitor.monitor_playbook_execution(
                args.command, args.interval
            )
            
            # Display basic metrics
            monitor.console.print(f"\n[bold]Execution completed in {metrics.duration:.2f} seconds[/bold]")
            monitor.console.print(f"CPU Usage: {metrics.cpu_usage_avg:.1f}% (avg), {metrics.cpu_usage_max:.1f}% (peak)")
            monitor.console.print(f"Memory Usage: {metrics.memory_usage_avg:.1f}% (avg), {metrics.memory_usage_max:.1f}% (peak)")
            monitor.console.print(f"Tasks: {metrics.task_count}, Hosts: {metrics.host_count}")
            monitor.console.print(f"Success Rate: {metrics.success_rate:.1f}%")
            
            # Show command output if failed
            if return_code != 0:
                monitor.console.print(f"\n[red]Command failed with return code {return_code}[/red]")
                if stderr:
                    monitor.console.print(Panel(stderr, title="Error Output", border_style="red"))
            
            sys.exit(return_code)
    
    except Exception as e:
        monitor.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
