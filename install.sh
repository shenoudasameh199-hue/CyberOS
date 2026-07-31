#!/usr/bin/env bash
set -e
echo -e "\033[0;36m[+] Installing system requirements & Python packages...\033[0m"
pkg update -y && pkg upgrade -y
pkg install python git clang libjpeg-turbo libpng -y
pip install --upgrade pip
pip install -r requirements.txt

echo -e "\033[0;36m[+] Creating global 'cyber' command...\033[0m"
echo -e '#!/usr/bin/env bash\ncd ~/CyberOS && python main.py' > $PREFIX/bin/cyber
chmod +x $PREFIX/bin/cyber

echo -e "\033[0;32m[✔] CyberOS v1.0 Installed Successfully!\033[0m"
