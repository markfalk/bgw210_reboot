import os
import requests
from hashlib import md5

# Get variables from environment
MODEM_IP = os.getenv("MODEM_IP", "192.168.1.254")
PASSWORD = os.getenv("PASSWORD")

s = requests.Session()

if not PASSWORD:
    raise ValueError("The PASSWORD environment variable is not set.")

# Function to fetch nonce from login page
def get_nonce():
    url = f"http://{MODEM_IP}/cgi-bin/login.ha"
    response = s.get(url)
    # call again now that we have a session cookie
    response = s.get(url)
    nonce = response.text.split('name="nonce" value="')[1].split('"')[0]
    return nonce

# Function to generate hashed password
def get_hashed_password(nonce, password):
    hash_input = (password + nonce).encode('utf-8')
    hashed_password = md5(hash_input).hexdigest()
    return hashed_password

# Function to login and get cookies
def login():
    nonce = get_nonce()
    hashed_password = get_hashed_password(nonce, PASSWORD)
    
    login_data = {
        "nonce": nonce,
        "password": "****",
        "hashpassword": hashed_password,
        "Continue": "Continue"
    }
    
    login_url = f"http://{MODEM_IP}/cgi-bin/login.ha"
    print("Logging in...")
    s.post(login_url, data=login_data)


# Function to reboot the modem
def reboot_modem():
    login()
    """
    Reboots the modem by sending a request to the reboot URL.
    If the response status code is 200, it indicates success in sending the reboot command.
    Otherwise, prints a message indicating failure to send the reboot command.
    """
    reboot_url = f"http://{MODEM_IP}/cgi-bin/restart.ha"
    # reboot_url = f"http://{MODEM_IP}/cgi-bin/securityoptions.ha"
    response = s.get(reboot_url)
    
    if response.status_code == 200:
        print("Reboot command sent to the modem.")
    else:
        print("Failed to send reboot command.")

# Call the reboot function
if __name__ == "__main__":
    reboot_modem()
