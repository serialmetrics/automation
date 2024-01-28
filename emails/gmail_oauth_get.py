"""
Here are utils to manage access token for Gmail API
"""
import os
import sys
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

GMAIL_REDIRECT_URI = os.getenv("GMAIL_REDIRECT_URI", "https://oauth2.dance/")

def get_gmail_access_token(
    username: str,
    gmail_client_id: str,
    gmail_client_secret: str,
    gmail_redirect_uri: str = GMAIL_REDIRECT_URI
):
    # if there is a file with name f"{username}.json" in the current directory, read it
    key_file = os.path.join(os.getenv("KEYS_DIR"), f"{username}.json")
    if os.path.isfile(key_file):
        print(f"Found {key_file}", file=sys.stderr)
        with open(key_file, "r") as f:
            data = json.loads(f.read())
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]
            expire_in = data["expire_in"]
            created_at = data["created_at"]
            expire_at = created_at + expire_in
            if expire_at > int(time.time()):
                print(f"Access token is still valid: {access_token}", file=sys.stderr)
                return access_token
            else:
                print(f"Access token is expired: {access_token}", file=sys.stderr)
                # use refresh token to get new access token
                return refresh_gmail_access_token(username, gmail_client_id, gmail_client_secret, refresh_token)
    else:
        # use authorization code to get access token
        return get_gmail_authorization_code(username, gmail_client_id, gmail_client_secret, gmail_redirect_uri)

def refresh_gmail_access_token(
    username: str,
    gmail_client_id: str,
    gmail_client_secret: str,
    refresh_token: str,
):
    # use refresh token to get new access token
    params = {
        "client_id": gmail_client_id,
        "client_secret": gmail_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    request_url = "https://oauth2.googleapis.com/token"
    print(f"Refreshing token: {refresh_token}", file=sys.stderr)
    response = urlopen(Request(request_url, urlencode(params).encode())).read()
    print(f"Response: {response}", file=sys.stderr)
    response = json.loads(response)
    response['refresh_token'] = refresh_token
    save_tokens(response, username)
    return response["access_token"]

def get_gmail_authorization_code(
    username: str,
    gmail_client_id: str,
    gmail_client_secret: str,
    gmail_redirect_uri: str = GMAIL_REDIRECT_URI
):
    # use authorization code to get access token
    permissions_url = generate_permissions_url(gmail_client_id)
    print(f"\nOpen the URL in browser and grant permission:7\n{permissions_url}")
    # wait for user to grant permission
    authorization_code = input('Enter verification code: ')
    response = authorize_tokens(gmail_client_id, gmail_client_secret, authorization_code, gmail_redirect_uri)
    save_tokens(response, username)
    return response["access_token"]

def save_tokens(response: dict, username: str):
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]
    expire_in = response["expires_in"]
    created_at = int(time.time())
    key_file = os.path.join(os.getenv("KEYS_DIR"), f"{username}.json")
    with open(key_file, "w") as f:
        f.write(json.dumps({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_in": expire_in,
            "created_at": created_at
        }))

def generate_permissions_url(gmail_client_id: str):
    params = {
        "client_id": gmail_client_id,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "scope": "https://mail.google.com/",
        "redirect_uri": GMAIL_REDIRECT_URI
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

def authorize_tokens(
    gmail_client_id: str,
    gmail_client_secret: str,
    authorization_code: str,
    gmail_redirect_uri: str = GMAIL_REDIRECT_URI
):
    # use authorization code to get access token
    params = {
        "client_id": gmail_client_id,
        "client_secret": gmail_client_secret,
        "code": authorization_code,
        "redirect_uri": gmail_redirect_uri,
        "grant_type": "authorization_code"
    }
    response = urlopen("https://oauth2.googleapis.com/token", urlencode(params).encode("utf-8")).read().decode("utf-8")
    return json.loads(response)