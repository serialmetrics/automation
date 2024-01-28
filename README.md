
# Automation

## Email automation

### email_resume_and_answer.py

The script that reads INBOX for new unread messages and creates responses for those that have
offerings and invitations. The way to detect this messages is defined by the template RESPONSE_TEMPLATE in email_resume_and_answer_prompts.py.
If the response for a message was not created by LLM, the message doesn't take part in further processing.
If response was created the resume for the source email is created too.
After all messages are scanned and responses and resumes are collected, the resumes go to the digest
creation process.
Responses and digest are then send to proper addresses.

### Here's how to get Client ID and Client Secret for XOAUTH authentication to access imap.gmail.com:

1. Create a Google Cloud Project:

    Visit the Google Cloud Console (https://console.cloud.google.com/).
    Create a new project or select an existing one.

2. Enable the Gmail API:

    In the Navigation menu, go to APIs & Services > Library.
    Search for "Gmail API" and enable it.

3. Create OAuth Client ID credentials:

    Go to APIs & Services > Credentials.
    Click Create credentials > OAuth client ID.
    Choose the application type that matches your usage -> Web application.
    Provide a name for your app and authorized JavaScript origins for web app, specify https://oauth2.dance/.
    Click Create.
    You'll receive the Client ID and Client Secret. Keep them confidential.