import socket
import concurrent.futures
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def ip_lookup(target: str) -> None:
    console.print(f"\n[bold cyan]🌐 جاري جلب بيانات IP لـ: {target}[/bold cyan]")
    try:
        res = requests.get(f"https://ipapi.co/{target}/json/", headers={"User-Agent": "CyberOS/1.0"}, timeout=5).json()
        table = Table(title=f"بيانات IP: {target}", style="cyan")
        table.add_column("الخاصية", style="magenta")
        table.add_column("القيمة", style="white")

        for k in ["ip", "city", "region", "country_name", "org", "asn", "timezone"]:
            table.add_row(k.capitalize(), str(res.get(k, "N/A")))

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]حدث خطأ أثناء جلب البيانات: {e}[/bold red]")

def port_scan_worker(ip: str, port: int, timeout: float = 1.0) -> int | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                return port
    except Exception:
        pass
    return None

def port_scanner(target: str, start_port: int = 1, end_port: int = 100) -> None:
    console.print(f"\n[bold cyan]🔍 فحص المنافذ لـ {target} (من {start_port} إلى {end_port})[/bold cyan]")
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        console.print("[bold red]❌ فشل حل اسم المضيف DNS[/bold red]")
        return

    open_ports = []
    ports = range(start_port, end_port + 1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task(description="جاري المسح...", total=len(ports))
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = {executor.submit(port_scan_worker, target_ip, p): p for p in ports}
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    open_ports.append(res)
                progress.advance(task)

    if open_ports:
        table = Table(title=f"المنافذ المفتوحة على {target}", style="green")
        table.add_column("Port", style="yellow")
        table.add_column("Status", style="bold green")
        table.add_column("Service", style="cyan")
        for p in sorted(open_ports):
            try:
                service = socket.getservbyport(p)
            except Exception:
                service = "Unknown"
            table.add_row(str(p), "OPEN", service)
        console.print(table)
    else:
        console.print("[yellow]لم يتم العثور على أي منافذ مفتوحة في هذا النطاق.[/yellow]")

def http_headers(url: str) -> None:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    console.print(f"\n[bold cyan]🌐 جاري جلب HTTP Headers لـ: {url}[/bold cyan]")
    try:
        r = requests.get(url, timeout=5)
        table = Table(title=f"HTTP Headers (Status: {r.status_code})", style="magenta")
        table.add_column("Header", style="yellow")
        table.add_column("Value", style="white")

        for k, v in list(r.headers.items())[:15]:
            table.add_row(k, v)
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]فشل الاتصال: {e}[/bold red]")

def ping_host(host: str) -> None:
    console.print(f"\n[bold cyan]📡 جاري اختبار الاتصال (Ping) بـ {host}...[/bold cyan]")
    try:
        target_ip = socket.gethostbyname(host)
        console.print(f"[bold green]✔ الهدف متصل وصحيح! IP: {target_ip}[/bold green]")
    except socket.gaierror:
        console.print(f"[bold red]❌ تتعذر الوصول إلى المضيف {host}[/bold red]")
