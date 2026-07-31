import os
import sys
import json
import zipfile
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display

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

def ar(text: str) -> str:
    """دالة لمعالجة النص العربي ليعرض بشكل صحيح ومترابط في الترمكس"""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except Exception:
        return str(text)

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
        console.print(f"\n[bold green]📄 {ar('تم حفظ تقرير الجلسة بنجاح في:')} {filename}[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]{ar('فشل حفظ التقرير:')} {e}[/bold red]")

def display_header() -> None:
    theme = CONFIG.get("theme_color", "bright_blue")
    header_text = (
        f"[bold green]{CONFIG.get('app_name')} v{CONFIG.get('version')}[/bold green]\n"
        f"[bold green]{ar('منصة الاستطلاع والأمن السيبراني المتكاملة')}[/bold green]\n"
        f"[bold yellow]{ar('تطوير:')} {CONFIG.get('developer')}[/bold yellow]"
    )
    console.print(Panel(header_text, border_style=theme, expand=False))

def display_menu() -> None:
    table = Table(title=f"[italic white]{ar('لوحة التحكم الرئيسية CyberOS v2.0')}[/italic white]", show_header=True, header_style="bold magenta", border_style="white")
    table.add_column(ar("م"), style="bold cyan", justify="center")
    table.add_column(ar("الأقسام والأدوات المتاحة"), style="bold green")

    table.add_row("1", ar("معلومات النظام والموارد"))
    table.add_row("2", ar("أدوات الشبكة (IP / المنافذ / Ping / الترويسات)"))
    table.add_row("3", ar("🔍 الاستطلاع المتقدم (النطاقات الفرعية والمسارات)"))
    table.add_row("4", ar("🔐 الخزنة المشفرة (تشفير الملفات والتجزئة)"))
    table.add_row("5", ar("مدير ومحلل كلمات المرور"))
    table.add_row("6", ar("⚡ مولد الاتصالات العكسية (Reverse Shells)"))
    table.add_row("7", ar("مدير الملفات وشجرة المجلدات"))
    table.add_row("8", ar("مولد أكواد QR Code"))
    table.add_row("9", ar("الملاحظات السريعة والنسخ الاحتياطي"))
    table.add_row("10", ar("حول الأداة والإعدادات"))
    table.add_row("11", ar("📄 تصدير تقرير الجلسة (HTML)"))
    table.add_row("0", ar("خروج"))

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
    console.print(Panel(f"[bold cyan]📝 {ar('ملاحظات النظام السريعة')}[/bold cyan]", border_style="cyan"))
    console.print(f"1. {ar('إضافة ملاحظة جديدة')}\n2. {ar('عرض جميع الملاحظات')}\n3. {ar('مسح الملاحظات')}\n0. {ar('عودة')}")
    
    sub = Prompt.ask(ar("اختر الخيار"), choices=["0", "1", "2", "3"])
    if sub == "1":
        note = Prompt.ask(ar("أدخل نص الملاحظة"))
        notes.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": note})
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=4)
        console.print(f"[bold green]✔ {ar('تم حفظ الملاحظة بنجاح!')}[/bold green]")
    elif sub == "2":
        if not notes:
            console.print(f"[yellow]{ar('لا توجد ملاحظات محفوظة.')}[/yellow]")
        else:
            for idx, n in enumerate(notes, 1):
                console.print(f"[bold yellow]{idx}.[/bold yellow] [{n['date']}] {n['text']}")
    elif sub == "3":
        if os.path.exists(notes_file):
            os.remove(notes_file)
            console.print(f"[bold red]{ar('تم مسح جميع الملاحظات.')}[/bold red]")

def handle_backup() -> None:
    console.clear()
    console.print(Panel(f"[bold cyan]📦 {ar('مدير النسخ الاحتياطي')}[/bold cyan]", border_style="cyan"))
    target = Prompt.ask(ar("أدخل مسار المجلد المراد ضغطه"), default=".")
    if not os.path.exists(target):
        console.print(f"[bold red]❌ {ar('المسار المحدد غير موجود.')}[/bold red]")
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
        console.print(f"[bold green]✔ {ar('تم إنشاء النسخة الاحتياطية في:')} {out_name}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]{ar('خطأ أثناء الضغط:')} {e}[/bold red]")

