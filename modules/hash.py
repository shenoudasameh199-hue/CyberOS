import hashlib
import os
from rich.console import Console
from rich.table import Table

console = Console()

def hash_string(text: str) -> None:
    encoded = text.encode("utf-8")
    table = Table(title="🔑 نتائج التجزئة للنص", style="cyan")
    table.add_column("الخوارزمية", style="yellow")
    table.add_column("Hash", style="bold green")

    table.add_row("MD5", hashlib.md5(encoded).hexdigest())
    table.add_row("SHA-1", hashlib.sha1(encoded).hexdigest())
    table.add_row("SHA-256", hashlib.sha256(encoded).hexdigest())
    table.add_row("SHA-512", hashlib.sha512(encoded).hexdigest())

    console.print(table)

def hash_file(file_path: str) -> None:
    if not os.path.isfile(file_path):
        console.print("[bold red]❌ الملف غير موجود![/bold red]")
        return

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5.update(chunk)
                sha256.update(chunk)

        table = Table(title=f"🔑 نتائج تجزئة الملف: {os.path.basename(file_path)}", style="cyan")
        table.add_column("الخوارزمية", style="yellow")
        table.add_column("Hash", style="bold green")

        table.add_row("MD5", md5.hexdigest())
        table.add_row("SHA-256", sha256.hexdigest())
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]خطأ أثناء قراءة الملف: {e}[/bold red]")
