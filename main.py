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
        time.sleep(0.02)
    console.clear()

def display_dashboard():
    theme = CONFIG.get("theme_color", "bright_blue")
    try:
        load1, load5, load15 = os.getloadavg()
        cpu_str = f"{load1:.2f}"
    except Exception:
        cpu_str = "N/A"

    status_text = (
        f"[bold green]SYSTEM:[/bold green] ONLINE  |  "
        f"[bold cyan]LOAD AVG:[/bold cyan] {cpu_str}  |  "
        f"[bold magenta]VER:[/bold magenta] v{CONFIG.get('version')}  |  "
        f"[bold red]DEV:[/bold red] {CONFIG.get('developer')}"
    )
    console.print(Panel(status_text, title="[bold white]🛡️ CyberOS Live Dashboard[/bold white]", border_style=theme, expand=True))

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

def view_past_reports():
    rep_dir = CONFIG.get("reports_dir", "reports")
    if not os.path.exists(rep_dir) or not os.listdir(rep_dir):
        console.print("[yellow]⚠️ لا توجد تقارير محفوظة حالياً.[/yellow]")
        return

    reports = sorted(os.listdir(rep_dir), reverse=True)
    table = Table(title="📂 التقارير المحفوظة سابقةً", show_header=True, header_style="bold magenta")
    table.add_column("الرقم", style="cyan", justify="center")
    table.add_column("اسم الملف", style="bold green")
    table.add_column("الحجم", style="bold yellow", justify="center")

    for idx, rep in enumerate(reports, 1):
        fp = os.path.join(rep_dir, rep)
        size = f"{os.path.getsize(fp) / 1024:.1f} KB"
        table.add_row(str(idx), rep, size)

    console.print(table)
    choice = Prompt.ask("\nاختر رقم الملف لعرضه (أو 0 للرجوع)", default="0")
    if choice.isdigit() and 0 < int(choice) <= len(reports):
        selected_file = os.path.join(rep_dir, reports[int(choice)-1])
        console.clear()
        console.print(f"[bold cyan]📑 قراءة الملف: {reports[int(choice)-1]}[/bold cyan]\n")
        try:
            with open(selected_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                console.print(content[:3000] + ("\n... [تم إيقاف العرض لكبر الحجم]" if len(content) > 3000 else ""))
        except Exception as e:
            console.print(f"[bold red]❌ فشل قراءة الملف: {e}[/bold red]")

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
            get_disk_usage()
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "2":
            console.clear()
            t = Prompt.ask("أدخل الهدف للفحص (مثال: example.com)")
            ip_lookup(t)
            port_scanner(t, 1, 100)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "3":
            console.clear()
            t = Prompt.ask("أدخل الهدف لاستكشاف النطاقات الفرعية (Domain)")
            subdomain_enum(t)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "4":
            console.clear()
            t = Prompt.ask("أدخل الرابط أو الدومين للتحليل (Web Intelligence)")
            whois_dns_lookup(t)
            cms_tech_scanner(t)
            ssl_inspector(t)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "5":
            console.clear()
            sub = Prompt.ask("1. تجزئة نص (Hash String)\n2. تشفير ملف (Encrypt File)\nاختر أمر", choices=["1", "2"])
            if sub == "1":
                txt = Prompt.ask("أدخل النص")
                hash_string(txt)
            else:
                fpath = Prompt.ask("أدخل مسار الملف")
                key = Prompt.ask("أدخل مفتاح التشفير")
                encrypt_file(fpath, key)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "6":
            console.clear()
            sub = Prompt.ask("1. استخراج EXIF من صورة\n2. إخفاء نص في ملف\nاختر أمر", choices=["1", "2"])
            if sub == "1":
                img = Prompt.ask("أدخل مسار الصورة")
                extract_exif(img)
            else:
                fpath = Prompt.ask("أدخل مسار الملف")
                txt = Prompt.ask("أدخل النص المخفي")
                hide_text_in_file(fpath, txt)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "7":
            console.clear()
            sub = Prompt.ask("1. توليد كلمة سر معقدة\n2. اختبار قوة كلمة سر\nاختر أمر", choices=["1", "2"])
            if sub == "1":
                length = int(Prompt.ask("أدخل طول كلمة السر", default="16"))
                pwd = generate_password(length)
                console.print(f"\n[bold green]🔑 كلمة السر المنشأة:[/bold green] [bold yellow]{pwd}[/bold yellow]")
            else:
                pwd = Prompt.ask("أدخل كلمة السر للاختبار")
                analyze_password(pwd)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "8":
            console.clear()
            ip = Prompt.ask("أدخل الـ LHOST (IP الخاص بك)")
            port = Prompt.ask("أدخل الـ LPORT", default="4444")
            generate_payloads(ip, port)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "9":
            console.clear()
            path = Prompt.ask("أدخل المسار للعرص", default=".")
            show_tree(path)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "10":
            console.clear()
            data = Prompt.ask("أدخل النص أو الرابط لتحويله لـ QR Code")
            generate_terminal_qr(data)
            if Prompt.ask("هل تريد حفظه كصورة؟ (y/n)", choices=["y", "n"]) == "y":
                save_qr_image(data, "qrcode.png")
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "11":
            console.clear()
            view_past_reports()
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "12":
            console.clear()
            console.print("[bold cyan]⚙️ الإعدادات الحالية:[/bold cyan]")
            console.print(CONFIG)
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "13":
            export_report("html")
            Prompt.ask("\nاضغط Enter للمتابعة...")
            
        elif choice == "0":
            console.print("\n[bold red]إلى اللقاء! تم إغلاق CyberOS بنجاح.[/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    main()
