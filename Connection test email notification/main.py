from definitions import checkPing, sendEmail, simpleTimer, create_log_file
from subprocess import check_output
from os import path
import csv,time,os,subprocess 

#The Simple Connection Tester v1.0.1
#Samuel Bravo, 01/31/2020

print("The Simple Connection Tester v1.0.2")

#!For gmail accounts less secure app access MUST be enabled
#!https://myaccount.google.com/lesssecureapps

debugFile = open("debug.txt","w")
debugFile.close()



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
            #if the line contains data AND doesnt start with #, append it
            if row and row[0].find("#") == -1:
                hosts_info.append(row)
        csvFile.close()
print(hosts_info)
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
debug_on = False                #Creates a file debug.txt that contains program logs

while(True):

    debugFile = open("debug.txt", "a")

    #Set a timer to control when the loop begins
    print("Periodic timer set for " + str(periodicInterval) + " seconds")
    os.system("time /T")
    print("Timer started...")
    simpleTimer(periodicInterval)
    print("Begining connection tests")
    
    #Checks to see if a log file exists, if not it creates one
    #This allows a new log file to be created daily when the date changes
    log_file_name = create_log_file()
    
    #attempt to ping the host IP, if it fails generate an email if none have been generated
    #already, or enough time has lapsed since the last email was sent.
    for host in hosts_info:
        print("\n--> ",end=" ")

        #Convert the hosts failure time tracker to an integer
        host[3] = int(host[3])
        
        #Test the connection to the host
        pingStatus = checkPing(host[0])

        if pingStatus == False:
            if debug_on:
                debugFile.write("Connection failed\n")
            #Track the state of failed connections
            detectedFailures = True

            #Write a new log entry
            log = open(log_file_name,"a")
            log_entry = check_output("time /T", shell=True).decode().replace("\n",'')
            log_entry = log_entry[:len(log_entry)-1] + " Connection to host " + str(host[:3]) + " FAILED\n"
            log.write(log_entry)
            log.close()

            #check if a previous issue was logged already
            if issue_start_time == 0:
                print("Logging issue occurence start time")
                issue_start_time = int(time.time())
                if debug_on:
                    debugFile.write("issue start time: " + str(issue_start_time) + "\n")

            #This if is only here because VS auto indented the following 20 lines and im lazy..
            if True:
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
            if host[3] == 0:
                if debug_on:
                    debugFile.write("Host last email sent time is 0, sending first email\n")
                print("No prior issue logged for this host, generating notification")
                sendEmail(sender, passwd, destination_address, body, subject, serverInfo)
                #track the time the email was sent for this host
                host[3] = time.time()
                if debug_on:
                    debugFile.write("Email sent time logged: " + str(host[3]) + "\n")

            #If a prior email was sent, check how much time has lapsed. Then send another email if
            #the time lapsed exceeds the periodic interval.
            elif (int(time.time()) - host[3]) / 60 + 1 >= email_notification_every:
                print("Persistant issue logged again, generating another email")
                sendEmail(sender, passwd, destination_address, body, subject, serverInfo)
                #track the time the email was sent for this host
                host[3] = time.time()

            #If the device isnt already in the list of failed devices, add it.
            if debug_on:
                debugFile.write("Current list of failed devices: " + str(failedDevices) + "\n")
            found = False
            if failedDevices:
                for device in failedDevices:
                    if device == host[0]:
                        found = True
                        if debug_on:
                            debugFile.write("host is already in the list of failed devices\n")
                if found == False:
                    print("Logging the device as failed.")
                    failedDevices.append(host[0])
                    if debug_on:
                        debugFile.write("host was not in the list of failed devices adding it not\n")
                        debugFile.write("failedDevices: " + str(failedDevices) + "\n")
            else:
                failedDevices.append(host[0])


        if pingStatus == True:
            #if the ping to a previouly failed device succeeds, remove it from the list of failed devices
            #and notify the admin.
            if debug_on:
                        debugFile.write("Connection was successful\n")
            if detectedFailures:
                for device in failedDevices:
                    if host[0] == device:
                        print("Connection to " + host[0] + " Restored")
                        print("Removing device from the failed log")

                        #Remove the host and reset its last email sent time tracker to 0
                        failedDevices.remove(host[0])
                        host[3] = 0

                        #Send a new email informing the recipient that the connection has been restored
                        body = "Connection to host " + str(host[0]) + " was restored.\n" + str(host[1]) + "\n" + str(host[2]) 
                        subject = "Connection Restored!"
                        sendEmail(sender, passwd, destination_address, body, subject, serverInfo)

                        #Create a new log entry
                        log = open(log_file_name,"a")
                        log_entry = check_output("time /T", shell=True).decode().replace("\n",'')
                        log_entry = log_entry[:len(log_entry)-1] + " Connection to host " + str(host[:3]) + " RESTORED\n"
                        log.write(log_entry)
                        log.close()

                    #Exit the for loop as soon as a match is found
                    break
        print("<--")

    #If no failed devices are being tracked, reset trackers
    if not failedDevices:
        failedDevices.clear()
        issue_start_time = 0
        detectedFailures = False
        prior_email_sent = False
        print("\nAll connections successful")
    else:
        print("\nConnection failures detected!")
    print("=========================================================\n")
    debugFile.close()
            
