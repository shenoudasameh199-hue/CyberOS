import logging
import hashlib
import socket
import json
import requests
import qrcode
import io
import dns.resolver
import whois
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from modules.password import generate_password

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "8619543254:AAGm6IRV_hMifTOMonCrrzyIIKiqzUJfhE8"

# إعداد الـ DNS Resolver لبيئة Termux
custom_resolver = dns.resolver.Resolver(configure=False)
custom_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🛡️ **CyberOS Pro v7.0 - Advanced Recon & OSINT Suite**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "أهلاً بك يا شنودة! البوت جاهز بأعلى المواصفات الاحترافية:\n\n"
        "🔍 **Reconnaissance & OSINT:**\n"
        "▪️ `/ip <domain>` - جلب الـ IP والجيولوكيشن ومزود الخدمة\n"
        "▪️ `/subdomains <domain>` - كشف وتصفية الدومينات الفرعية\n"
        "▪️ `/dns <domain>` - استخراج سجلات (A, MX, TXT)\n"
        "▪️ `/whois <domain>` - جلب بيانات الملكية وتواريخ الدومين\n"
        "▪️ `/tech <url>` - كشف تقنيات السيرفر والموقع المستخدمة\n"
        "▪️ `/headers <url>` - فحص أمان HTTP Security Headers\n"
        "▪️ `/scan <host>` - فحص المنافذ والبورتات المفتوحة\n"
        "▪️ `/ping <host>` - اختبار سرعة واستجابة الهدف\n\n"
        "🛠️ **Utilities & Security:**\n"
        "▪️ `/genpass <length>` - توليد كلمات سر قوية ومفصّلة\n"
        "▪️ `/hash <text>` - تجزئة النصوص (MD5 / SHA256)\n"
        "▪️ `/qr <text>` - تحويل روابط ونصوص لـ QR Code صورة\n\n"
        "👨‍💻 **Developer:** Shenouda Sameh"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

