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
from modules.web_advanced import whois_dns_lookup, cms_tech_scanner, ssl_inspector
from modules.forensics import extract_exif, hide_text_in_file, extract_text_from_file

def load_config():
    default_cfg = {
        "app_name": "CyberOS Ultimate",
        "version": "2.5",
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
        console.print(f"\n[bold green]📄 تم حفظ تقرير الجلسة بنجاح في: {filename}[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]فشل حفظ التقرير: {e}[/bold red]")

def display_header() -> None:
    theme = CONFIG.get("theme_color", "bright_blue")
    header_text = (
        f"[bold green]{CONFIG.get('app_name')} v{CONFIG.get('version')}[/bold green]\n"
        "[bold green]منصة الأمن السيبراني وفحص الشبكات وتحليل البيانات الشاملة[/bold green]\n"
        f"[bold yellow]تطوير: {CONFIG.get('developer')}[/bold yellow]"
    )
    console.print(Panel(header_text, border_style=theme, expand=False))

def display_menu() -> None:
    theme = CONFIG.get("theme_color", "bright_blue")
    table = Table(title="[italic white]القائمة الرئيسية - CyberOS v2.5[/italic white]", show_header=True, header_style="bold magenta", border_style=theme)
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
    table.add_row("11", "📝 الملاحظات والنسخ الاحتياطي والثيمات (Config & Backup)")
    table.add_row("12", "📄 تصدير تقرير الجلسة (Export HTML)")
    table.add_row("0", "خروج (Exit)")

    console.print(table)

def handle_settings() -> None:
    console.clear()
    console.print(Panel("[bold cyan]⚙️ الإعدادات وتغيير الثيم[/bold cyan]", border_style="cyan"))
    console.print("1. Matrix Green 🟢\n2. Cyberpunk Purple 🟣\n3. Hacker Red 🔴\n4. Blue Classic 🔵\n0. رجوع")
    sub = Prompt.ask("اختر ثيماً", choices=["0", "1", "2", "3", "4"])
    colors = {"1": "green", "2": "magenta", "3": "red", "4": "bright_blue"}
    if sub in colors:
        CONFIG["theme_color"] = colors[sub]
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, indent=4)
        console.print("[bold green]✔ تم تحديث المظهر بنجاح![/bold green]")

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
    console.print(Panel("[bold cyan]📝 دفتر الملاحظات السريع[/bold cyan]", border_style="cyan"))
    console.print("1. إضافة ملاحظة جديدة\n2. عرض جميع الملاحظات\n3. مسح كافة الملاحظات\n0. رجوع")
    
    sub = Prompt.ask("اختر خياراً", choices=["0", "1", "2", "3"])
    if sub == "1":
        note = Prompt.ask("اكتب الملاحظة")
        notes.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": note})
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=4, ensure_ascii=False)
        console.print("[bold green]✔ تم حفظ الملاحظة بنجاح![/bold green]")
    elif sub == "2":
        if not notes:
            console.print("[yellow]لا توجد ملاحظات محفوظة.[/yellow]")
        else:
            for idx, n in enumerate(notes, 1):
                console.print(f"[bold yellow]{idx}.[/bold yellow] [{n['date']}] {n['text']}")
    elif sub == "3":
        if os.path.exists(notes_file):
            os.remove(notes_file)
            console.print("[bold red]تم مسح جميع الملاحظات.[/bold red]")

def handle_backup() -> None:
    console.clear()
    console.print(Panel("[bold cyan]📦 مدير النسخ الاحتياطي[/bold cyan]", border_style="cyan"))
    target = Prompt.ask("أدخل مسار المجلد المراد ضغطه", default=".")
    if not os.path.exists(target):
        console.print("[bold red]❌ المسار غير موجود.[/bold red]")
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
        console.print(f"[bold green]✔ تم إنشاء النسخة الاحتياطية بنجاح في: {out_name}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]خطأ أثناء النسخ الاحتياطي: {e}[/bold red]")

