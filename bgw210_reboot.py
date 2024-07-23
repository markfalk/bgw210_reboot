import os
from time import sleep
import requests
from hashlib import md5
from os import environ
from slack_sdk.webhook import WebhookClient

# Get variables from environment
MODEM_IP = os.getenv("MODEM_IP", "192.168.1.254")
PASSWORD = os.getenv("PASSWORD")
DEBUG = True if os.getenv("DEBUG") else False

s = requests.Session()

if not PASSWORD:
    raise ValueError("The PASSWORD environment variable is not set.")

# Function to fetch nonce from login page
def get_nonce():
    url = f"http://{MODEM_IP}/cgi-bin/login.ha"
    print("Fetching initial cookie...")
    response = s.get(url)
    # call again now that we have a session cookie
    print("Fetching nonce...")
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
    response = s.post(login_url, data=login_data)
    if DEBUG:
        print(response.content)

def send_slack_message(slack_webhook_url, message_data):
    """Sends a Slack message with retries on failure.

    Args:
        slack_webhook_url: The Slack webhook URL.
        message_data: The message data to send.

    Returns:
        True if the message was sent successfully, False otherwise.
    """

    max_retries = 5
    retry_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            webhook = WebhookClient(slack_webhook_url)
            response = webhook.send_dict(message_data)
            if DEBUG:
                print(response.body)
            assert response.status_code == 200
            assert response.body == "ok"
            return True  # Success
        except Exception as e:
            print(f"Error sending Slack message: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                sleep(retry_delay)
            else:
                print("Maximum retries reached.")
    return False  # Failed after all retries

# Function to reboot the modem
def reboot_modem():
    login()
    """
    Reboots the modem by sending a request to the reboot URL.
    If the response status code is 302, it indicates success in sending the reboot command.
    Otherwise, prints a message indicating failure to send the reboot command.
    """
    reboot_url = f"http://{MODEM_IP}/cgi-bin/restart.ha"
    print("Loading retart page...")
    response = s.get(reboot_url)
    if DEBUG:
        print(response.content)

    if response.status_code == 200:
        print("Restart page loaded...")
    else:
        print("Failed to load restart page.")
        raise SystemExit(1)

    nonce = response.text.split('name="nonce" value="')[1].split('"')[0]
    reboot_data = {
        "nonce": nonce,
        "Restart": "Restart"
    }
    print("Rebooting the modem...")
    response = s.post(reboot_url, data=reboot_data)
    if DEBUG:
        print(response.content)
    print(f"Reboot command sent to the modem.  Response Code: {response.status_code}")

    slack_webhook_url = environ.get('SLACK_WEBHOOK_URL')
    if slack_webhook_url:
        message_data = {
            "username": "AT&T Modem",
            "text": f"response status_code: {response.status_code}",
            "icon_emoji": ":bgw210:",
        }
        send_slack_message(slack_webhook_url, message_data)

# Call the reboot function
if __name__ == "__main__":
    reboot_modem()
