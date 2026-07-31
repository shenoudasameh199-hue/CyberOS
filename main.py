import os
import sys
import json
import time
import logging
import zipfile
import argparse
import psutil
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import track
from rich.layout import Layout
from rich.live import Live

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
        "version": "3.0",
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

def show_splash():
    console.clear()
    banner = r"""
   ______ ____ ___  ____ _____ ____  ____  ____ 
  / ___/ / / // _ \/ __// ___// __ \/ __/ / / / 
 / /__/ /_/ // ___/ _/ / /__ / /_/ /\ \  /_/ /  
 \___/\__,_//_/  /___/ \___/ \____/___/  (_) /   
                                        /___/    
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[bold yellow]⚡ INITIALIZING CYBEROS CORE SYSTEM...[/bold yellow]\n")
    for _ in track(range(10), description="[bold green]Loading Modules...[/bold green]"):
        time.sleep(0.04)
    console.clear()

def display_dashboard():
    theme = CONFIG.get("theme_color", "bright_blue")
    
    # حساب الموارد
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    
    status_text = (
        f"[bold green]SYSTEM:[/bold green] ONLINE  |  "
        f"[bold cyan]CPU:[/bold cyan] {cpu_usage}%  |  "
        f"[bold yellow]RAM:[/bold yellow] {ram_usage}%  |  "
        f"[bold magenta]VER:[/bold magenta] v{CONFIG.get('version')}  |  "
        f"[bold red]DEV:[/bold red] {CONFIG.get('developer')}"
    )
    
    console.print(Panel(status_text, title="[bold white]🛡️ CyberOS Live Status[/bold white]", border_style=theme, expand=True))

def display_menu():
    theme = CONFIG.get("theme_color", "bright_blue")
    table = Table(show_header=True, header_style="bold magenta", border_style=theme, expand=True)
    
    table.add_column("ID", style="bold cyan", justify="center", width=6)
    table.add_column("الوحدة / Module", style="bold green")
    table.add_column("الوصف / Description", style="dim white")

    table.add_row("1", "💻 معلومات واستكشاف النظام", "مراقبة المعالج، الذاكرة، والتخزين")
    table.add_row("2", "🌐 أدوات الشبكة والمنافذ", "فحص IP، Port Scanner سريع، Ping")
    table.add_row("3", "🔍 الاستكشاف المتقدم (Recon)", "جمع Subdomains والمسارات المخفية")
    table.add_row("4", "🛰️ فحص المواقع (Web Intelligence)", "كشف التقنيات، DNS، شهادات SSL")
    table.add_row("5", "🔐 الخزنة والتشفير (Cryptography)", "تشفير الملفات والتجزئة Hashes")
    table.add_row("6", "🖼️ التحليل الجنائي (Forensics)", "استخراج EXIF والإخفاء داخل الملفات")
    table.add_row("7", "🔑 إدارة وتحليل كلمات السر", "توليد كشوف معقدة واختبار القوة")
    table.add_row("8", "⚡ مولد الحمولات (Payload Generator)", "إنشاء اتصال عكسي Reverse Shells")
    table.add_row("9", "📁 إدارة الملفات والشجرة", "عرض واستكشاف المجلدات والأحجام")
    table.add_row("10", "📱 رموز الاستجابة (QR Tools)", "توليد وحفظ رموز QR")
    table.add_row("11", "📂 مركز التقارير (Reports Center)", "عرض وقراءة وتقييم التقارير")
    table.add_row("12", "⚙️ الإعدادات والنسخ الاحتياطي", "تغيير الثيم، الملاحظات، والباك أب")
    table.add_row("13", "📄 تصدير التقرير الحالي", "حفظ الجلسة كـ HTML / Text")
    table.add_row("0", "❌ خروج (Exit)", "إنهاء الجلسة وحفظ البيانات")

    console.print(table)

def export_report(fmt="html") -> None:
    rep_dir = CONFIG.get("reports_dir", "reports")
    os.makedirs(rep_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if fmt == "html":
        filename = os.path.join(rep_dir, f"report_{timestamp}.html")
        try:
            console.save_html(filename)
            console.print(f"\n[bold green]📄 تم حفظ التقرير بنجاح: {filename}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red]فشل حفظ التقرير: {e}[/bold red]")

def main():
    show_splash()
    while True:
        console.clear()
        display_dashboard()
        display_menu()

        choice = Prompt.ask("\n[bold cyan]CyberOS[/bold cyan] > [bold yellow]اختر أمر من القائمة[/bold yellow]", choices=[str(i) for i in range(14)])

        if choice == "1":
            console.clear()
            get_system_info()
            Prompt.ask("\nاضغط Enter للمتابعة...")
        elif choice == "2":
            console.clear()
            t = Prompt.ask("أدخل الهدف للفحص")
            port_scanner(t, 1, 300)
            Prompt.ask("\nاضغط Enter للمتابعة...")
        elif choice == "11":
            console.clear()
            from main import view_past_reports
            view_past_reports()
            Prompt.ask("\nاضغط Enter للمتابعة...")
        elif choice == "0":
            console.print("\n[bold red]إلى اللقاء! تم إغلاق CyberOS بنجاح.[/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    main()
