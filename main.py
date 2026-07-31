import os
import sys
import json
import zipfile
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from modules.system import get_system_info, get_running_processes, get_disk_usage
from modules.network import ip_lookup, port_scanner, http_headers, ping_host
from modules.password import generate_password, analyze_password
from modules.files import show_tree, get_dir_size, search_files
from modules.hash import hash_string, hash_file
from modules.qr import generate_terminal_qr, save_qr_image
from modules.recon import subdomain_enum, dir_buster
from modules.crypto import encrypt_file, decrypt_file
from modules.payloads import generate_payloads

def load_config():
    default_cfg = {
        "app_name": "CyberOS Ultimate",
        "version": "2.0",
        "developer": "Shenouda Sameh",
        "theme_color": "bright_blue",
        "auto_save_reports": True,
        "reports_dir": "reports"
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return {**default_cfg, **json.load(f)}
        except Exception:
            pass
    return default_cfg

CONFIG = load_config()
console = Console(record=True)

def export_report() -> None:
    rep_dir = CONFIG.get("reports_dir", "reports")
    os.makedirs(rep_dir, exist_ok=True)
    filename = os.path.join(rep_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    try:
        console.save_html(filename)
        console.print(f"\n[bold green]📄 Session report successfully saved to: {filename}[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]Failed to save report: {e}[/bold red]")

def display_header() -> None:
    theme = CONFIG.get("theme_color", "bright_blue")
    header_text = (
        f"[bold green]{CONFIG.get('app_name')} v{CONFIG.get('version')}[/bold green]\n"
        "[bold green]Ultimate Cyber Recon & Security Toolkit[/bold green]\n"
        f"[bold yellow]Developed by {CONFIG.get('developer')}[/bold yellow]"
    )
    console.print(Panel(header_text, border_style=theme, expand=False))

def display_menu() -> None:
    table = Table(title="[italic white]CyberOS v2.0 Main Dashboard[/italic white]", show_header=True, header_style="bold magenta", border_style="white")
    table.add_column("No", style="bold cyan", justify="center")
    table.add_column("Category & Tools", style="bold green")

    table.add_row("1", "System Information & Resources")
    table.add_row("2", "Basic Network Tools (IP/Ports/Ping/Headers)")
    table.add_row("3", "🔍 Advanced Recon (Subdomains & DirBuster)")
    table.add_row("4", "🔐 Crypto Vault (File Encrypt/Decrypt & Hashes)")
    table.add_row("5", "Password Manager & Analyzer")
    table.add_row("6", "⚡ Reverse Shell & Payload Generator")
    table.add_row("7", "File Manager & Directory Tree")
    table.add_row("8", "QR Code Generator")
    table.add_row("9", "Quick Notes & Backup Manager")
    table.add_row("10", "About & Config")
    table.add_row("11", "📄 Export Session Report (HTML)")
    table.add_row("0", "Exit")

    console.print(table)

def handle_notes() -> None:
    notes_file = "notes.json"
    notes = []
    if os.path.exists(notes_file):
        try:
            with open(notes_file, "r", encoding="utf-8") as f:
                notes = json.load(f)
        except Exception:
            notes = []

    console.clear()
    console.print(Panel("[bold cyan]📝 Quick System Notes[/bold cyan]", border_style="cyan"))
    console.print("1. Add new note\n2. View all notes\n3. Clear all notes\n0. Back")
    
    sub = Prompt.ask("Select option", choices=["0", "1", "2", "3"])
    if sub == "1":
        note = Prompt.ask("Enter note text")
        notes.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": note})
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=4)
        console.print("[bold green]✔ Note saved successfully![/bold green]")
    elif sub == "2":
        if not notes:
            console.print("[yellow]No notes found.[/yellow]")
        else:
            for idx, n in enumerate(notes, 1):
                console.print(f"[bold yellow]{idx}.[/bold yellow] [{n['date']}] {n['text']}")
    elif sub == "3":
        if os.path.exists(notes_file):
            os.remove(notes_file)
            console.print("[bold red]All notes have been cleared.[/bold red]")

def handle_backup() -> None:
    console.clear()
    console.print(Panel("[bold cyan]📦 Backup Manager[/bold cyan]", border_style="cyan"))
    target = Prompt.ask("Enter target directory path to compress", default=".")
    if not os.path.exists(target):
        console.print("[bold red]❌ Target path does not exist.[/bold red]")
        return

    os.makedirs("backups", exist_ok=True)
    out_name = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    try:
        with zipfile.ZipFile(out_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(target):
                if "backups" in root or "reports" in root:
                    continue
                for f in files:
                    fp = os.path.join(root, f)
                    zipf.write(fp, os.relpath(fp, target))
        console.print(f"[bold green]✔ Backup successfully created at: {out_name}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Backup error: {e}[/bold red]")

def main() -> None:
    while True:
        console.clear()
        display_header()
        display_menu()

        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])

        if choice == "1":
            console.clear()
            console.print("[bold cyan]1. General System Info\n2. Running Processes\n3. Disk & Storage Usage[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2", "3"])
            if sub == "1": get_system_info()
            elif sub == "2": get_running_processes()
            elif sub == "3": get_disk_usage()
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "2":
            console.clear()
            console.print("[bold cyan]1. IP Lookup\n2. Port Scanner\n3. HTTP Headers\n4. Ping Host[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2", "3", "4"])
            if sub == "1":
                t = Prompt.ask("Enter IP or Domain")
                ip_lookup(t)
            elif sub == "2":
                t = Prompt.ask("Enter Target Host")
                sp = int(Prompt.ask("Start Port", default="1"))
                ep = int(Prompt.ask("End Port", default="100"))
                port_scanner(t, sp, ep)
            elif sub == "3":
                u = Prompt.ask("Enter Target URL")
                http_headers(u)
            elif sub == "4":
                h = Prompt.ask("Enter Host")
                ping_host(h)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "3":
            console.clear()
            console.print("[bold cyan]1. Subdomain Enumerator\n2. Directory Buster[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2"])
            if sub == "1":
                dom = Prompt.ask("Enter Domain (e.g. example.com)")
                subdomain_enum(dom)
            elif sub == "2":
                url = Prompt.ask("Enter Target URL (e.g. http://example.com)")
                dir_buster(url)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "4":
            console.clear()
            console.print("[bold cyan]1. Encrypt File with Password\n2. Decrypt File\n3. Hash String\n4. Hash File[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2", "3", "4"])
            if sub == "1":
                fp = Prompt.ask("Enter file path to encrypt")
                pwd = Prompt.ask("Set Encryption Password", password=True)
                encrypt_file(fp, pwd)
            elif sub == "2":
                fp = Prompt.ask("Enter encrypted file path (.enc)")
                pwd = Prompt.ask("Enter Password", password=True)
                decrypt_file(fp, pwd)
            elif sub == "3":
                txt = Prompt.ask("Enter Text")
                hash_string(txt)
            elif sub == "4":
                fp = Prompt.ask("Enter File Path")
                hash_file(fp)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "5":
            console.clear()
            console.print("[bold cyan]1. Generate Password\n2. Analyze Password Strength[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2"])
            if sub == "1":
                l = int(Prompt.ask("Length", default="16"))
                generate_password(l)
            elif sub == "2":
                p = Prompt.ask("Enter Password to Analyze")
                analyze_password(p)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "6":
            console.clear()
            console.print("[bold cyan]⚡ Reverse Shell Payload Generator[/bold cyan]")
            lhost = Prompt.ask("Enter your IP (LHOST)")
            lport = Prompt.ask("Enter Port (LPORT)", default="4444")
            generate_payloads(lhost, lport)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "7":
            console.clear()
            console.print("[bold cyan]1. Directory Tree View\n2. Directory Size\n3. Search Files[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2", "3"])
            if sub == "1":
                path = Prompt.ask("Path", default=".")
                show_tree(path)
            elif sub == "2":
                path = Prompt.ask("Path", default=".")
                get_dir_size(path)
            elif sub == "3":
                d = Prompt.ask("Search Directory", default=".")
                k = Prompt.ask("Search Keyword")
                search_files(d, k)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "8":
            console.clear()
            console.print("[bold cyan]1. Terminal QR Code\n2. Save QR PNG Image[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2"])
            if sub == "1":
                d = Prompt.ask("Enter URL or Text")
                generate_terminal_qr(d)
            elif sub == "2":
                d = Prompt.ask("Enter URL or Text")
                fn = Prompt.ask("Filename", default="qrcode.png")
                save_qr_image(d, fn)
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "9":
            console.clear()
            console.print("[bold cyan]1. Quick Notes\n2. Backup Manager[/bold cyan]")
            sub = Prompt.ask("Select option", choices=["1", "2"])
            if sub == "1": handle_notes()
            elif sub == "2": handle_backup()
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "10":
            console.clear()
            console.print(Panel(f"[bold cyan]{CONFIG.get('app_name')} v{CONFIG.get('version')}[/bold cyan]\n• Developer: {CONFIG.get('developer')}\n• All-in-one Termux Security Platform", title="About"))
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "11":
            export_report()
            Prompt.ask("\nPress Enter to continue...")

        elif choice == "0":
            if CONFIG.get("auto_save_reports", True):
                export_report()
            console.print("\n[bold red]Goodbye![/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if CONFIG.get("auto_save_reports", True):
            export_report()
        console.print("\n[bold red]Terminated by user. Goodbye![/bold red]")
        sys.exit(0)
