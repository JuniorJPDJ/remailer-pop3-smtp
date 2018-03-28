#!/usr/bin/env python3
import email
import poplib
import smtplib
import logging
import sys

import yaml

# DONE: downloading mails by pop3
# DONE: deleting mails by pop3
# DONE: sending mails through SMTP
# DONE: adding prefixes to topics
# DONE: changing reply-to to original author
# DONE: changing bcc to list of recipients
# DONE: changing sender to own address
# DONE: detect Delivery Status Notifications and stop loops


main_logger = logging.getLogger('Remailer')

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(name)s: %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S',
                    stream=sys.stdout,
                    level=logging.INFO)

with open('config.yaml', 'r') as file:
    conf = yaml.safe_load(file)

for l in conf:
    logger = main_logger.getChild("{} <{}>".format(l['sender_name'], l['sender_email']))
    if l['pop3_ssl']:
        pop3 = poplib.POP3_SSL(l['pop3_server'], l['pop3_port'] if 'pop3_port' in l else poplib.POP3_SSL_PORT)
    else:
        pop3 = poplib.POP3(l['pop3_server'], l['pop3_port'] if 'pop3_port' in l else poplib.POP3_PORT)

    pop3.user(l['pop3_user'])
    pop3.pass_(l['pop3_pass'])

    msgs = []
    msg_num = len(pop3.list()[1])
    for i in range(msg_num):
        msg = email.message_from_bytes(b'\n'.join(pop3.retr(i + 1)[1]))

        # you can modify message to send here

        if not msg['reply-to']:
            msg['reply-to'] = msg['from']
        del msg['from']
        msg['from'] = "{} <{}>".format(l['sender_name'], l['sender_email'])

        if (msg.is_multipart() and len(msg.get_payload()) > 1 and
                msg.get_payload(1).get_content_type() == 'message/delivery-status'):
            # detect Delivery Status Notifications
            # https://stackoverflow.com/questions/5298285/detecting-if-an-email-is-a-delivery-status-notification-and-extract-informatio
            # https://tools.ietf.org/html/rfc3464#page-7
            # send them to other recipments list
            logger.info("DSN to forward: %s", msg['subject'])
            msg['bcc'] = ','.join(l['dsn_recipments'])
        else:
            logger.info("Message to forward: %s", msg['subject'])
            msg['bcc'] = ','.join(l['recipients'])

        subject = l['topic_prefix'] + msg['subject']
        del msg['subject']
        msg['subject'] = subject

        del msg['to']
        del msg['cc']

        msgs.append(msg)
        pop3.dele(i + 1)

    pop3.quit()

    if msgs:
        logger.info("%d new messages to forward", len(msgs))

    if msgs:
        if['smtp_ssl']:
            smtp = smtplib.SMTP_SSL(l['smtp_server'], l['smtp_serverport'] if 'smtp_serverport' in l else 0)
        else:
            smtp = smtplib.SMTP(l['smtp_server'], l['smtp_serverport'] if 'smtp_serverport' in l else 587 if l['smtp_starttls'] else 0)
            if l['smtp_starttls']:
                smtp.starttls()

        smtp.login(l['smtp_user'], l['smtp_pass'])
        for msg in msgs:
            smtp.send_message(msg)

        smtp.quit()
