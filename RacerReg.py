#file -- RacerReg.py --
#!/usr/bin/env python

from db_connection import get_db_connection, get_cursor
from pprint import pprint

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Functions related to RFID Pad and Registering Youth
# Should get moved to a separate Class
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Read RFID Card and return back pipe delimited view of what is on the card. 
############################################################################################################
def ReadCard(CardData):
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Car Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                print(str(id) + "\n" + text + "\n")
                OldText=text
                CardData = str(id) + "|" + text
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
    return CardData
## End def ReadCard()

############################################################################################################
## Read RFID Card and return back RFID only
############################################################################################################
def ReadRFIDCard(CardData):
    ## Read only RFID off of card
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Car Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                print(str(id) + "\n" + text + "\n")
                OldText=text
                CardData = str(id) 
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
    return CardData
## End def ReadCard()


############################################################################################################
## Register a new racer (Update card and Database) 
############################################################################################################
def RegisterRacer(CardData):
## Register a New Racer

    # Get the database connection
    db = get_db_connection()

    cursor = db.cursor(buffered=True)
    RFCardID = ReadRFIDCard( CardData )  
  
    print(RFCardID)
    
    ## At this point you should have a valid ID off of the card. 

    CarName = input('Car Name: ')
    RacerFirstName = input('Racer First Name: ')
    RacerLastName = input('Racer Last Name: ')
        
    ## Check if this RFID is already in Use in the Database
    sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from racerinfo WHERE RacerRFID= '"+ str(RFCardID) + "';"
    cursor.execute(sql)
    result = cursor.fetchone()

    if cursor.rowcount >= 1:
        print("RF ID Already Registered " + str(result[0]) + " "+ str(result[1]) + " " + str(result[2]) + " " + str(RFCardID) )
    else:
        ## RFID not already registered in the database so you can use it
        ## Write to the RFID Card the CarName and Racers Name
        reader.write(CarName + '|' + RacerFirstName + '|' + RacerLastName)
        print("Written")
    
        ## Now update the database 
        cursor = db.cursor()
        sql = "INSERT INTO racerinfo( RacerCarName, RacerFirstName, RacerLastName, RacerRFID) VALUES (%s, %s, %s, %s)" 
        print(str(RFCardID))
        val = (CarName, RacerFirstName, RacerLastName, str(RFCardID))
        cursor.execute(sql, val)
        db.commit()
        
        ## Verify that the insert worked
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from racerinfo WHERE RacerRFID= '"+ RFCardID + "';"
        cursor.execute(sql)
        result = cursor.fetchone()

        if cursor.rowcount >= 1:
            print("Welcome " + str(result[0]) + " "+ result[1] + " " + result[2] )
            print("Remove Car from PAD")
        else:
            print("User does not exist, something went wrong!")
        ## End if
        cursor.close()
    ## End if
## End RegisterRacer

############################################################################################################
## This routine will replace RFID in RacerInfo with a new RFID and will update all records in RaceResults that 
## had old RFID with the new RFID.
## This routine will get used when a car has lost its RFID tag and a new one is needed.
############################################################################################################
def LostRFIDCard():
## This routine will replace RFID in RacerInfo with a new RFID and will update all records in RaceResults that had old RFID with the new RFID.
## This routine will get used when a car has lost its RFID tag and a new one is needed.

    # Get the database connection
    db = get_db_connection()

    ## Get RFID from new tag
    NewRFID = readRFIDCard('False')
       
    ## Check if RFID is already in use
    sql = "SELECT * from racerinfo WHERE RacerRFID = '" + NewRFID['RacerRFID'] + "';" 
    
    cursor = db.cursor(buffered=True)
    cursor.execute(sql)
    
    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    cursor.close()
    pprint( result )
    xx = input("Do you wish to overwrite this card Y/N: ")
    ## Ask if you want to overwrite the card
    if xx == 'Y' or xx == 'y' :
        cursor = db.cursor(buffered=True)
        ## lookup database record
        ExistingRacer = lookupDBRacer()
        pprint( ExistingRacer )
        details = ExistingRacer[0]
        Racer = details['RacerID']
        sql = "UPDATE racerinfo SET RacerRFID = '" + str(NewRFID['RacerRFID']) + "' WHERE RacerID ='"+ str(Racer) + "';"
        cursor.execute(sql)
        sql = "UPDATE raceresults SET RacerRFID = '" + str(NewRFID['RacerRFID']) + "' WHERE RacerID ='"+ str(Racer) + "';"
        cursor.execute(sql)
        cursor.close()
        reader.write(str(details['RacerCarName']) + '|' + str(details['RacerFirstName']) + '|' + str(details['RacerLastName']))
        print("Written")
    
    ## End if check that card is to be overwritten

## End LostRFIDCard    