def main() -> None:
    while True:
        console.clear()
        display_header()
        display_menu()

        choice = Prompt.ask("\nاختر رقماً من القائمة", choices=[str(i) for i in range(13)])

        if choice == "1":
            console.clear()
            console.print("[bold cyan]1. معلومات النظام العامة\n2. العمليات الشغالة\n3. استهلاك المساحة والتخزين[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3"])
            if sub == "1": get_system_info()
            elif sub == "2": get_running_processes()
            elif sub == "3": get_disk_usage()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "2":
            console.clear()
            console.print("[bold cyan]1. فحص IP\n2. فحص المنافذ (Port Scanner)\n3. ترويسات المواقع (HTTP Headers)\n4. اختبار اتصال (Ping Host)[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3", "4"])
            if sub == "1":
                t = Prompt.ask("أدخل IP أو النطاق")
                ip_lookup(t)
            elif sub == "2":
                t = Prompt.ask("أدخل الهدف")
                sp = int(Prompt.ask("من منفذ", default="1"))
                ep = int(Prompt.ask("إلى منفذ", default="100"))
                port_scanner(t, sp, ep)
            elif sub == "3":
                u = Prompt.ask("أدخل رابط الموقع")
                http_headers(u)
            elif sub == "4":
                h = Prompt.ask("أدخل المضيف")
                ping_host(h)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "3":
            console.clear()
            console.print("[bold cyan]1. استخراج النطاقات الفرعية (Subdomains)\n2. فحص المسارات المخفية (DirBuster)[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2"])
            if sub == "1":
                dom = Prompt.ask("أدخل النطاق (مثال: example.com)")
                subdomain_enum(dom)
            elif sub == "2":
                url = Prompt.ask("أدخل الرابط (مثال: http://example.com)")
                dir_buster(url)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "4":
            console.clear()
            console.print("[bold cyan]1. فحص Whois & DNS\n2. كشف التقنيات و CMS\n3. فحص شهادة SSL/TLS[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3"])
            if sub == "1":
                d = Prompt.ask("أدخل النطاق (مثال: google.com)")
                whois_dns_lookup(d)
            elif sub == "2":
                u = Prompt.ask("أدخل رابط الموقع")
                cms_tech_scanner(u)
            elif sub == "3":
                d = Prompt.ask("أدخل النطاق")
                ssl_inspector(d)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "5":
            console.clear()
            console.print("[bold cyan]1. تشفير ملف بكلمة سر\n2. فك تشفير ملف\n3. تجزئة نص (Hash String)\n4. تجزئة ملف (Hash File)[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3", "4"])
            if sub == "1":
                fp = Prompt.ask("أدخل مسار الملف لتشفيره")
                pwd = Prompt.ask("كلمة سر التشفير", password=True)
                encrypt_file(fp, pwd)
            elif sub == "2":
                fp = Prompt.ask("أدخل مسار الملف المشفر (.enc)")
                pwd = Prompt.ask("كلمة السر", password=True)
                decrypt_file(fp, pwd)
            elif sub == "3":
                txt = Prompt.ask("أدخل النص")
                hash_string(txt)
            elif sub == "4":
                fp = Prompt.ask("أدخل مسار الملف")
                hash_file(fp)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "6":
            console.clear()
            console.print("[bold cyan]1. استخراج بيانات EXIF من الصور\n2. إخفاء نص داخل ملف\n3. استخراج نص مخفي من ملف[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3"])
            if sub == "1":
                p = Prompt.ask("أدخل مسار الصورة")
                extract_exif(p)
            elif sub == "2":
                p = Prompt.ask("أدخل مسار الملف الأصلي")
                txt = Prompt.ask("أدخل النص السرّي المراد إخفاؤه")
                out = Prompt.ask("أدخل مسار الملف الناتج", default="secret_out.jpg")
                hide_text_in_file(p, txt, out)
            elif sub == "3":
                p = Prompt.ask("أدخل مسار الملف المدمج")
                extract_text_from_file(p)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "7":
            console.clear()
            console.print("[bold cyan]1. توليد كلمة سر معقدة\n2. تحليل قوة كلمة السر[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2"])
            if sub == "1":
                l = int(Prompt.ask("الطول", default="16"))
                generate_password(l)
            elif sub == "2":
                p = Prompt.ask("أدخل كلمة السر لتحليلها")
                analyze_password(p)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "8":
            console.clear()
            console.print("[bold cyan]⚡ مولد الاتصال العكسي (Reverse Shell Generator)[/bold cyan]")
            lhost = Prompt.ask("أدخل عنوان IP الخاص بك (LHOST)")
            lport = Prompt.ask("أدخل المنفذ (LPORT)", default="4444")
            generate_payloads(lhost, lport)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "9":
            console.clear()
            console.print("[bold cyan]1. عرض شجرة المجلدات\n2. حساب حجم المجلد\n3. البحث عن ملفات[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3"])
            if sub == "1":
                path = Prompt.ask("المسار", default=".")
                show_tree(path)
            elif sub == "2":
                path = Prompt.ask("المسار", default=".")
                get_dir_size(path)
            elif sub == "3":
                d = Prompt.ask("مجلد البحث", default=".")
                k = Prompt.ask("كلمة البحث")
                search_files(d, k)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "10":
            console.clear()
            console.print("[bold cyan]1. توليد QR في الطرفية\n2. حفظ QR كصورة PNG[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2"])
            if sub == "1":
                d = Prompt.ask("أدخل النص أو الرابط")
                generate_terminal_qr(d)
            elif sub == "2":
                d = Prompt.ask("أدخل النص أو الرابط")
                fn = Prompt.ask("اسم الملف", default="qrcode.png")
                save_qr_image(d, fn)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "11":
            console.clear()
            console.print("[bold cyan]1. الملاحظات السريعة\n2. إدارة النسخ الاحتياطي\n3. تغيير ثيم ومظهر الأداة[/bold cyan]")
            sub = Prompt.ask("اختر خياراً", choices=["1", "2", "3"])
            if sub == "1": handle_notes()
            elif sub == "2": handle_backup()
            elif sub == "3": handle_settings()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "12":
            export_report()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "0":
            if CONFIG.get("auto_save_reports", True):
                export_report()
            console.print("\n[bold red]إلى اللقاء![/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if CONFIG.get("auto_save_reports", True):
            export_report()
        console.print("\n[bold red]تم الإنهاء بواسطة المستخدم. إلى اللقاء![/bold red]")
        sys.exit(0)
