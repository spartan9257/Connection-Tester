from definitions import checkPing, sendEmail, simpleTimer
import csv,time,os,subprocess 

#to Do:
#1. instead of sending an email for every device that fails, condense all the failed
#   devices into a single list. Then send an email with all of them.

#!For gmail accounts less secure app access MUST be enabled
#!https://myaccount.google.com/lesssecureapps

#Open the CSV file containing the list of hosts and append them to a list
hosts_info = []
print("Getting hosts information")
with open("hosts.csv") as csvFile:
    csvReader = csv.reader(csvFile, delimiter=',')
    for row in csvReader:
        hosts_info.append(row)
    csvFile.close()

#Get the credentials for the admin email account to send an email notification
creds = []
with open("creds.csv") as csvFile:
    csvReader = csv.reader(csvFile, delimiter=',')
    for row in csvReader:
        creds.append(row)
    csvFile.close()

issue_start_time = 0            #logs the time of the first failure occurence
email_notification_every = 3600 #sets the interval that the emails will be periodically resent
minutesLapsed = 0               #tracks the minutes that have lapsed since the last email was sent
last_email_sent_time = 0        #saves the time that the last email was sent
prior_email_sent = False 
DetectedFailures = False
failedDevices = []              #maintains a list of the host's whos connection failed
periodicInterval = 10           #Time in seconds between connection tests

while(True):
    print("Periodic timer started\The current time is: ", end=":")
    os.system("time /T")
    simpleTimer(periodicInterval)
    print("Begining connection tests")
    for host in hosts_info:
        print("Begining connection tests")
        #attempt to ping the host IP, if it fails generate an email if non has been generated
        #already. Or if enough time has lapsed since the last email was sent.
        if checkPing(host[0]) == False:
            DetectedFailures = True
            if issue_start_time == 0:
                print("Logging issue occurence start time")
                issue_start_time = int(time.time())

                #Get all the data needed to send an email notification
                body = "WARNING! Connection to host " + str(host[0]) + " failed.\n" + str(host[1]) + "\n" + str(host[2]) 
                subject = "Connection Failure"
                sender = str(creds[0][0])
                destination_address = []
                serverInfo = []
                passwd = str(creds[0][1])
                #Get the recipient(s) addresses from a csv file
                csvFile = open("email_recipients.csv", "r")
                csvReader = csv.reader(csvFile, delimiter=',')
                for address in csvReader:
                    destination_address.append(address)
                csvFile.close()
                #Get the server ip address and port# from a csv file
                csvFile = open("server_info.csv", "r")
                csvReader = csv.reader(csvFile, delimiter=',')
                for field in csvReader:
                    serverInfo.append(field)
                csvFile.close()

            #If a prior email hasn't been sent, generate one now.
            if prior_email_sent == False:
                print("No prior issue logged, generating notification")
                sendEmail(sender, passwd, destination_address, body, subject, serverInfo)
                prior_email_sent = True
                last_email_sent_time = int(time.time())

            #If a prior email was sent, check how much time has lapsed. Then send another email if
            #the time lapsed exceeds the periodic interval.
            elif int(time.time()) - last_email_sent_time >= email_notification_every:
                print("Persistant issue logged again, generating another email")
                sendEmail(sender, passwd, destination_address, body, subject, serverInfo)
                prior_email_sent = True
                last_email_sent_time = int(time.time())

            #If the device isnt already in the list of failed devices, add it.
            found = False
            if not failedDevices:
                failedDevices.append(host)
            else:
                for device in failedDevices:
                    print(device)
                    if device == host:
                        found = True
                    if found == False:
                        print("Logging the device as failed.")
                        failedDevices.append(host)

        else:
            #if the ping to a previouly failed device succeeds, remove it from the list of failed devices
            #and notify the admin.
            if DetectedFailures:
                for device in failedDevices:
                    if host == device:
                        print("Connection to " + host[0] + "Restored")
                        print("Removing device from the failed log")
                        failedDevices.remove(host)
                        #Send a new email informing the recipient that the connection has been restored
                        text = "Connection to host " + str(host[0]) + " was restored.\n" + str(host[1]) + "\n" + str(host[2]) 
                        subject = "Connection Restored!"
                        sendEmail(sender, passwd, destination_address, body, subject, serverInfo)
        
        if not failedDevices:
            print("All connections successful")
        else:
            print("Connection failures detected!")
            
