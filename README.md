
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