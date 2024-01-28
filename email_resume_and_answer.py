import os
import sys
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

from emails.imap_utils import get_imap_messages
from emails.smtp_utils import respond_to_email, send_digest, smtp_server

from email_resume_and_answer_prompts import (
    RESPONSE_TEMPLATE,
    RESUME_TEMPLATE,
    DIGEST_TEMPLATE,
)

# load environment variables
load_dotenv()

# fetch emails
try:
    emails = [e for e in get_imap_messages()]
except Exception as e:
    print(f"Failed to fetch emails: {e}. Exiting...", e.message, file=sys.stderr)
    sys.exit(1)

if not emails:
    print("No unread emails found. Exiting...", file=sys.stderr)
    sys.exit(0)

# prepare prompts
response_prompt = ChatPromptTemplate.from_template(RESPONSE_TEMPLATE)
resume_prompt = ChatPromptTemplate.from_template(RESUME_TEMPLATE)
digest_prompt = ChatPromptTemplate.from_template(DIGEST_TEMPLATE)
# prepare models
gpt3_5_16k = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.2)
gpt4 = ChatOpenAI(model="gpt-4", temperature=0.2)
# prepare output parser
output_parser = StrOutputParser()

# prepare chains
response_chain = response_prompt | gpt3_5_16k | output_parser
resume_chain = resume_prompt | gpt3_5_16k | output_parser
digest_chain = digest_prompt | gpt4 | output_parser

# collect emails that will be answered and resumed
collected_email = []

# process each email
for idx, email in enumerate(emails, start=1):
    print(f"\n############ Email {idx}: From: {email['from_']}, Subject: {email['subject']}")
    # if email has non empty references, than it's not initial email
    # so, skip it to not interfere with human activity
    if email['references']:
        print(">>> Email has non empty references. Skipping...")
        continue

    email_text = email['text']
    # try to create a response to the email
    response = response_chain.invoke({
        'email_message': email['text'],
        'me': os.getenv("ME_IN_PROMPTS"),
    })
    # if the response is empty, skip the email and go to the next
    if response == "NONE":
        print(">>> Created response is empty, because it doesn't contain any offers. Skipping...")
        continue
    email['response'] = response
    
    print(f"{'-'*20}\nInitial email:\n{email['text']}")
    # if we have a response, make a resume from the original email for the digest
    resume = resume_chain.invoke({
        'email_message': email['text'],
    })

    # save the resume for digest
    email['resume'] = resume
    collected_email.append(email)
    
    # print the created response and the resume
    print(f"{'-'*20}\nResume:\n{resume}")
    print(f"{'-'*20}\nTo: {email['from_']}\nResponse:\n{response}")

if not collected_email:
    print("No emails collected. No digest will be created. Exiting...", file=sys.stderr)
    sys.exit(0)

# prepare list of messages for digest
email_list = "---\n".join([
    f"From: {email['from_']}\nBody:\n{email['resume']}\n" for email in collected_email if not email['references']
])
print(f"\n\n{'='*20}\nCollected emails for digest:\n{email_list}")

# create digest
digest = digest_chain.invoke({
    'email_list': email_list,
})
print(f"{'-'*20}\nDigest:\n{digest}")

# send emails
try:
    with smtp_server() as smtp_conn:
        # send responses
        for email in collected_email:
            respond_to_email(smtp_conn, email, email['response'])
        # send digest
        send_digest(smtp_conn, digest)

except Exception as e:
    print(f"Failed to send emails: {e}. Exiting...", e.message, file=sys.stderr)
    sys.exit(1)