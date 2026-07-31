import random
import string
from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_password(length: int = 16, use_upper: bool = True, use_digits: bool = True, use_symbols: bool = True) -> str:
    chars = string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    pwd = "".join(random.choice(chars) for _ in range(length))
    console.print(Panel(f"[bold green]{pwd}[/bold green]", title="🔒 كلمة المرور المولدة", border_style="green"))
    return pwd

def analyze_password(password: str) -> None:
    score = 0
    reasons = []

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        reasons.append("الطول أقل من 8 أحرف.")

    if any(c.isupper() for c in password): score += 1
    else: reasons.append("لا تحتوي أحرف كبيرة.")

    if any(c.islower() for c in password): score += 1
    else: reasons.append("لا تحتوي أحرف صغيرة.")

    if any(c.isdigit() for c in password): score += 1
    else: reasons.append("لا تحتوي أرقام.")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
    else: reasons.append("لا تحتوي رموز خاصة.")

    status = "ضعيفة ❌" if score < 3 else "متوسطة ⚠️" if score < 5 else "قوية جداً 🛡️"
    color = "red" if score < 3 else "yellow" if score < 5 else "green"

    output = f"التقييم: [{color}]{status}[/{color}]\nالنقاط: {score}/6\n"
    if reasons:
        output += "\nملاحظات للتحسين:\n" + "\n".join(f"- {r}" for r in reasons)

    console.print(Panel(output, title="محلل حماية كلمة المرور", border_style=color))
