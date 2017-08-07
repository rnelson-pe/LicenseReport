# ---------------------------------------------------------------------------
# LicenseMonitor.py
# Created on: Thu Jun 27 2011
# Author: Jeff Mitzelfelt
# Purpose: Monitor ArcGIS Licenses using the lmutil lmstat -a command and load
#   information into a SQL Server Database
# Modified on: Feb 13, 2013
#   Modified the code to allow for system to interrogate multiple license
#   managers by IP address. Command can be run on a machine with the license
#   manager installed but not hosting any licenses.
# Command Line: LicenseMonitor.py 10.10.10.99 10.10.20.100 ...
# ---------------------------------------------------------------------------

# Import system modules
import os, re, datetime, sys, getopt

# Regular Expressions
regLicenseType = re.compile(r"(Users of)(.+): .\(Total of (\d+) .+\Total of (\d+)")
regUserRecord = re.compile(r"^\s+(\S+) (\S+) .+\(v(\d{1,2}[\.\d+]*)\) .+, start \w+ (\d+)/(\d+) (\d+):(\d+)")
regQuoteCheck = re.compile(r"'")

# Copied from http://answers.oreilly.com/topic/318-how-to-match-ipv4-addresses-with-regular-expressions/
regIpAddress = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

# Local Variables

currTime = datetime.datetime.now().replace(microsecond=0)

LicenseManagerDirectory = os.getcwd()

def swapLic(lic):
    swap = {'Info':'Advanced',
            'Editor':'Standard',
            'Viewer':'Basic',
            'Publisher':'Publisher',
            'Grid':'Spatial Analyst',
            'Network':'Network Analyst'}

    rt = lic
    if lic in swap:
        rt = swap[lic]
    
    return rt

def getLmutilOutput(lmutilDirectory, licenseManagerAddress):
    currentDirectory = os.getcwd()
    command = 'lmutil lmstat -a'
    commandTail = ' -c @' + licenseManagerAddress
    # Change to lmutilDirectory
    os.chdir(lmutilDirectory)
    # Execute lmutil command
    commandOut = os.popen(command + commandTail,'r').readlines()
    # Change to currentDirectory
    os.chdir(currentDirectory)
    return commandOut

def parseLmutilData(inString):
    #Parse lmutil output
    outputArray = []
    for line in inString:
        line = regQuoteCheck.sub("''",line)
        # Get Line that shows License Type
        testText = regLicenseType.match(line)

        if testText:
            productName = testText.group(2).strip()
            LicenseStatus = testText.group(4) + ' of ' + testText.group(3)

        # Get Line that contains User Information
        testText = regUserRecord.search(line.replace('ACTIVATED LICENSE(S)','BORROWED'))
        if testText:


            # Extract User Information into variables
            userCredential = testText.group(1)
            machineName =  testText.group(2)
            softwareVersion = testText.group(3)
            startTime = datetime.datetime( \
                currTime.year - (1 if (currTime.month > int(testText.group(4))) else 0) , \
                int(testText.group(4)), \
                int(testText.group(5)), \
                int(testText.group(6)), \
                int(testText.group(7)))
            sessionInfo = [productName, userCredential, machineName, softwareVersion, startTime, LicenseStatus]
            outputArray += [sessionInfo]


    return outputArray



def storeLmutilData(inArray):
    # Database Connection Setup
    #cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=ServerNameOrIP;DATABASE=DatabaseName;UID=UserId;PWD=Password')
    #cursor = cnxn.cursor()
                         
##    for record in inArray:
##        # Stored Procedure SQL Command Setup and Execution
##        storedProcedure = 'EXEC spSessionUpdateWithVersion ' + \
##            '@ProductName = \'' + record[0] + '\', ' + \
##            '@ScriptTime = \'' + str(currTime) + '\', ' + \
##            '@UserCredential = \'' + record[1] + '\', ' + \
##            '@MachineName = \'' + record[2] + '\', ' + \
##            '@StartTime	= \'' + str(record[4]) + '\', ' + \
##            '@SoftwareVersion = \'' + record[3] + '\''
        #cursor.execute(storedProcedure)
    
    print '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SUMMARY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print ' %-15s %-12s %-10s %-15s %-15s %-10s %-25s %-25s' % ('LICENSE','ORIG LIC','COUNT','USER','MACHINE','VERSION','CHECK OUT','TIMESTAMP')
    for record in inArray:

        #print 'License: {0};|User: {2};|Machine: {3};   StartTime: {4}; SoftwareVersion: {5};   Timestamp: {1}'.format(record[0],str(currTime),record[1],record[2],record[4],record[3])
        print ' %-15s %-12s %-10s %-15s %-15s %-10s %-25s %-25s' % (swapLic(record[0]),record[0], record[5],record[1],record[2],record[3],str(record[4]),str(currTime))


    # Commit record changes and close database connection
##    cnxn.commit()
##    cursor.close()
##    cnxn.close()

# Load Options and Arguments from command line
#opts, args = getopt.getopt(sys.argv[1:],0)

opts = []
args = ['10.1.252.111']


for element in args:

    # test that command line argument is a valid IP address
    testIp = regIpAddress.search(element)
    
    # IP address is valid
    print '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ VERBOSE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    if testIp:
        output = getLmutilOutput(LicenseManagerDirectory, element)
        #print output
        for i in output:
            #print i
            if not i.isspace():
                print i.replace('\n','')
        userArray = parseLmutilData(output)

        # Test that licenses are used
        if len(userArray)>0:
            # Store license use data
##            userArray = []            
##            for i in fullArray:
##                if i not in userArray:
##                    userArray.append(i)
            storeLmutilData(userArray)

    # IP address is invalid
    else:
        print element + ' is an invalid IP address'
