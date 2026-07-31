import urllib.request
import json
import ssl
import socket
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

console = Console()

def whois_dns_lookup(domain: str):
    console.print(f"[bold cyan]🔍 فحص سجلات DNS و Whois للهدف: {domain}[/bold cyan]")
    table = Table(title="سجلات DNS الأساسية", show_header=True, header_style="bold magenta")
    table.add_column("نوع السجل", style="bold yellow")
    table.add_column("النتيجة / العنوان", style="bold green")

    # A Record
    try:
        ips = socket.gethostbyname_ex(domain)[2]
        for ip in ips:
            table.add_row("A (IPv4)", ip)
    except Exception as e:
        table.add_row("A Record", f"فشل الجلب: {e}")

    # Basic API for MX & TXT via Google DNS API
    for qtype in ['MX', 'TXT', 'NS']:
        try:
            url = f"https://dns.google/resolve?name={domain}&type={qtype}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if 'Answer' in data:
                    for ans in data['Answer']:
                        table.add_row(qtype, ans.get('data', ''))
                else:
                    table.add_row(qtype, "لا توجد سجلات معلنة")
        except Exception:
            table.add_row(qtype, "خطأ أثناء الفحص")

    console.print(table)

def cms_tech_scanner(url: str):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    console.print(f"[bold cyan]⚙️ جاري تحليل التقنيات المستخدمة في: {url}[/bold cyan]")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=8, context=context) as resp:
            headers = dict(resp.headers)
            body = resp.read().decode('utf-8', errors='ignore')

        table = Table(title="التقنيات المكتشفة", show_header=True, header_style="bold blue")
        table.add_column("العنصر / التقنية", style="bold cyan")
        table.add_column("التفاصيل", style="bold green")

        # Web Server
        server = headers.get('Server', 'غير معلوم')
        table.add_row("خادم الويب (Server)", server)

        # Powered By
        powered = headers.get('X-Powered-By', 'غير معلن')
        table.add_row("لغة/إطار العمل", powered)

        # CMS Checks
        cms = "غير معروف / مخصص"
        if "wp-content" in body or "wp-includes" in body:
            cms = "WordPress 📝"
        elif "Joomla" in body:
            cms = "Joomla 🧩"
        elif "Drupal" in body:
            cms = "Drupal 💧"
        elif "Shopify" in body:
            cms = "Shopify 🛍️"
        table.add_row("نظام إدارة المحتوى (CMS)", cms)

        # JS Libraries
        libs = []
        if "jquery" in body.lower(): libs.append("jQuery")
        if "react" in body.lower(): libs.append("React")
        if "vue" in body.lower(): libs.append("Vue.js")
        if "bootstrap" in body.lower(): libs.append("Bootstrap")
        table.add_row("مكتبات الواجهة (JS/CSS)", ", ".join(libs) if libs else "لم تكتشف مكتبات شهيرة")

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ فشل الاتصال بالموقع: {e}[/bold red]")

def ssl_inspector(domain: str):
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    console.print(f"[bold cyan]🔒 فحص شهادة الأمان SSL/TLS لـ: {domain}[/bold cyan]")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                table = Table(title="تفاصيل شهادة الأمان", show_header=True, header_style="bold green")
                table.add_column("الخاصية", style="bold yellow")
                table.add_column("القيمة", style="bold white")

                issuer = dict(x[0] for x in cert.get('issuer', []))
                subject = dict(x[0] for x in cert.get('subject', []))

                table.add_row("الجهة المصدرة (Issuer)", issuer.get('organizationName', 'N/A'))
                table.add_row("صادرة لـ (Subject)", subject.get('commonName', domain))
                table.add_row("تاريخ البدء", cert.get('notBefore', 'N/A'))
                table.add_row("تاريخ الانتهاء", cert.get('notAfter', 'N/A'))
                
                console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ خطأ في فحص الشهادة: {e}[/bold red]")
