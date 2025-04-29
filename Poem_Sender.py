
from Poem_Scraper import connect_Database
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
from dotenv import load_dotenv
import os
from datetime import date
import time

load_dotenv(r"PoemDelivery\.env")

def SQLReader():
    database, cursor = connect_Database()
    query = """SELECT * FROM poems WHERE is_sent = 0 ORDER BY RAND() LIMIT 1"""
    cursor.execute(query)
    result = cursor.fetchone()

    return result

def read_recipient(file):
    with open(file, 'r') as f:
        content = csv.DictReader(f)

        return list(content)

def Confidential():
    email = os.getenv("email")
    password = os.getenv("email_password")

    return email, password


def SSL_SMTP_Connection():
    connection = SMTP_SSL("smtp.gmail.com", 465, timeout = 10) 
    connection.ehlo()
    email, password = Confidential()
    connection.login(email, password)
    return connection


def Automated_email():
    attempts = 0
    while True:
        try:
            connection = SSL_SMTP_Connection()
            data = SQLReader()
            recipients = read_recipient(r"PoemDelivery\recipients.csv")
            email, _ = Confidential()
            file = r"PoemDelivery\heart.png"
            for information in recipients:
                message = MIMEMultipart()
                message["From"] = email
                message["To"] = information["email"]
                message["subject"] = data[1]

                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(open(file, 'rb').read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment', filename = os.path.basename((file)))

                message.attach(attachment)
                message.attach(MIMEText(data[2] + "\n" + data[3], 'plain'))

                connection.send_message(message)
                print(f"email sent to {information['name']}")
            
            return data[0]
        except Exception as e:
            attempts += 1
            print(f"error {e} occured, retrying!")
            time.sleep(5)

def SQLUpdate():
    database, cursor = connect_Database()
    target_update = Automated_email()
    time = date.today()
    query = f"""UPDATE poems
    SET is_sent = 1, date_sent = %s
    WHERE Poem_id = %s"""
    cursor.execute(query, (time, target_update))
    database.commit()
    cursor.close()
    database.close()

SQLUpdate()