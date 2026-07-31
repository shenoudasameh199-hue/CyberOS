import platform
import psutil
from rich.console import Console
from rich.table import Table

console = Console()

def get_system_info():
    table = Table(title="💻 System Specifications", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Details", style="bold green")

    table.add_row("OS / Kernel", f"{platform.system()} {platform.release()}")
    table.add_row("Hostname", platform.node())
    table.add_row("Architecture", platform.machine())

    # CPU Usage with Fallback for Android restriction
    try:
        cpu = f"{psutil.cpu_percent(interval=1)}%"
    except Exception:
        cpu = "N/A (Android Restricted)"
    table.add_row("CPU Usage", cpu)

    # Memory Usage
    try:
        ram = psutil.virtual_memory()
        ram_info = f"{ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)"
    except Exception:
        ram_info = "N/A"
    table.add_row("RAM Usage", ram_info)

    # Disk Usage
    try:
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
    except Exception:
        disk_info = "N/A"
    table.add_row("Disk Usage", disk_info)

    console.print(table)

def get_running_processes():
    table = Table(title="⚙️ Top Processes", show_header=True, header_style="bold yellow")
    table.add_column("PID", style="cyan", justify="center")
    table.add_column("Name", style="bold white")
    table.add_column("CPU %", style="bold green", justify="center")
    table.add_column("RAM %", style="bold magenta", justify="center")

    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        sorted_procs = sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
        for p in sorted_procs:
            cpu = f"{p['cpu_percent']:.1f}%" if p['cpu_percent'] else "0.0%"
            mem = f"{p['memory_percent']:.1f}%" if p['memory_percent'] else "0.0%"
            table.add_row(str(p['pid']), str(p['name']), cpu, mem)
            
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error reading process table: {e}[/bold red]")

def get_disk_usage():
    table = Table(title="💾 Disk Partitions", show_header=True, header_style="bold blue")
    table.add_column("Mountpoint", style="bold cyan")
    table.add_column("Total", style="bold white", justify="center")
    table.add_column("Used", style="bold yellow", justify="center")
    table.add_column("Free", style="bold green", justify="center")
    table.add_column("Usage %", style="bold magenta", justify="center")

    try:
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                table.add_row(
                    part.mountpoint,
                    f"{usage.total // (1024**3)} GB",
                    f"{usage.used // (1024**3)} GB",
                    f"{usage.free // (1024**3)} GB",
                    f"{usage.percent}%"
                )
            except PermissionError:
                continue
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error fetching disk details: {e}[/bold red]")
