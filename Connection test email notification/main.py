from definitions import checkPing, sendEmail, simpleTimer, create_log_file
from subprocess import check_output
from os import path
import csv,time,os,subprocess 

#!For gmail accounts less secure app access MUST be enabled
#!https://myaccount.google.com/lesssecureapps


#Open the CSV file containing the list of hosts and append them to a list
hosts_info = []
print("Getting hosts information")
#make sure the host file exists
if path.exists("hosts.csv") == False:
    print("Error: hosts.csv not found. Create the file and add it to the same directory as main.py")
    os.system("pause")
    exit()
else:
    with open("hosts.csv") as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        for row in csvReader:
            if row:
                hosts_info.append(row)
        csvFile.close()

#Get the credentials for the admin email account to send an email notification
creds = []
if path.exists("creds.csv") == False:
    print("Error: creds.csv not found. Create the file and add it to the same directory as main.py")
    os.system("pause")
    exit()
else:
    with open("creds.csv") as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        for row in csvReader:
            if row:
                creds.append(row)
        csvFile.close()

issue_start_time = 0            #logs the time of the first failure occurence
email_notification_every = 3600 #sets the interval that the emails will be periodically resent
minutesLapsed = 0               #tracks the minutes that have lapsed since the last email was sent
last_email_sent_time = 0        #saves the time that the last email was sent
prior_email_sent = False 
detectedFailures = False
failedDevices = []              #maintains a list of the host's whos connection failed
periodicInterval = 10           #Time in seconds between connection tests

while(True):
    #Set a timer to control when the loop begins
    print("Periodic timer set for " + str(periodicInterval) + " seconds")
    os.system("time /T")
    simpleTimer(periodicInterval)
    print("Begining connection tests")
    
    #Checks to see if a log file exists, if not it creates one
    #This allows a new log file to be created daily when the date changes
    log_file_name = create_log_file()

    for host in hosts_info:
        #attempt to ping the host IP, if it fails generate an email if; none have been generated
        #already, or enough time has lapsed since the last email was sent.
        print("\n--> ",end=" ")
        if checkPing(host[0]) == False:
            detectedFailures = True

            #Write a new log entry
            log = open(log_file_name,"a")
            log_entry = check_output("time /T", shell=True).decode().replace("\n",'')
            log_entry = log_entry[:len(log_entry)-1] + " Connection to host " + str(host) + " FAILED\n"
            log.write(log_entry)
            log.close()

            #check if a previous issue was logged already
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
                    if address:
                        destination_address.append(address)
                csvFile.close()
                #Get the server ip address and port# from a csv file
                csvFile = open("server_info.csv", "r")
                csvReader = csv.reader(csvFile, delimiter=',')
                for field in csvReader:
                    if field:
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
                    if device == host:
                        found = True
                    if found == False:
                        print("Logging the device as failed.")
                        failedDevices.append(host)

        else:
            #if the ping to a previouly failed device succeeds, remove it from the list of failed devices
            #and notify the admin.
            if detectedFailures:
                for device in failedDevices:
                    if host == device:
                        print("Connection to " + host[0] + "Restored")
                        print("Removing device from the failed log")
                        failedDevices.remove(host)
                        #Send a new email informing the recipient that the connection has been restored
                        body = "Connection to host " + str(host[0]) + " was restored.\n" + str(host[1]) + "\n" + str(host[2]) 
                        subject = "Connection Restored!"
                        sendEmail(sender, passwd, destination_address, body, subject, serverInfo)
                        #Create a new log entry
                        log = open(log_file_name,"a")
                        log_entry = check_output("time /T", shell=True).decode().replace("\n",'')
                        log_entry = log_entry[:len(log_entry)-1] + " Connection to host " + str(host) + " RESTORED\n"
                        log.write(log_entry)
                        log.close()
        print("<--")

    #If no failed devices are being tracked, reset trackers
    if not failedDevices:
        issue_start_time = 0
        detectedFailures = False
        prior_email_sent = False
        print("\nAll connections successful")
    else:
        print("\nConnection failures detected!")
    print("=========================================================\n")
            
