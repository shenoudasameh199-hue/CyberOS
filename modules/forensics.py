import os
from PIL import Image
from PIL.ExifTags import TAGS
from rich.console import Console
from rich.table import Table

console = Console()

def extract_exif(image_path: str):
    if not os.path.exists(image_path):
        console.print(f"[bold red]❌ الملف غير موجود: {image_path}[/bold red]")
        return

    try:
        image = Image.open(image_path)
        exif_data = image._getexif()

        if not exif_data:
            console.print("[yellow]⚠️ لا توجد بيانات وصفيّة (EXIF Data) خفية في هذه الصورة.[/yellow]")
            return

        table = Table(title=f"📷 البيانات الخفية للصورة: {os.path.basename(image_path)}", show_header=True, header_style="bold magenta")
        table.add_column("الخاصية (EXIF Tag)", style="bold cyan")
        table.add_column("القيمة (Value)", style="bold green")

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except Exception:
                    value = "<Binary Data>"
            table.add_row(str(tag_name), str(value)[:80])

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ خطأ أثناء تحليل الصورة: {e}[/bold red]")

def hide_text_in_file(file_path: str, secret_text: str, output_path: str):
    """إخفاء نص في نهاية ملف بدون إتلافه"""
    if not os.path.exists(file_path):
        console.print(f"[bold red]❌ الملف غير موجود: {file_path}[/bold red]")
        return

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        marker = b"\n---CYBEROS_SECRET_START---\n"
        secret_bytes = marker + secret_text.encode("utf-8")

        with open(output_path, "wb") as f:
            f.write(data + secret_bytes)

        console.print(f"[bold green]✔ تم دمج النص الخفي داخل الملف بنجاح! الملف الجديد: {output_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ خطأ أثناء الإخفاء: {e}[/bold red]")

def extract_text_from_file(file_path: str):
    """استخراج النص المخفي من الملف"""
    if not os.path.exists(file_path):
        console.print(f"[bold red]❌ الملف غير موجود: {file_path}[/bold red]")
        return

    try:
        with open(file_path, "rb") as f:
            content = f.read()

        marker = b"\n---CYBEROS_SECRET_START---\n"
        if marker in content:
            parts = content.split(marker)
            secret = parts[-1].decode("utf-8", errors="ignore")
            console.print(f"[bold green]🔓 النص المخفي المستخرج:\n[/bold green][yellow]{secret}[/yellow]")
        else:
            console.print("[yellow]⚠️ لم يتم العثور على أية نصوص مخفية داخل هذا الملف.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ خطأ أثناء الاستخراج: {e}[/bold red]")
