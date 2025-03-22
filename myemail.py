import smtplib
import os
from dotenv import load_dotenv
load_dotenv()


GMAIL_USER = os.getenv("gmail_user")
GMAIL_PASSWORD = os.getenv("gmail_pwd")
FROM = GMAIL_USER
TO = [Email]
SUBJECT = "Alert"
TEXT = "High Traffic.....Take a different route"

# Prepare actual message
message = """From: %s\nTo: %s\nSubject: %s\n\n%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    server.close()
    print("successfully sent the mail")
except:
    print ("failed to send mail")