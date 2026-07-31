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

# تحميل الإعدادات
def load_config():
    default_cfg = {
        "app_name": "CyberOS Pro",
        "version": "1.1",
        "developer": "Shenouda Sameh",
        "theme_color": "cyan",
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

# تفعيل خاصية التسجيل للتقارير
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
    theme = CONFIG.get("theme_color", "cyan")
    header_text = (
        f"[bold green]{CONFIG.get('app_name', 'CyberOS')} v{CONFIG.get('version', '1.1')}[/bold green]\n"
        "[bold green]Professional Terminal Toolkit[/bold green]\n"
        f"[bold yellow]Developed by {CONFIG.get('developer', 'Shenouda Sameh')}[/bold yellow]"
    )
    console.print(Panel(header_text, border_style=theme, expand=False))

def display_menu() -> None:
    table = Table(title="[italic white]Main Menu[/italic white]", show_header=True, header_style="bold magenta", border_style="white")
    table.add_column("No", style="bold cyan", justify="center")
    table.add_column("Tool", style="bold green")

    table.add_row("1", "System Information")
    table.add_row("2", "Network Tools")
    table.add_row("3", "Password Generator")
    table.add_row("4", "File Manager")
    table.add_row("5", "Hash Calculator")
    table.add_row("6", "QR Code Generator")
    table.add_row("7", "Notes")
    table.add_row("8", "Backup")
    table.add_row("9", "About & Config")
    table.add_row("10", "Export Session Report (HTML)")
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
    console.print(Panel("[bold cyan]📝 ملاحظات حافظة النظام السريعة[/bold cyan]", border_style="cyan"))
    console.print("1. إضافة ملاحظة جديدة\n2. عرض جميع الملاحظات\n3. مسح الملاحظات\n0. عودة")
    
    sub = Prompt.ask("اختر الخيار", choices=["0", "1", "2", "3"])
    if sub == "1":
        note = Prompt.ask("أدخل الملاحظة")
        notes.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": note})
        with open(notes_file, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=4)
        console.print("[bold green]✔ تم حفظ الملاحظة![/bold green]")
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
    console.print(Panel("[bold cyan]📦 أداة عمل نسخ احتياطي (Backup Manager)[/bold cyan]", border_style="cyan"))
    target = Prompt.ask("أدخل مسار المجلد المراد ضغطه", default=".")
    if not os.path.exists(target):
        console.print("[bold red]❌ المسار المرفق غير موجود.[/bold red]")
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
        console.print(f"[bold red]خطأ أثناء عمل النسخة الاحتياطية: {e}[/bold red]")

def show_about() -> None:
    about_text = f"""
    [bold cyan]{CONFIG.get('app_name')} - Professional Terminal Toolkit[/bold cyan]
    
    • [bold yellow]المطور الأساسي:[/bold yellow] {CONFIG.get('developer')}
    • [bold yellow]الإصدار الحالي:[/bold yellow] {CONFIG.get('version')}
    • [bold yellow]مجلس التقارير:[/bold yellow] {CONFIG.get('reports_dir')}
    • [bold yellow]البيئة المستهدفة:[/bold yellow] Termux / Linux
    """
    console.print(Panel(about_text, title="عن الأداة والإعدادات", border_style="green"))

def main() -> None:
    while True:
        console.clear()
        display_header()
        display_menu()

        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

        if choice == "1":
            console.clear()
            console.print("[bold cyan]1. معلومات النظام الشاملة\n2. العمليات الأكثر استهلاكاً\n3. أقسام التخزين[/bold cyan]")
            sub = Prompt.ask("اختر", choices=["1", "2", "3"])
            if sub == "1": get_system_info()
            elif sub == "2": get_running_processes()
            elif sub == "3": get_disk_usage()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "2":
            console.clear()
            console.print("[bold cyan]1. فحص IP\n2. فحص المنافذ Port Scanner\n3. ترويسات HTTP\n4. اختبار Ping[/bold cyan]")
            sub = Prompt.ask("اختر", choices=["1", "2", "3", "4"])
            if sub == "1":
                t = Prompt.ask("أدخل IP أو Domain")
                ip_lookup(t)
            elif sub == "2":
                t = Prompt.ask("أدخل الهدف")
                sp = int(Prompt.ask("منفذ البداية", default="1"))
                ep = int(Prompt.ask("منفذ النهاية", default="100"))
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
            console.print("[bold cyan]1. توليد كلمة مرور\n2. تحليل قوة كلمة مرور[/bold cyan]")
            sub = Prompt.ask("اختر", choices=["1", "2"])
            if sub == "1":
                l = int(Prompt.ask("الطول", default="16"))
                generate_password(l)
            elif sub == "2":
                p = Prompt.ask("أدخل كلمة المرور للفحص")
                analyze_password(p)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "4":
            console.clear()
            console.print("[bold cyan]1. عرض شجرة المجلد\n2. حساب حجم المجلد\n3. البحث عن ملف[/bold cyan]")
            sub = Prompt.ask("اختر", choices=["1", "2", "3"])
            if sub == "1":
                path = Prompt.ask("المسار", default=".")
                show_tree(path)
            elif sub == "2":
                path = Prompt.ask("المسار", default=".")
                get_dir_size(path)
            elif sub == "3":
                d = Prompt.ask("مجلد البحث", default=".")
                k = Prompt.ask("الكلمة المفتاحية")
                search_files(d, k)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "5":
            console.clear()
            console.print("[bold cyan]1. تجزئة نص\n2. تجزئة ملف[/bold cyan]")
            sub = Prompt.ask("اختر", choices=["1", "2"])
            if sub == "1":
                txt = Prompt.ask("أدخل النص")
                hash_string(txt)
            elif sub == "2":
                fp = Prompt.ask("أدخل مسار الملف")
                hash_file(fp)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "6":
            console.clear()
            console.print("[bold cyan]1. طباعة QR في الترمكس\n2. حفظ QR كصورة PNG[/bold cyan]")
            sub = Prompt.ask("اختر", choices=["1", "2"])
            if sub == "1":
                d = Prompt.ask("أدخل الرابط أو النص")
                generate_terminal_qr(d)
            elif sub == "2":
                d = Prompt.ask("أدخل الرابط أو النص")
                fn = Prompt.ask("اسم الملف", default="qrcode.png")
                save_qr_image(d, fn)
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "7":
            handle_notes()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "8":
            handle_backup()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "9":
            console.clear()
            show_about()
            Prompt.ask("\nاضغط Enter للمتابعة...")

        elif choice == "10":
            export_report()
            Prompt.ask("\nاضغط Enter للمتابعة...")

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
        console.print("\n[bold red]تم التوقف بواسطة المستخدم. Goodbye![/bold red]")
        sys.exit(0)
