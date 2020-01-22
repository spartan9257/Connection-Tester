import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Return true if ping was successful
def checkPing(host):
    count = 0
    while(count < 1):
        response = os.system("ping -n 1 " + host)
        # and then check the response...
        if response == 0:
            pingstatus = True
            break
        else:
            print("Reattempting the connection...")
            pingstatus = False
            simpleTimer(10)
            count = count + 1
    if pingStatus == False:
        print("Unable to connect to host after 3 attempts")
    return pingstatus

#send an email notification
def sendEmail(sender, passwd, recipients, body, subject, serverInfo):
    #Create message parameters
    message = MIMEMultipart()
    for destination_address in recipients:
        print("Sending email to admin at " + str(destination_address))
        #Create message
        message['From'] = sender
        message["To"] = ','.join(destination_address)
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()

        #Connect to google smtp server (can be changed to different provider)
        print("Connecting to server @" + str(serverInfo[0][0]) + " via port " + str(serverInfo[0][1]))
        server = smtplib.SMTP(str(serverInfo[0][0]), str(serverInfo[0][1]))
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
