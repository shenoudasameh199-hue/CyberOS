import platform
import psutil
from rich.console import Console
from rich.table import Table

console = Console()

def get_system_info():
    table = Table(title="💻 معلومات النظام والعتاد", show_header=True, header_style="bold magenta")
    table.add_column("المعيار / العنصر", style="bold cyan", justify="right")
    table.add_column("التفاصيل", style="bold green", justify="right")

    table.add_row("نظام التشغيل", f"{platform.system()} {platform.release()}")
    table.add_row("اسم الجهاز (Hostname)", platform.node())
    table.add_row("معمارية المعالج", platform.machine())

    try:
        cpu = f"{psutil.cpu_percent(interval=1)}%"
    except Exception:
        cpu = "غير متاح (قيود أندرويد)"
    table.add_row("استهلاك المعالج (CPU)", cpu)

    try:
        ram = psutil.virtual_memory()
        ram_info = f"{ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)"
    except Exception:
        ram_info = "غير متاح"
    table.add_row("الذاكرة العشوائية (RAM)", ram_info)

    try:
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
    except Exception:
        disk_info = "غير متاح"
    table.add_row("المساحة التخزينية (Disk)", disk_info)

    console.print(table)

def get_running_processes():
    table = Table(title="⚙️ العمليات الشغالة حالياً", show_header=True, header_style="bold yellow")
    table.add_column("معرف العملية PID", style="cyan", justify="center")
    table.add_column("اسم التطبيق", style="bold white", justify="right")
    table.add_column("استهلاك CPU", style="bold green", justify="center")
    table.add_column("استهلاك RAM", style="bold magenta", justify="center")

    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        sorted_procs = sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
        for p in sorted_procs:
            cpu = f"{p['cpu_percent']:.1f}%" if p['cpu_percent'] else "0.0%"
            mem = f"{p['memory_percent']:.1f}%" if p['memory_percent'] else "0.0%"
            table.add_row(str(p['pid']), str(p['name']), cpu, mem)
            
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]خطأ في جلب قائمة العمليات: {e}[/bold red]")

def get_disk_usage():
    table = Table(title="💾 أقسام التخزين", show_header=True, header_style="bold blue")
    table.add_column("مسار القسم", style="bold cyan", justify="right")
    table.add_column("الإجمالي", style="bold white", justify="center")
    table.add_column("المستخدم", style="bold yellow", justify="center")
    table.add_column("المتبقي", style="bold green", justify="center")
    table.add_column("نسبة الاستهلاك", style="bold magenta", justify="center")

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
        console.print(f"[bold red]خطأ في جلب تفاصيل التخزين: {e}[/bold red]")
