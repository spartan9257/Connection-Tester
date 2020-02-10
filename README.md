#The Simple Connection Tester v1.0.1
#Samuel Bravo, 01/31/2020

NOTE: For the best readability, view this text using wordPad.

Uses ICMP to test the connection to a list of IP address. Failed attempts generate an email notification. The state of each device is tracked independently so that notifications can be generated on a per device basis periodically.

Installation:
  1. Place main.py and definitions.py into an empty directory.
  2. Create the following files exactly as they appear:
	server_info.csv
	creds.csv
	hosts.csv
	email_recipients.csv
  3. Populate each file with the appropriate information (see  	bellow for more details).
  4. Run main.py to start the program

Changing configuration files:
Because all of the information that the script uses is stored in separate files, modifying them is simple. For instance; to add or remove hosts simply modify the entries in the hosts.csv file. If you'd like to add or remove admin email addresses from the recipient list, simply update email_recipients.csv. 

NOTE: Modifying any of the configuration files will require the script to be restarted for the changes to take effect.

-----------------------------------------------------------------

Configuration files:

server_info.csv
 Contains the address of the server being used to send the notifications and the port# it's listening on. Create a single entry using the following syntax: "server_address,port#" (Ex - 10.1.1.254,587)

creds.csv 
Contains the login credentials for the server being used to send the notifications. For security reasons a private internal email server is recommended as well as an account being used souly to receive these notifications. Create a single entry using the following syntax: "username,password".

hosts.csv 
Contains all the host IP address, descriptions, and location information. All of the hosts in this file will be tested for connectivity. Each host entry will contain 4 fields and must use the following syntax: "hostIP,description,location,0" (Ex - 10.1.1.254,Cisco Router,Bldg 6 MDF 101,0)
NOTE: Blank lines and lines that begin with "#" will be ignored to allow for basic formatting and comments.
NOTE: the last field containing the 0 is used by the program to track the state of the device, therefore it MUST be included.

email_recipients.csv
Contains the email address of all the recipients that will get a notification when a connection fails. Simply add each email address separated by a comma (Ex - admin_1@company.net,admin_2@compay.net,sysadmin@company.net"

-----------------------------------------------------------------

Default configurations:

Logging:
When main.py first runs /logs/logfile.txt will automatically be created. A new log file will be generated daily and will contain entries of the failed/restored devices. If no issues occurred, the file will remain empty. By default 150 log files will be created to keep a back log for approximately 5 months. Once exceeded the oldest logs will begin to be automatically deleted.

Periodic Interval:
Connections are tested every 300 seconds (5min). To modify it change the main.py variable "periodicInterval = (sec)"

checkPing() will attempt a connection 3 times before declaring it as failed. To adjust to number of attempts change the line containing "while(count < #):" so that # is equal to the number of desired attempts - 1.

Once an issue occurs it will be tracked until the connection succeeds. By default an email alert for an issue being tracked will be sent every 60 minutes. To change the notification interval change the value of "email_notification_every" in main.py the integer specified is the number of seconds between notifications.

Debugging:
By default debugging is turned off, to enable debugging set "debug_on=True" in main.py. Debugging logs are generated during the programs run time, allowing you to see the what the program is doing (or not doing). The debug.txt file will be created automatically and can be viewed while the program is running, once the program is terminated the logs will be erased.

-----------------------------------------------------------------

Functions - definition.py

checkPing(ip_address):
	Attempts to send an ICMP echo-request to the specified 	ip_address. If the first attempt fails 2 more requests are 	sent. If those attempts also fail return False, or if any of 	the attempts succeed return True.

sendEmail(sender,passwd,recipients,body,subject,serverInfo):
	sender: username used to log into the email server.
	passwd: password used to log into the email server.
	recipients: the list of destination email addresses.
	body: the message text being sent.
	subject: email subject field defined by the admin.
	serverInfo: list containing the email servers ip and port#.
	
	The above information is compiled together to generate an 	email notification. A secured connection to the SMTP server 	is established using TLS, then the login credentials are 	sent. If the login authentication succeeds, the email(s) is 	sent then the connection is terminated.

creat_log_file():
	Controls the creation of log files using the current date so 	that a new logfile is created every 24hrs.

	Generates a logfile name using the current date, then 	checks to see if a log folder exists in the current 	directory. If the folder isn't found then it's created along 	with 	a logfile using the name that was generated. Then 	the current time/ date are added to the first line of the 	file and the file's name is returned.
	If the folder already existed, then it checks to see if 	there's already a file using the name that was generated. 	If there is a logfile already created, return the name of 	that file. 
	
	The number of log files stored in the logs folder is then 	counted. If it exceeds 150, the oldest logs are 	automatically deleted.

-----------------------------------------------------------------

Psudo Code for main.py

check to see if the the file hosts_info.csv exists, if it doesnt print an error
if it does exist, get each line and save it to a list called host_info

check to see if the file creds.csv exists, it doesnt print an error
if it does exist, pull the username and passwd then save it to the list creds

Start and infinite loop
	begin a timer that pauses the system for 300 seconds
	call create_log_file() to create the logs folder and log file

	for every host in the host_info list do:

		attempt to ping it with checkPing(), if it fails do:
			set detectedFailures to true
			create a log entry in the log file
			build the contents for an email notification
			pull email_recipients to get the destination address
			pull the sending servers contact from server_info
			add the host to the list of failedDevices

			determine if its the first occurrence, if false do:
				save the issue_start_time
				send the email alerts
				set prior_email_sent to true

			if its an on-going issue being tracked, do:
				if timeLapsed exceeds the notification interval, do:
					send another email alert
				otherwise just create a new log entry

		if failures were detected, and the connection was successful, do:
			check if the host is in the failedDevices list, if true:
				send an email alerting that a connection was restored
				create another log entry
				remove the host from the failedDevices list

	if no faileddevices were detected, reset the following variables:
		issue_start_time = 0
		detectedIssues = False
		prior_email_sent = False
		
				