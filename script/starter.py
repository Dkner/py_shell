import os
import subprocess

commands = [
    '"C:/Users/liliang_hu/AppData/Local/youdao/apps/YoudaoNote/RunYNote.exe"',
    '"C:/Users/liliang_hu/AppData/Local/Google/Chrome/Application/chrome.exe"',
    '"C:/Program Files/TrueCrypt/TrueCrypt.exe"',
    '"C:/Program Files/VanDyke Software/SecureCRT/SecureCRT.exe"',
    # '"C:/Program Files (x86)/JetBrains/PhpStorm 8.0.3/bin/PhpStorm.exe"',
    '"D:/appserv/Apache2.4/bin/httpd.exe"',
    # '"D:/IntelliJ IDEA Community Edition 14.1.5/bin/idea.exe"',
    '"C:/Users/liliang_hu/Desktop/Sublime Text/sublime_text.exe"',
    # '"D:/IntelliJ IDEA 2016.3.4/bin/idea64.exe"'
]

os.startfile("outlook")

for i in commands:
    subprocess.Popen(i)