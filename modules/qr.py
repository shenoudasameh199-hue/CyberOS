import qrcode
from rich.console import Console

console = Console()

def generate_terminal_qr(data: str) -> None:
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make(fit=True)
    console.print("\n[bold cyan]📱 رمز الـ QR الخاص بك في الترمكس:[/bold cyan]\n")
    qr.print_ascii(invert=True)

def save_qr_image(data: str, filename: str = "qrcode.png") -> None:
    try:
        img = qrcode.make(data)
        img.save(filename)
        console.print(f"\n[bold green]✔ تم حفظ صورة QR بنجاح بالاسم: {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]فشل حفظ الصورة: {e}[/bold red]")
