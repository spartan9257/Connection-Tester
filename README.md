# Connection-Tester
Uses ICMP to test the connection to a list of IP address. Failed attempts generate an email notification.
Installation:
  1. Place main.py and definitions.py into an empty directory.
  2. Create the following files exactly as they appear:
	-server_info.csv
	-creds.csv
	-hosts.csv
	-email_recipients.csv
  3. Populate each file with the appropriate information (see bellow for more details).
  4. Run main.py

Configuration files:
server_info.csv
 Contains the address of the server being used to send the notifions and the port# that it's listening on. Create a single entry using the following syntax: "server_address,port#" (Ex - 10.1.1.254,587)

creds.csv 
Contains the login credentials for the server being used to send the notificaitons. For security reasons a private internal email server is recommended as well as an account being used souly to recieve these notifications. Create a single entry using the following syntax: "username,password".

hosts.csv 
Contains all the host IP address, descriptions, and location information. All of the hosts in this file will be tested for connectivity. Each entry must use the following syntax: "hostIP,description,location" (Ex - 10.1.1.254,Cisco Router,Bldg 6 MDF 101)

email_recipients.csv
Contains the email address of all the recipients that will get a notification when a connection fails. Simply add each email address separated by a comma (Ex - admin@company.net,net_admin@compay.net,sysadmin@company.net"

Default configurations:
-Connections are tested every 300 seconds (5min). To adjust it change the value of the variable periodicInterval = #

-checkPing() will attempt a connection 3 times before declaring it as failed. To adjust to number of attempts change the line containing "while(count < #):" so that # is equal to the number of desired attempts - 1.

-Once an issue occurs it will be tracked until the connection succeeds. By default an email alert for an issue being tracked will be sent every 60 minutes. To change the notification interval change the value of "email_notification_every" in main.py the integer specified is the number of seconds between notifiations.

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

			determine if its the first occurence, if false do:
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
		
				