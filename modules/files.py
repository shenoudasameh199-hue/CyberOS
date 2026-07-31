import os
from rich.console import Console
from rich.tree import Tree
from rich.table import Table

console = Console()

def show_tree(path: str = ".") -> None:
    if not os.path.exists(path):
        console.print("[bold red]المسار غير موجود.[/bold red]")
        return

    tree = Tree(f"📁 [bold cyan]{os.path.abspath(path)}[/bold cyan]")
    try:
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            if level > 1:
                continue
            sub_tree = tree if root == path else tree.add(f"📂 [yellow]{os.path.basename(root)}[/yellow]")
            for f in files[:10]:
                sub_tree.add(f"📄 [dim]{f}[/dim]")
        console.print(tree)
    except Exception as e:
        console.print(f"[bold red]خطأ أثناء العرض: {e}[/bold red]")

def get_dir_size(path: str = ".") -> None:
    total_size = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
                file_count += 1

    size_mb = total_size / (1024 * 1024)
    console.print(f"\n[bold green]📊 المساحة الإجمالية للمجلد '{path}': {size_mb:.2f} MB ({file_count} ملف)[/bold green]")

def search_files(directory: str, keyword: str) -> None:
    console.print(f"\n[bold cyan]🔍 البحث عن كلمة '{keyword}' في '{directory}'...[/bold cyan]")
    matches = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if keyword.lower() in f.lower():
                matches.append(os.path.join(root, f))

    if matches:
        table = Table(title="نتائج البحث", style="green")
        table.add_column("الملف المعثور عليه", style="white")
        for m in matches[:20]:
            table.add_row(m)
        console.print(table)
    else:
        console.print("[yellow]لم يتم العثور على أي ملفات مطابقة.[/yellow]")
