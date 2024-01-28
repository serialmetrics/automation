from contextlib import contextmanager
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import os
import base64
import smtplib
import ssl
from typing import Any, Dict

from .gmail_oauth_get import get_gmail_access_token


@contextmanager
def smtp_server():
    """Connects to SMTP server and prepares it for sending.
    """
    SMTP_USER = os.getenv('SMTP_USER')
    # Get date, subject and body len of all emails from INBOX folder
    if SMTP_USER.split('@')[1] == 'gmail.com':
        # create a Google app here https://console.developers.google.com
        # then fill the following variables
        GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
        GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
        GMAIL_REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI')

        access_token = get_gmail_access_token(SMTP_USER, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REDIRECT_URI)
        auth_string = 'user={}\1auth=Bearer {}\1\1'.format(SMTP_USER, access_token)
        with smtplib.SMTP_SSL("smtp.googlemail.com", context=ssl.create_default_context()) as smtp_conn:
            # smtp_conn.set_debuglevel(True)
            smtp_conn.ehlo()
            smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string.encode('utf-8')).decode('utf-8'))
            smtp_conn.ehlo()
            yield smtp_conn
    else:
        SMTP_SERVER = os.getenv('SMTP_SERVER')
        SMTP_PASS = os.getenv('SMTP_PASS')

        with smtplib.SMTP_SSL(SMTP_SERVER, context=ssl.create_default_context()) as smtp_conn:
            # smtp_conn.set_debuglevel(True)
            smtp_conn.ehlo()
            smtp_conn.login(SMTP_USER, SMTP_PASS)
            yield smtp_conn
    

def respond_to_email(smtp_conn: smtplib.SMTP_SSL, email: Dict[str, Any], body: str):

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = f"Re: {email['subject']}"
    full_name = os.getenv("USER_FULLNAME")
    from_address = os.getenv('SMTP_USER')
    to_address = email['from_']
    original_message_id = email['message_id']
    original_references = f"{email['references']}\r\n " if email['references'] else ''

    if full_name:
        msg['From'] = formataddr((str(Header(full_name, 'utf-8')), from_address))
    else:
        msg['From'] = from_address
    
    if email['reply_to']:
        to_address = email['reply_to']
    # if override is defined, use it
    msg['To'] = to_override = os.getenv("OVERRIDE_TO", to_address)

    # if there are any Cc in the email, add them to the To field
    if email['cc'] and not os.getenv("OVERRIDE_TO"):
        msg['Cc'] = email['cc']

    msg['In-Reply-To'] = original_message_id
    msg['References'] = original_references + original_message_id
    smtp_conn.sendmail(from_address, msg['To'], msg.as_string())

def send_digest(smtp_conn: smtplib.SMTP_SSL, digest: str):
    msg = MIMEText(digest, 'plain', 'utf-8')
    msg['Subject'] = "[AI-Digest] Latest offerings and invitations"
    full_name = os.getenv("USER_FULLNAME")
    from_address = os.getenv("SMTP_USER")
    if full_name:
        msg['From'] = formataddr((str(Header(full_name, 'utf-8')), from_address))
    else:
        msg['From'] = from_address
    msg['To'] = os.getenv("OVERRIDE_TO", from_address)
    smtp_conn.sendmail(from_address, msg['To'], msg.as_string())


if __name__ == '__main__':
    with smtp_server() as smtp_conn:
        send_digest(smtp_conn, 'test')