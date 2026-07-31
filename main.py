import os
import sys
import json
import logging
import zipfile
import argparse
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
        "version": "2.7",
        "developer": "Shenouda Sameh",
        "theme_color": "bright_blue",
        "auto_save_reports": True,
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

def export_report(fmt="html") -> None:
    rep_dir = CONFIG.get("reports_dir", "reports")
    os.makedirs(rep_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if fmt == "html":
        filename = os.path.join(rep_dir, f"report_{timestamp}.html")
        try:
            console.save_html(filename)
            console.print(f"\n[bold green]📄 تم حفظ تقرير HTML بنجاح في: {filename}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red]فشل حفظ التقرير: {e}[/bold red]")

def cli_quick_scan(target):
    console.print(Panel(f"[bold cyan]🔍 بدء الفحص السريع والكامل للهدف: {target}[/bold cyan]", border_style="green"))
    ip_lookup(target)
    whois_dns_lookup(target)
    port_scanner(target, 1, 100)
    export_report("html")

def display_header() -> None:
    theme = CONFIG.get("theme_color", "bright_blue")
    header_text = (
        f"[bold green]{CONFIG.get('app_name')} v{CONFIG.get('version')}[/bold green]\n"
        "[bold green]منصة الأمن السيبراني وفحص الشبكات الشاملة[/bold green]\n"
        f"[bold yellow]تطوير: {CONFIG.get('developer')}[/bold yellow]"
    )
    console.print(Panel(header_text, border_style=theme, expand=False))

def display_menu() -> None:
    theme = CONFIG.get("theme_color", "bright_blue")
    table = Table(title="[italic white]القائمة الرئيسية - CyberOS v2.7[/italic white]", show_header=True, header_style="bold magenta", border_style=theme)
    table.add_column("الرقم", style="bold cyan", justify="center")
    table.add_column("الأدوات والخصائص", style="bold green", justify="right")

    table.add_row("1", "💻 معلومات النظام والموارد (System Info)")
    table.add_row("2", "🌐 أدوات الشبكة الأساسية (IP / Ports / Ping)")
    table.add_row("3", "🔍 الاستكشاف المتقدم (Subdomains & DirBuster)")
    table.add_row("4", "🛰️ فحص المواقع والتقنيات (DNS / CMS / SSL)")
    table.add_row("5", "🔐 الخزنة المشفرة والتجزئة (Crypto & Hashes)")
    table.add_row("6", "🖼️ التحليل الجنائي والإخفاء (EXIF & Steganography)")
    table.add_row("7", "🔑 إدارة كشوف السر والتحليل (Passwords)")
    table.add_row("8", "⚡ مولد الحمولات والثغرات (Payload Generator)")
    table.add_row("9", "📁 إدارة الملفات والشجرة (File Manager)")
    table.add_row("10", "📱 صانع رموز الاستجابة السريعة (QR Code)")
    table.add_row("11", "📂 تصفح وإدارة التقارير السابقة (Reports Manager)")
    table.add_row("12", "📝 الملاحظات والنسخ الاحتياطي والثيمات (Config & Backup)")
    table.add_row("13", "📄 تصدير تقرير الجلسة (Export HTML / Text)")
    table.add_row("0", "خروج (Exit)")

    console.print(table)

def main() -> None:
    parser = argparse.ArgumentParser(description="CyberOS Terminal Tool")
    parser.add_argument("--scan", help="فحص سريع ومباشر لهدف معين وتصدير التقرير")
    args = parser.parse_args()

    if args.scan:
        cli_quick_scan(args.scan)
        sys.exit(0)

    while True:
        console.clear()
        display_header()
        display_menu()

        choice = Prompt.ask("\nاختر رقماً من القائمة", choices=[str(i) for i in range(14)])

        if choice == "1":
            console.clear()
            get_system_info()
            Prompt.ask("\nاضغط Enter للمتابعة...")
        elif choice == "2":
            console.clear()
            t = Prompt.ask("أدخل الهدف للفحص")
            port_scanner(t, 1, 500)
            Prompt.ask("\nاضغط Enter للمتابعة...")
        elif choice == "0":
            console.print("\n[bold red]إلى اللقاء![/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    main()
