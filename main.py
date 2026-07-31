import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import track

from modules.system import get_system_info, get_running_processes, get_disk_usage
from modules.network import ip_lookup, port_scanner, http_headers, ping_host
from modules.password import generate_password, analyze_password
from modules.files import show_tree, get_dir_size, search_files
from modules.hash import hash_string, hash_file
from modules.qr import generate_terminal_qr, save_qr_image
from modules.recon import subdomain_enum, dir_buster
from modules.crypto import encrypt_file, decrypt_file
from modules.payloads import generate_payloads
from modules.web_advanced import whois_dns_lookup, cms_tech_scanner, ssl_inspector
from modules.forensics import extract_exif, hide_text_in_file, extract_text_from_file

logging.basicConfig(
    filename="cyberos.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def load_config():
    default_cfg = {
        "app_name": "CyberOS Ultimate",
        "version": "3.5",
        "developer": "Shenouda Sameh",
        "theme_color": "cyan",
        "reports_dir": "reports"
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return {**default_cfg, **json.load(f)}
        except Exception as e:
            logging.error(f"Error loading config: {e}")
    return default_cfg

CONFIG = load_config()
console = Console(record=True)

def show_splash():
    console.clear()
    banner = r"""
   _____ ____  ______  ______ ____  ____  ____ 
  / ___// __ \/ __  / / ____// __ \/ ___// / / 
 / /__ / /_/ / /_/ / / /___ / /_/ /\__ \/_/ /  
 \___/ \__, /\____/  \____/ \____/____/ (_) /   
      /____/                             /___/   
    """
    console.print(f"[bold bright_cyan]{banner}[/bold bright_cyan]")
    console.print("[bold yellow]⚡ SYSTEM BOOT: CYBEROS CORE v3.5[/bold yellow]\n")
    for _ in track(range(10), description="[bold green]Loading Cyber Modules...[/bold green]"):
        time.sleep(0.02)
    console.clear()

def display_dashboard():
    try:
        load1, load5, load15 = os.getloadavg()
        cpu_str = f"{load1:.2f}"
    except Exception:
        cpu_str = "ACTIVE"

    status_text = (
        f"[bold green]STATUS:[/bold green] ONLINE  │  "
        f"[bold cyan]LOAD:[/bold cyan] {cpu_str}  │  "
        f"[bold magenta]VERSION:[/bold magenta] v{CONFIG.get('version')}  │  "
        f"[bold yellow]DEV:[/bold yellow] {CONFIG.get('developer')}"
    )
    console.print(Panel(status_text, title="[bold white]🛡️ CYBEROS DASHBOARD[/bold white]", border_style="bright_blue", expand=True))

def display_menu():
    table = Table(show_header=True, header_style="bold bright_magenta", border_style="bright_blue", expand=True)
    
    table.add_column("OPTION", style="bold bright_cyan", justify="center", width=8)
    table.add_column("MODULE NAME", style="bold green", width=30)
    table.add_column("DESCRIPTION", style="dim white")

    table.add_row("01", "System Intelligence", "Monitor CPU, Memory, and Disk Usage")
    table.add_row("02", "Network Scanner", "IP Lookup, Multi-Threaded Port Scanner, Ping")
    table.add_row("03", "Reconnaissance", "Subdomain Enumeration & Directory Buster")
    table.add_row("04", "Web Intelligence", "WHOIS, DNS Lookup, CMS & SSL Inspector")
    table.add_row("05", "Cryptography Vault", "File Encryption/Decryption & Hashing")
    table.add_row("06", "Digital Forensics", "EXIF Data Extraction & Steganography")
    table.add_row("07", "Password Manager", "Strong Password Generator & Security Analyzer")
    table.add_row("08", "Payload Generator", "Generate Reverse Shell Payloads")
    table.add_row("09", "File Manager", "Directory Tree Viewer & Storage Search")
    table.add_row("10", "QR Code Tools", "Generate & Save Custom Terminal QR Codes")
    table.add_row("11", "Reports Center", "View, Manage & Analyze Generated Reports")
    table.add_row("12", "System Settings", "Configure Themes & System Backups")
    table.add_row("13", "Export Report", "Export Current Session Report to HTML")
    table.add_row("00", "Exit System", "Safely Close CyberOS Session")

    console.print(table)

def export_report(fmt="html") -> None:
    rep_dir = CONFIG.get("reports_dir", "reports")
    os.makedirs(rep_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if fmt == "html":
        filename = os.path.join(rep_dir, f"report_{timestamp}.html")
        try:
            console.save_html(filename)
            console.print(f"\n[bold green]📄 Report saved successfully: {filename}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red]Report Export Failed: {e}[/bold red]")

def view_past_reports():
    rep_dir = CONFIG.get("reports_dir", "reports")
    if not os.path.exists(rep_dir) or not os.listdir(rep_dir):
        console.print("[yellow]⚠️ No saved reports found.[/yellow]")
        return

    reports = sorted(os.listdir(rep_dir), reverse=True)
    table = Table(title="📂 Saved Reports", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Filename", style="bold green")
    table.add_column("Size", style="bold yellow", justify="center")

    for idx, rep in enumerate(reports, 1):
        fp = os.path.join(rep_dir, rep)
        size = f"{os.path.getsize(fp) / 1024:.1f} KB"
        table.add_row(str(idx), rep, size)

    console.print(table)
    choice = Prompt.ask("\nSelect Report ID to read (0 to back)", default="0")
    if choice.isdigit() and 0 < int(choice) <= len(reports):
        selected_file = os.path.join(rep_dir, reports[int(choice)-1])
        console.clear()
        console.print(f"[bold cyan]📑 File Content: {reports[int(choice)-1]}[/bold cyan]\n")
        try:
            with open(selected_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                console.print(content[:3000] + ("\n... [Truncated due to file size]" if len(content) > 3000 else ""))
        except Exception as e:
            console.print(f"[bold red]❌ Read error: {e}[/bold red]")

def main():
    show_splash()
    while True:
        console.clear()
        display_dashboard()
        display_menu()

        choice = Prompt.ask("\n[bold bright_cyan]CyberOS[/bold bright_cyan] ❯", default="01")

        if choice in ["1", "01"]:
            console.clear()
            get_system_info()
            get_disk_usage()
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["2", "02"]:
            console.clear()
            t = Prompt.ask("Enter target host (e.g. example.com)")
            ip_lookup(t)
            port_scanner(t, 1, 100)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["3", "03"]:
            console.clear()
            t = Prompt.ask("Enter target domain for Subdomains")
            subdomain_enum(t)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["4", "04"]:
            console.clear()
            t = Prompt.ask("Enter URL/Domain for Web Intelligence")
            whois_dns_lookup(t)
            cms_tech_scanner(t)
            ssl_inspector(t)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["5", "05"]:
            console.clear()
            sub = Prompt.ask("1. Hash String\n2. Encrypt File\nSelect Option", choices=["1", "2"])
            if sub == "1":
                txt = Prompt.ask("Enter Text")
                hash_string(txt)
            else:
                fpath = Prompt.ask("Enter File Path")
                key = Prompt.ask("Enter Encryption Key")
                encrypt_file(fpath, key)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["6", "06"]:
            console.clear()
            sub = Prompt.ask("1. Extract Image EXIF\n2. Hide Text in File\nSelect Option", choices=["1", "2"])
            if sub == "1":
                img = Prompt.ask("Enter Image Path")
                extract_exif(img)
            else:
                fpath = Prompt.ask("Enter File Path")
                txt = Prompt.ask("Enter Hidden Text")
                hide_text_in_file(fpath, txt)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["7", "07"]:
            console.clear()
            sub = Prompt.ask("1. Generate Password\n2. Analyze Strength\nSelect Option", choices=["1", "2"])
            if sub == "1":
                length = int(Prompt.ask("Enter Length", default="16"))
                pwd = generate_password(length)
                console.print(f"\n[bold green]🔑 Password:[/bold green] [bold yellow]{pwd}[/bold yellow]")
            else:
                pwd = Prompt.ask("Enter Password to Test")
                analyze_password(pwd)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["8", "08"]:
            console.clear()
            ip = Prompt.ask("Enter LHOST (Your IP)")
            port = Prompt.ask("Enter LPORT", default="4444")
            generate_payloads(ip, port)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["9", "09"]:
            console.clear()
            path = Prompt.ask("Enter Path", default=".")
            show_tree(path)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice == "10":
            console.clear()
            data = Prompt.ask("Enter Text/URL for QR Code")
            generate_terminal_qr(data)
            if Prompt.ask("Save as image? (y/n)", choices=["y", "n"]) == "y":
                save_qr_image(data, "qrcode.png")
            Prompt.ask("\nPress Enter to return...")
            
        elif choice == "11":
            console.clear()
            view_past_reports()
            Prompt.ask("\nPress Enter to return...")
            
        elif choice == "12":
            console.clear()
            console.print("[bold cyan]⚙️ System Config:[/bold cyan]")
            console.print(CONFIG)
            Prompt.ask("\nPress Enter to return...")
            
        elif choice == "13":
            export_report("html")
            Prompt.ask("\nPress Enter to return...")
            
        elif choice in ["0", "00"]:
            console.print("\n[bold red]Exiting CyberOS. Goodbye![/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    main()
