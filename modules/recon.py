import json
import urllib.request
import urllib.error
from rich.console import Console
from rich.table import Table

console = Console()

def subdomain_enum(domain: str):
    console.print(f"\n[bold cyan]🔍 جاري فحص النطاقات الفرعية لـ: {domain}...[/bold cyan]")
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            subdomains = sorted(list(set([entry['name_value'] for entry in data])))
            
            table = Table(title=f"Subdomains found for {domain}", show_header=True, header_style="bold magenta")
            table.add_column("#", style="cyan", justify="center")
            table.add_column("Subdomain", style="bold green")
            
            for idx, sub in enumerate(subdomains[:30], 1):
                for s in sub.split('\n'):
                    table.add_row(str(idx), s)
            
            console.print(table)
            console.print(f"[bold green]✔ تم العثور على {len(subdomains)} نطاق فرعي![/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ خطأ أثناء فحص النطاقات: {e}[/bold red]")

def dir_buster(target_url: str):
    if not target_url.startswith("http"):
        target_url = "http://" + target_url
    target_url = target_url.rstrip("/")
    
    wordlist = [
        "/admin", "/login", "/dashboard", "/config.json", "/backup.zip",
        "/api", "/db.sql", "/.env", "/.git/HEAD", "/robots.txt", "/wp-admin",
        "/phpmyadmin", "/uploads", "/test", "/server-status"
    ]
    
    console.print(f"\n[bold cyan]🚀 جاري فحص مسارات الموقع: {target_url}...[/bold cyan]\n")
    table = Table(show_header=True, header_style="bold yellow")
    table.add_column("Path", style="bold white")
    table.add_column("Status Code", justify="center")
    
    for path in wordlist:
        url = target_url + path
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                code = resp.getcode()
                table.add_row(path, f"[bold green]{code} OK[/bold green]")
        except urllib.error.HTTPError as e:
            if e.code in [401, 403]:
                table.add_row(path, f"[bold yellow]{e.code} Forbidden[/bold yellow]")
            elif e.code != 404:
                table.add_row(path, f"[bold blue]{e.code}[/bold blue]")
        except Exception:
            pass
            
    console.print(table)
