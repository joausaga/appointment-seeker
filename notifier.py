import logging
import smtplib, ssl



def notify_appointment(sender_email_address, sender_email_password, 
                      email_host_server, email_host_server_port, 
                      receiver_email_address):
    message = """\
    Subject: Hi there
    This message is sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(email_host_server, email_host_server_port, context=context) as server:
        server.login(sender_email_address, sender_email_password)
        server.sendmail(sender_email_address, receiver_email_address, message)
        logging.info('Notification email sent')