def main() -> None:
    while True:
        console.clear()
        display_header()
        display_menu()

        choice = Prompt.ask(f"\n[bold yellow]{ar('اختر رقماً من القائمة')}[/bold yellow]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])

        if choice == "1":
            console.clear()
            console.print(f"[bold cyan]1. {ar('معلومات النظام العامة')}\n2. {ar('العمليات الأكثر استهلاكاً')}\n3. {ar('استهلاك التخزين والقرص')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2", "3"])
            if sub == "1": get_system_info()
            elif sub == "2": get_running_processes()
            elif sub == "3": get_disk_usage()
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "2":
            console.clear()
            console.print(f"[bold cyan]1. {ar('فحص IP')}\n2. {ar('فحص المنافذ Port Scanner')}\n3. {ar('ترويسات HTTP')}\n4. {ar('اختبار Ping')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2", "3", "4"])
            if sub == "1":
                t = Prompt.ask(ar("أدخل IP أو Domain"))
                ip_lookup(t)
            elif sub == "2":
                t = Prompt.ask(ar("أدخل الهدف"))
                sp = int(Prompt.ask(ar("منفذ البداية"), default="1"))
                ep = int(Prompt.ask(ar("منفذ النهاية"), default="100"))
                port_scanner(t, sp, ep)
            elif sub == "3":
                u = Prompt.ask(ar("أدخل رابط الموقع"))
                http_headers(u)
            elif sub == "4":
                h = Prompt.ask(ar("أدخل المضيف"))
                ping_host(h)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "3":
            console.clear()
            console.print(f"[bold cyan]1. {ar('فحص النطاقات الفرعية (Subdomains)')}\n2. {ar('فحص المسارات المخفية (DirBuster)')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2"])
            if sub == "1":
                dom = Prompt.ask(ar("أدخل الدومين (مثال: example.com)"))
                subdomain_enum(dom)
            elif sub == "2":
                url = Prompt.ask(ar("أدخل رابط الموقع (مثال: http://example.com)"))
                dir_buster(url)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "4":
            console.clear()
            console.print(f"[bold cyan]1. {ar('تشفير ملف بكلمة سر')}\n2. {ar('فك تشفير ملف')}\n3. {ar('تجزئة نص (Hash String)')}\n4. {ar('تجزئة ملف (Hash File)')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2", "3", "4"])
            if sub == "1":
                fp = Prompt.ask(ar("مسار الملف المراد تشفيره"))
                pwd = Prompt.ask(ar("كلمة سر التشفير"), password=True)
                encrypt_file(fp, pwd)
            elif sub == "2":
                fp = Prompt.ask(ar("مسار الملف المشفر (.enc)"))
                pwd = Prompt.ask(ar("كلمة سر فك التشفير"), password=True)
                decrypt_file(fp, pwd)
            elif sub == "3":
                txt = Prompt.ask(ar("أدخل النص"))
                hash_string(txt)
            elif sub == "4":
                fp = Prompt.ask(ar("أدخل مسار الملف"))
                hash_file(fp)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "5":
            console.clear()
            console.print(f"[bold cyan]1. {ar('توليد كلمة مرور')}\n2. {ar('تحليل قوة كلمة المرور')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2"])
            if sub == "1":
                l = int(Prompt.ask(ar("الطول"), default="16"))
                generate_password(l)
            elif sub == "2":
                p = Prompt.ask(ar("أدخل كلمة المرور للفحص"))
                analyze_password(p)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "6":
            console.clear()
            console.print(f"[bold cyan]⚡ {ar('مولد الاتصالات العكسية (Payload Generator)')}[/bold cyan]")
            lhost = Prompt.ask(ar("أدخل IP الخاص بك (LHOST)"))
            lport = Prompt.ask(ar("أدخل المنفذ (LPORT)"), default="4444")
            generate_payloads(lhost, lport)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "7":
            console.clear()
            console.print(f"[bold cyan]1. {ar('عرض شجرة المجلدات')}\n2. {ar('حساب حجم المجلد')}\n3. {ar('البحث عن ملفات')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2", "3"])
            if sub == "1":
                path = Prompt.ask(ar("المسار"), default=".")
                show_tree(path)
            elif sub == "2":
                path = Prompt.ask(ar("المسار"), default=".")
                get_dir_size(path)
            elif sub == "3":
                d = Prompt.ask(ar("مجلد البحث"), default=".")
                k = Prompt.ask(ar("الكلمة المفتاحية"))
                search_files(d, k)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "8":
            console.clear()
            console.print(f"[bold cyan]1. {ar('عرض QR في الترمكس')}\n2. {ar('حفظ QR كصورة PNG')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2"])
            if sub == "1":
                d = Prompt.ask(ar("أدخل الرابط أو النص"))
                generate_terminal_qr(d)
            elif sub == "2":
                d = Prompt.ask(ar("أدخل الرابط أو النص"))
                fn = Prompt.ask(ar("اسم الملف"), default="qrcode.png")
                save_qr_image(d, fn)
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "9":
            console.clear()
            console.print(f"[bold cyan]1. {ar('الملاحظات السريعة')}\n2. {ar('مدير النسخ الاحتياطي')}[/bold cyan]")
            sub = Prompt.ask(ar("اختر"), choices=["1", "2"])
            if sub == "1": handle_notes()
            elif sub == "2": handle_backup()
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "10":
            console.clear()
            console.print(Panel(f"[bold cyan]{CONFIG.get('app_name')} v{CONFIG.get('version')}[/bold cyan]\n• {ar('المطور:')} {CONFIG.get('developer')}\n• {ar('منصة فحص أمنية شاملة للترمكس')}", title=ar("حول الأداة")))
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "11":
            export_report()
            Prompt.ask(f"\n{ar('اضغط Enter للمتابعة...')}")

        elif choice == "0":
            if CONFIG.get("auto_save_reports", True):
                export_report()
            console.print(f"\n[bold red]{ar('تم الخروج. إلى اللقاء!')}[/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if CONFIG.get("auto_save_reports", True):
            export_report()
        console.print(f"\n[bold red]{ar('تم الإيقاف بواسطة المستخدم. إلى اللقاء!')}[/bold red]")
        sys.exit(0)
