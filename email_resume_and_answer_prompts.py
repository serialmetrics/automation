
RESPONSE_TEMPLATE = """You are helpful personal assistant.
Read the provided message and if it's addressed personally to {me} and
offer a participation in some project related to creation of AI application or
other AI-based project, create a polite answer from me, stating that I will
concider the offer and respond to it as soon as possible.
If the message doesn't contain any such offerings, response with just a "NONE".

The message:
{email_message}
"""

RESUME_TEMPLATE = """You are helpful personal assistant.
Read the provided email message and make it compact and concise. Use only body of the message.
The main criteria you should follow - the result should be no longer than initial message.
Omit greetings and introductions. Keep all important details, especially the subject, contacts, dates and values.

The message:
{email_message}
"""

DIGEST_TEMPLATE = """You are helpful personal assistant.
Read the provided list of emails and make it compact and concise.
Use the provided example for the digest.
Digest should be a list where each line formated as "- <Sender's Full name> (<Sender's email>): <Message resume>".

Example of the digest:
- Bill Gates (bill@gates.com): Offering a project related to AI
- Mikhail Gorbachev (msg@kremlin.ru): Asking about ways to use AI to make money

The list of emails:
{email_list}
"""
