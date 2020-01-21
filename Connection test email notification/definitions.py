import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Return true if ping was successful
def checkPing(host):
    hostname = host
    count = 0
    while(count < 1):
        response = os.system("ping -n 1 " + hostname)
        # and then check the response...
        if response == 0:
            pingstatus = True
            break
        else:
            print("Connection to host " + host + " failed! Reattempting...")
            pingstatus = False
            simpleTimer(10)
            count = count + 1

    return pingstatus

#send an email notification
def sendEmail(sender, passwd, recipients, body, subject):
    #Create message parameters
    message = MIMEMultipart()
    for destination_address in recipients:
        print("Sending email to admin at " + destination_address)
        #Create message
        message['From'] = sender
        message["To"] = ','.join(destination_address)
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()

        #Connect to google smtp server (can be changed to different provider)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() #begin a secure transmission
        server.login(sender, passwd)
        #send message
        server.sendmail(sender, destination_address, text)
        server.quit()

def simpleTimer(delay):
    startTime = int(time.time())
    while(True):
        if int(time.time()) - startTime >= delay:
            break
