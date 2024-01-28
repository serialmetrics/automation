from contextlib import contextmanager
import os
import pprint
from typing import Dict

from dotenv import load_dotenv
from imap_tools import MailBox, AND

from .gmail_oauth_get import get_gmail_access_token

load_dotenv()

pp = pprint.PrettyPrinter(indent=4)
pt = pp.pprint

DICT_ATTRS = 'uid,subject,from_,to,cc,bcc,reply_to,date,date_str,text,html,flags,size_rfc822,size'.split(',')
ATTACHMENT_ATTRS = 'filename,payload,content_id,content_type,content_disposition,size'.split(',')

def html_to_md(html):
    import html2text
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(html)


def html_to_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

# Convert attachment to dict
def attachment_to_dict(attachment):
    d = {k: getattr(attachment, k) for k in ATTACHMENT_ATTRS}
    return d

def get_text_without_breaking_words(text, max_length):
    if len(text) <= max_length:
        return text

    words = text.split()
    result = ""
    for word in words:
        if not word.strip():
            continue
        if len(result) + len(word) + 1 > max_length:
            break
        result += (word + " ")

    return result.strip()

# Convert email.message.Message to dict
def message_to_dict(message):
    d = {k: getattr(message, k) for k in DICT_ATTRS}
    d['message_id'] = message.headers.get('message-id')[0]
    d['references'] = message.headers.get('references')
    d['attachments'] = [attachment_to_dict(attachment) for attachment in message.attachments]
    if not d['text'] and d['html']:
        d['text'] = html_to_md(d['html'])
    
    # make text shorter
    short_text = get_text_without_breaking_words(d['text'], 10000)
    d['full_text'] = d['text']
    d['text'] = short_text
    return d


@contextmanager
def get_mailbox():
    IMAP_USER = os.getenv('IMAP_USER')
    # Get date, subject and body len of all emails from INBOX folder
    if IMAP_USER.split('@')[1] == 'gmail.com':
        # create a Google app here https://console.developers.google.com
        # then fill the following variables
        GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
        GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
        GMAIL_REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI')

        access_token = get_gmail_access_token(IMAP_USER, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REDIRECT_URI)
        with MailBox("imap.gmail.com").xoauth2(username=IMAP_USER, access_token=access_token) as mail_box:
            yield mail_box
    else:
        IMAP_SERVER = os.getenv('IMAP_SERVER')
        IMAP_PASS = os.getenv('IMAP_PASS')

        with MailBox(IMAP_SERVER).login(IMAP_USER, IMAP_PASS) as mail_box:
            yield mail_box

def get_imap_messages() -> Dict:
    keep_unseen = os.getenv('IMAP_KEEP_UNSEEN_ON_FETCH', 'False').lower() == 'true'
    with get_mailbox() as mailbox:
        mailbox.folder.set('INBOX')
        for msg in mailbox.fetch(AND(seen=False), mark_seen=not keep_unseen):
            yield message_to_dict(msg)


if __name__ == '__main__':
    for msg in get_imap_messages():
        pt(msg)