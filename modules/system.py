import platform
import psutil
from rich.console import Console
from rich.table import Table

console = Console()

def get_cpu_percent():
    try:
        return f"{psutil.cpu_percent(interval=1)}%"
    except (PermissionError, Exception):
        return "N/A (Android Restricted)"

def get_system_info() -> None:
    uname = platform.uname()
    
    try:
        mem = psutil.virtual_memory()
        ram_info = f"{mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)"
    except Exception:
        ram_info = "N/A"

    try:
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
    except Exception:
        disk_info = "N/A"

    table = Table(title="💻 معلومات النظام الأساسية", style="cyan")
    table.add_column("المعيار", style="bold yellow")
    table.add_column("التفاصيل", style="bold white")

    table.add_row("نظام التشغيل", f"{uname.system} {uname.release}")
    table.add_row("اسم الجهاز", uname.node)
    table.add_row("المعالج (Arch)", uname.machine)
    table.add_row("استهلاك المعالج", get_cpu_percent())
    table.add_row("الذاكرة (RAM)", ram_info)
    table.add_row("المساحة (Disk)", disk_info)

    console.print(table)

def get_running_processes(limit: int = 10) -> None:
    table = Table(title=f"⚙️ أعلى {limit} عمليات استهلاكاً للذاكرة", style="green")
    table.add_column("PID", style="yellow")
    table.add_column("اسم العملية", style="bold white")
    table.add_column("استهلاك RAM (%)", style="magenta")

    procs = []
    try:
        for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                pass
    except PermissionError:
        console.print("[bold yellow]⚠️ عرض العمليات يتطلب صلاحيات Root على Android.[/bold yellow]")
        return

    if not procs:
        console.print("[bold yellow]⚠️ لا توجد صلاحيات لعرض العمليات الحالية.[/bold yellow]")
        return

    sorted_procs = sorted(procs, key=lambda x: (x.get('memory_percent') or 0), reverse=True)[:limit]
    for p in sorted_procs:
        mem = f"{p['memory_percent']:.2f}%" if p.get('memory_percent') is not None else "0.0%"
        table.add_row(str(p['pid']), str(p['name']), mem)

    console.print(table)

def get_disk_usage() -> None:
    table = Table(title="📁 أقسام التخزين المتاحة", style="magenta")
    table.add_column("المسار", style="yellow")
    table.add_column("نظام الملفات", style="cyan")
    table.add_column("المساحة الكلية", style="white")
    table.add_column("المستغل (%)", style="red")

    try:
        partitions = psutil.disk_partitions()
        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                table.add_row(
                    part.mountpoint,
                    part.fstype,
                    f"{usage.total // (1024**3)} GB",
                    f"{usage.percent}%"
                )
            except Exception:
                continue
    except Exception:
        pass

    # Backup attempt for root storage if partition enumeration is restricted
    try:
        usage = psutil.disk_usage('/')
        table.add_row("/", "Internal", f"{usage.total // (1024**3)} GB", f"{usage.percent}%")
    except Exception:
        pass

    console.print(table)