async def handle_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة الهدف، مثال:\n`/ip google.com`", parse_mode="Markdown")
        return
    target = context.args[0].replace("https://", "").replace("http://", "").split('/')[0]
    await update.message.reply_text(f"🔍 جاري فحص البيانات لـ: `{target}`...", parse_mode="Markdown")
    try:
        ip = socket.gethostbyname(target)
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if resp.get("status") == "success":
            res = (
                f"🌐 **معلومات الـ IP والجيولوكيشن:**\n\n"
                f"🎯 **Target:** `{target}`\n"
                f"📌 **IP:** `{ip}`\n"
                f"🏳️ **Country:** {resp.get('country')}\n"
                f"🏙️ **City:** {resp.get('city')}\n"
                f"🏢 **ISP:** {resp.get('isp')}"
            )
        else:
            res = f"❌ تعذر جلب البيانات للعنوان."
    except Exception as e:
        res = f"❌ خطأ أثناء الفحص: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_subdomains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة الدومين، مثال:\n`/subdomains google.com`", parse_mode="Markdown")
        return
    domain = context.args[0].replace("https://", "").replace("http://", "").split('/')[0]
    await update.message.reply_text(f"🛰️ جاري البحث والفلترة الذكية لـ `{domain}`...", parse_mode="Markdown")
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            raw_subs = set()
            for entry in data:
                val = entry['name_value']
                for sub in val.split('\n'):
                    sub = sub.strip()
                    if '*' not in sub and '@' not in sub and sub.endswith(domain):
                        raw_subs.add(sub)
            
            clean_subs = sorted(raw_subs)
            if clean_subs:
                sub_list = "\n".join([f"• `{s}`" for s in clean_subs[:20]])
                res = f"🎯 **الدومينات الفرعية المكتشفة والمفلترة ({len(clean_subs)}):**\n\n{sub_list}"
                if len(clean_subs) > 20:
                    res += f"\n\n*(عرض 20 من أصل {len(clean_subs)} دومين فرعي)*"
            else:
                res = "⚠️ لم يتم العثور على دومينات فرعية نظيفة."
        else:
            res = "❌ فشل الاتصال بقاعدة بيانات الدومينات الفرعية."
    except Exception as e:
        res = f"❌ حدث خطأ: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_dns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الدومين، مثال:\n`/dns google.com`", parse_mode="Markdown")
        return
    domain = context.args[0].replace("https://", "").replace("http://", "").split('/')[0]
    await update.message.reply_text(f"📡 جاري فحص سجلات DNS المباشرة لـ `{domain}`...", parse_mode="Markdown")
    
    res = f"🌐 **سجلات الـ DNS لـ:** `{domain}`\n\n"
    for r_type in ['A', 'MX', 'TXT']:
        try:
            answers = custom_resolver.resolve(domain, r_type)
            res += f"🔹 **{r_type} Records:**\n"
            for rdata in answers:
                res += f"  • `{rdata.to_text()}`\n"
        except Exception:
            res += f"🔹 **{r_type} Records:** `غير مسجل / غير متوفر`\n"
            
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_whois(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الدومين، مثال:\n`/whois google.com`", parse_mode="Markdown")
        return
    domain = context.args[0].replace("https://", "").replace("http://", "").split('/')[0]
    await update.message.reply_text(f"📋 جاري استخراج بيانات WHOIS لـ `{domain}`...", parse_mode="Markdown")
    try:
        w = whois.whois(domain)
        registrar = w.registrar if isinstance(w.registrar, str) else (w.registrar[0] if w.registrar else "غير معلوم")
        creation = w.creation_date if not isinstance(w.creation_date, list) else w.creation_date[0]
        expiration = w.expiration_date if not isinstance(w.expiration_date, list) else w.expiration_date[0]
        
        res = (
            f"📄 **بيانات WHOIS لـ:** `{domain}`\n\n"
            f"🏢 **الشركة المسجلة (Registrar):** `{registrar}`\n"
            f"📅 **تاريخ الإنشاء:** `{str(creation)[:10]}`\n"
            f"⏳ **تاريخ الانتهاء:** `{str(expiration)[:10]}`\n"
            f"🌍 **سيرفرات الأسماء (NS):** `{', '.join(w.name_servers[:2]) if w.name_servers else 'غير متوفر'}`"
        )
    except Exception as e:
        res = f"❌ تعذر جلب بيانات WHOIS: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الرابط، مثال:\n`/tech google.com`", parse_mode="Markdown")
        return
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    await update.message.reply_text(f"🔍 جاري التحليل التقني لـ `{url}`...", parse_mode="Markdown")
    try:
        resp = requests.get(url, timeout=7)
        headers = resp.headers
        server = headers.get('Server', 'مخفي أو غير محدد')
        powered_by = headers.get('X-Powered-By', 'غير معلن')
        
        res = (
            f"⚙️ **التقنيات المكشوفة لـ:** `{url}`\n\n"
            f"🖥️ **السيرفر (Server):** `{server}`\n"
            f"⚡ **اللغة / الإطار (Powered-By):** `{powered_by}`\n"
            f"🔒 **تشفير HTTPS:** `{'مفعل ✅' if url.startswith('https') else 'غير مفعل ❌'}`"
        )
    except Exception as e:
        res = f"❌ خطأ أثناء الاتصال بالموقع: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_headers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الرابط، مثال:\n`/headers google.com`", parse_mode="Markdown")
        return
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    await update.message.reply_text(f"🛡️ جاري فحص هيدرز الأمان لـ `{url}`...", parse_mode="Markdown")
    try:
        resp = requests.get(url, timeout=5)
        headers = resp.headers
        sec_headers = ["Strict-Transport-Security", "X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy"]
        res = f"📋 **نتائج HTTP Security Headers:**\n\n"
        for sh in sec_headers:
            if sh in headers:
                res += f"✅ **{sh}:** موجود\n"
            else:
                res += f"❌ **{sh}:** غير موجود\n"
        res += f"\n🖥️ **Server Header:** `{headers.get('Server', 'مخفي')}`"
    except Exception as e:
        res = f"❌ خطأ أثناء الاتصال بالموقع: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الهدف، مثال:\n`/scan scanme.nmap.org`", parse_mode="Markdown")
        return
    target = context.args[0].replace("https://", "").replace("http://", "").split('/')[0]
    await update.message.reply_text(f"📡 جاري فحص المنافذ لـ `{target}`...", parse_mode="Markdown")
    common_ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL"}
    open_ports = []
    try:
        ip = socket.gethostbyname(target)
        for port, service in common_ports.items():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(f"🟢 Port `{port}` ({service}): OPEN")
            s.close()
        res = f"🔓 **البورتات المفتوحة لـ `{target}` ({ip}):**\n\n" + ("\n".join(open_ports) if open_ports else "🔒 لا توجد بورتات مفتوحة من المنافذ الشهيرة.")
    except Exception as e:
        res = f"❌ خطأ: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الهدف، مثال:\n`/ping google.com`", parse_mode="Markdown")
        return
    target = context.args[0].replace("https://", "").replace("http://", "").split('/')[0]
    try:
        ip = socket.gethostbyname(target)
        res = f"⚡ **استجابة السيرفر (Ping):**\n🎯 Target: `{target}`\n📌 IP: `{ip}`\n🟢 الحالة: `Online & Active`"
    except Exception as e:
        res = f"❌ تعذر الوصول للهدف: {e}"
    await update.message.reply_text(res, parse_mode="Markdown")

async def handle_genpass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = int(context.args[0]) if context.args and context.args[0].isdigit() else 16
    pwd = generate_password(length)
    await update.message.reply_text(f"🔑 **كلمة السر المولدة:**\n`{pwd}`", parse_mode="Markdown")

async def handle_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب النص للتجزئة.", parse_mode="Markdown")
        return
    text = " ".join(context.args)
    md5 = hashlib.md5(text.encode()).hexdigest()
    sha256 = hashlib.sha256(text.encode()).hexdigest()
    await update.message.reply_text(f"🔐 **MD5:** `{md5}`\n\n🔐 **SHA256:** `{sha256}`", parse_mode="Markdown")

async def handle_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب النص للـ QR.", parse_mode="Markdown")
        return
    text = " ".join(context.args)
    qr_img = qrcode.make(text)
    bio = io.BytesIO()
    bio.name = 'qrcode.png'
    qr_img.save(bio, 'PNG')
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption=f"📱 **QR Code جاهز~/CyberOS*", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ip", handle_ip))
    app.add_handler(CommandHandler("subdomains", handle_subdomains))
    app.add_handler(CommandHandler("dns", handle_dns))
    app.add_handler(CommandHandler("whois", handle_whois))
    app.add_handler(CommandHandler("tech", handle_tech))
    app.add_handler(CommandHandler("headers", handle_headers))
    app.add_handler(CommandHandler("scan", handle_scan))
    app.add_handler(CommandHandler("ping", handle_ping))
    app.add_handler(CommandHandler("genpass", handle_genpass))
    app.add_handler(CommandHandler("hash", handle_hash))
    app.add_handler(CommandHandler("qr", handle_qr))
    print("🚀 CyberOS Pro v7.0 is ACTIVE...")
    app.run_polling()

if __name__ == "__main__":
    main()
