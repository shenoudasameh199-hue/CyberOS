import os
import hashlib
from rich.console import Console

console = Console()

def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)

def encrypt_file(filepath: str, password: str):
    if not os.path.exists(filepath):
        console.print("[bold red]❌ الملف غير موجود.[/bold red]")
        return
    try:
        salt = os.urandom(16)
        key = _derive_key(password, salt)
        with open(filepath, 'rb') as f:
            data = f.read()
        
        encrypted_data = bytearray()
        for i, byte in enumerate(data):
            block = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()
            encrypted_data.append(byte ^ block[0])
            
        out_path = filepath + ".enc"
        with open(out_path, 'wb') as f:
            f.write(salt + bytes(encrypted_data))
            
        console.print(f"[bold green]🔒 تم تشفير الملف بنجاح وحفظه في: {out_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ خطأ أثناء التشفير: {e}[/bold red]")

def decrypt_file(filepath: str, password: str):
    if not os.path.exists(filepath):
        console.print("[bold red]❌ الملف غير موجود.[/bold red]")
        return
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        salt = content[:16]
        data = content[16:]
        key = _derive_key(password, salt)
        
        decrypted_data = bytearray()
        for i, byte in enumerate(data):
            block = hashlib.sha256(key + i.to_bytes(4, 'big')).digest()
            decrypted_data.append(byte ^ block[0])
            
        out_path = filepath.rstrip(".enc") + ".dec" if filepath.endswith(".enc") else filepath + ".dec"
        with open(out_path, 'wb') as f:
            f.write(bytes(decrypted_data))
            
        console.print(f"[bold green]🔓 تم فك تشفير الملف بنجاح وحفظه في: {out_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ خطأ أثناء فك التشفير: {e}[/bold red]")
