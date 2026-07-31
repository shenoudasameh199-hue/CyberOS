import socket
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
import requests

console = Console()

def ip_lookup(target):
    try:
        ip = socket.gethostbyname(target)
        console.print(f"\n[bold green]✔ الهدف:[/bold green] {target}")
        console.print(f"[bold cyan]📌 عنوان IP:[/bold cyan] {ip}")
    except Exception as e:
        console.print(f"[bold red]❌ فشل تحديد IP: {e}[/bold red]")

def check_port(target, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((target, port))
        sock.close()
        if result == 0:
            return port
    except Exception:
        pass
    return None

def port_scanner(target, start_port=1, end_port=1024, max_threads=50):
    console.print(f"\n[bold yellow]⚡ بدء الفحص السريع للمنافذ على {target} ({start_port}-{end_port}) باستخدام {max_threads} خيط...[/bold yellow]")
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(check_port, target, port) for port in range(start_port, end_port + 1)]
        for future in futures:
            res = future.result()
            if res:
                open_ports.append(res)
    
    if open_ports:
        table = Table(title=f"المنافذ المفتوحة - {target}", show_header=True)
        table.add_column("المنفذ (Port)", style="cyan", justify="center")
        table.add_column("الحالة (Status)", style="green", justify="center")
        for p in open_ports:
            table.add_row(str(p), "Open")
        console.print(table)
    else:
        console.print("[bold red]لا توجد منافذ مفتوحة في النطاق المحدد.[/bold red]")

def http_headers(url):
    if not url.startswith("http"):
        url = "http://" + url
    try:
        res = requests.get(url, timeout=5)
        table = Table(title=f"HTTP Headers - {url}", show_header=True)
        table.add_column("Header", style="cyan")
        table.add_column("Value", style="yellow")
        for k, v in res.headers.items():
            table.add_row(k, v)
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ فشل جلب الترويسات: {e}[/bold red]")

def ping_host(host):
    import os
    console.print(f"[bold yellow]📡 جاري اختبار الاتصال مع {host}...[/bold yellow]")
    os.system(f"ping -c 4 {host}")