############################################################################################################
## Lookup racer record in the database.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results
## Can pass RacerID, RFID or will prompt for firstname / lastname 
############################################################################################################
def lookupDBRacer(display = 'True', **kwargs):
## Function to lookup a racer returns a list of dictionaries.
## if display = true then print results, otherwise just return results 
    # Get the database connection
    db = get_db_connection()
    if 'RacerRFID' in kwargs :
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, SUBSTRING(CONCAT_WS(' ', RacerFirstName, RacerLastName), 1, 18) AS FullName, RacerPack,RacerCarName, RacerRFID from racerinfo WHERE RacerRFID= '"+ kwargs['RacerRFID'] + "';"
    elif 'RacerID' in kwargs :
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, SUBSTRING(CONCAT_WS(' ', RacerFirstName, RacerLastName), 1, 18) AS FullName RacerPack,RacerCarName, RacerRFID from racerinfo WHERE RacerID= '"+ kwargs['RacerID'] + "';"
    else :
        RacerFirstName = input('Racer First Name: ')
        RacerLastName = input('Racer Last Name: ')
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, SUBSTRING(CONCAT_WS(' ', RacerFirstName, RacerLastName), 1, 18) AS FullName, RacerPack,RacerCarName, RacerRFID from racerinfo WHERE RacerFirstName= '"+ RacerFirstName + "' AND RacerLastName= '"+ RacerLastName + "';"
    ## end if kwargs
    
    cursor = db.cursor(buffered=True)
        
    ## Check if this Racer is Registered in the Database
    cursor.execute(sql)
    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    cursor.close()
    
    if display == 'True':
        pprint( result )
    ## end if
    return result
## end lookupDBRacer

############################################################################################################
## Read only RFID off the card
## if display = true then print results, otherwise just return results
## returns a dictionary of the card
############################################################################################################
def readRFIDCard(display = 'True'):
    ## Read only RFID off of card
    ## if display == true then print data, otherwise just return data
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Car Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                if display == 'True':
                    print(str(id) + "\n" + text + "\n")
                ## End if
                OldText=text            
                CardData = { 'RacerRFID' : str(id), 'cardtext' : text  }
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
    return CardData
## End def ReadCard()

############################################################################################################
## Full roster of all racers in the database.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results 
############################################################################################################   
def RacerRoster(display = 'True'):
    # Get the database connection
    db = get_db_connection()
    
    ## Revised Function to lookup a racer returns a list of dictionaries (One dictionary for each racer) 
    sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from racerinfo;"
    cursor = db.cursor(buffered=True)
        
    ## Check if this Racer is Registered in the Database
     ## print(sql)
    cursor.execute(sql)

    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    
    cursor.close()
    
    if display == 'True':
        pprint( result )
    ## end if show results or just return results
    
    return result
############################################################################################################
## Lookup Database Record based on RFID card on the reader.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results
############################################################################################################   
def FullLookup(display = 'True') :
    results = readRFIDCard(display)
    
    racerResults = lookupDBRacer('False', **results)
    if display == 'True' :
        pprint(results)
        pprint( racerResults )
    ## end if should display results    
    return racerResults

## end FullLookup


############################################################################################################
## create a dictionary for a new racer
## Note:  RacerDict is a misnomer, it is actually a LIST containing a DICT
############################################################################################################
def createRacer(display = "True", **kwargs):
    
    ## AppendList = { 'lane' : kwargs['lane'] }
    print("Put Car on Pad")
    RacerDict = []
    while 1:
        RacerDict=FullLookup(display)
        if len(RacerDict) == 0:  ## list is empty
            print(" RFID Not Found " )
            flashLEDS()          ## indicate that there is an error
        else:
            break   ## break out of while loop
        ## end if list from FullLookup is empty
    
    ## end while
           
    ## if 'lane' in kwargs :
        ## print("Lane :", kwargs['lane'])
    ##    AppendList = {'lane' : kwargs['lane']}
    ##    RacerDict.update(AppendList)
    if display == 'True':    
        pprint(RacerDict)
    ## end if display == True
    return RacerDict

############################################################################################################
## Lookup Race Statistics - RaceCounter, FastestTime, Fastest Lane etc.
## if display = true then print results, otherwise just return results
## Can pass Unit #, or will just lookup maxRacecounter if none specified 
############################################################################################################
## Note: If there are no records in raceresults or track heat for the specified unit this routines just 
## hangs!!!  -- BUG!!
############################################################################################################
def lookupRaceStats(display='True', **kwargs):
    # Get the database connection
    db = get_db_connection()

    if 'Unit' in kwargs:
        # Construct SQL query for a specific unit
        sql = "SELECT MAX(A.RaceCounter) AS RaceCounter, RIGHT(MIN(A.RaceTime), 9) AS RaceTime, B.Heat FROM raceresults A INNER JOIN trackheat B ON A.Unit = B.TrackID WHERE A.Unit = '"+ str(kwargs['Unit']) + "' AND A.RaceTime > 00 ;"
    else:
        # Construct SQL query to get the maximum RaceCounter when no specific unit is specified
        sql = "SELECT MAX(RaceCounter) AS RaceCounter from raceresults ;"

    # Get the cursor
    cursor = get_cursor(db)

    result = []

    try:
        # Execute the SQL query
        cursor.execute(sql)

        if cursor.rowcount >= 1:
            columns = tuple([d[0] for d in cursor.description])
            for row in cursor:
                result.append(dict(zip(columns, row)))
        else:
            print("No Data in RaceResults / Raceheat")
            result.append({'RaceCounter': '1', 'RaceTime': '0', 'Heat': '1'})
    except Exception as e:
        print("Error executing SQL query:", e)
    finally:
        # Always close the cursor and database connection
        cursor.close()
        db.close()

    if display == 'True':
        pprint(result)
    
    return result
## end lookupRaceStats
