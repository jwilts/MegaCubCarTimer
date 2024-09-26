#file -- Registration.py --
#!/usr/bin/env python

############################################################################################################
##	Version: 4
##  Date: Feb 3/2023
##   Change mySQL connector to MariaDB
##  
############################################################################################################
##	Version: 3
##  Date: Feb 3/2022
##   Add lookup number of races for a Racer based on RFID Tag
##   Add support for mini LCD screen
##  
############################################################################################################
##	Version: 2
##  Date: Nov 26/2021
##  Pull database connection details from settings file
##  This application utilizes an RC-522 RFID pad and a mariaDB database to do basic registration for 
##  cubcar races.  The program checks to see if the Youth and or RFID is already in use in the database 
##  before creating a shell of a record.   
##  
############################################################################################################
##  Note: Version 2 does some better handling for the RFID tags (Better prompting)
## 
#############################################################################################################

import argparse
import logging
# import mysql.connector
import mariadb 
import os
from pprint import pprint
import re
import RPi.GPIO as GPIO
import sys
import time
from mfrc522 import SimpleMFRC522

import I2C_LCD_driver

import configparser

import pandas as pd  ## Note -- This causes the VERY slow load times

GPIO.setwarnings(False)
reader = SimpleMFRC522()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
## Turn on the debugger if the program is being stupid.
## import pdb; pdb.set_trace()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Config File Routines
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Create a config file
## NOTE:  This is here for reference, not used by the program
############################################################################################################
def create_config(path):
    if sys.version_info[0] == 3:
        # for Python3
        config = configparser.configparser()

    else:
        # for Python2
        config = ConfigParser.ConfigParser()

    config.add_section("Settings")
    config.set("Settings", "max_race_time", "")
    config.set("Settings", "min_race_time", "")
    config.set("Settings", "GPIO_relay_1", "")
    config.set("Settings", "GPIO_track_switch","")
    config.set("Settings", "track_switch_bounce_time", "")
    config.set("Settings", "GPIO_car_select_switch", "")
    config.set("Settings", "car_select_bounce_time", "")
    config.set("settings", "Leds","")
    config.set("Settings", "GPIO_ldr_lane_1", "")
    config.set("Settings", "GPIO_ldr_lane_2", "")
    config.set("Settings", "GPIO_ldr_lane_3", "")
    config.set("settings", "Unit","")
    config.set("settings", "Matrix_YN","")
    config.set("settings", "relay_yn","")
    config.set("settings", "LCD_yn","")
    config.set("settings", "LCD_Address","")

    config.set("dbase", "use_database_YN", "")
    config.set("dbase", "Host", "")
    config.set("dbase", "User", "")
    config.set("dbase", "Passwd", "")
    config.set("dbase", "Database", "")

    config.set("Races", "GFastestLane", "")
    config.set("Races", "GFastestTime", "")
    config.set("Races", "GFastestRaceCounter", "")
    config.set("Races", "race_counter","")
    config.set("Races", "Heat","")
    with open(path, "wb") as config_file:
        config.write(config_file)

############################################################################################################
## Return a Config object
############################################################################################################
def get_config(path):
    if not os.path.exists(path):
        create_config(path)

    if sys.version_info[0] == 3:
        # for Python3
        config = configparser.ConfigParser()

    else:
        # for Python2
        config = ConfigParser.ConfigParser()

    config.read(path)
    return config

############################################################################################################
## Return a Setting and Optionally Print to screen for debugging purposes
############################################################################################################
def get_setting(path, section, setting, diplay):
    config = get_config(path)
    value = config.get(section, setting)
    if diplay == True:
        print(" %r, %r, %r" % (section, setting, value))
    return value

############################################################################################################
## Read an Array delimited by commas
############################################################################################################
def get_setting2(path, section, setting, diplay):
    config = get_config(path)
    value = config.get(section, setting).split(',')

    if diplay == True:
        print(" %r, %r, %r" % (section, setting, value))
    return value

############################################################################################################
## Update a Setting
############################################################################################################
def update_setting(path, section, setting, value):
    config = get_config(path)
    config.set(section, setting, str(value))
    with open(path, "wb") as config_file:
        config.write(config_file)
############################################################################################################
## Delete a Setting
############################################################################################################
def delete_setting(path, section, setting):
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "wb") as config_file:
        config.write(config_file)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  Load .INI settings into globals
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

############################################################################################################
## Configuration Information
############################################################################################################
path = "RMsettings.ini"

############################################################################################################
## GPIO Information
############################################################################################################
LcdYN = str(get_setting(path, 'Settings', 'LCD_yn', True))
LCDAddress = str(get_setting(path, 'Settings', 'LCD_Address', True))

############################################################################################################
## Database Information
############################################################################################################
DBaseYN = str(get_setting(path, 'dbase', 'use_database_YN', True))
    
## db = mysql.connector.connect(
## host= get_setting(path, 'dbase', 'host', False),
## user= get_setting(path, 'dbase', 'user', False),
## passwd= get_setting(path, 'dbase', 'passwd', False),
##database=get_setting(path, 'dbase', 'database', True)
## ) 

db = mariadb.connect(
    host= get_setting(path, 'dbase', 'host', False),
    user= get_setting(path, 'dbase', 'user', False),
    passwd= get_setting(path, 'dbase', 'passwd', False),
    database=get_setting(path, 'dbase', 'database', True)
)

# cursor = db.cursor(buffered=True) ## for Database Interactions

OldText = ''                            ## Used to Check that the text on the card has changed
NoCarFlag = 'N'                         ## Used to only display message No Car Found once

MenuText = "1. Read RFID Card \n"
MenuText = MenuText + "2. Lookup Cub Record From Database \n"
MenuText = MenuText + "3. Register New Racer \n"
MenuText = MenuText + "4. Lost RFID Card \n"
MenuText = MenuText + "5. Update Heat \n"
MenuText = MenuText + "6. Update Racer information \n"
MenuText = MenuText + "7. Roster \n"
MenuText = MenuText + "8. Use RFID Lookup DB \n"
MenuText = MenuText + "9. Erase Card \n"
MenuText = MenuText + "10. Race Summary \n"
MenuText = MenuText + "11. Looping Race Summary \n"
MenuText = MenuText + "12. Exit \n"

def Main():
    os.system('clear')  
    print( 30 * "-", "MENU", 30 * "-")
    print( MenuText)
    print( 67 * "-")
## end def Main()

############################################################################################################
## Register a new racer (Update card and Database) 
##
############################################################################################################
def RegisterRacer(display = 'True'):
## Register a New Racer

    cursor = db.cursor(buffered=True)
    
    while 1: 
        RFCardID = readRFIDCard( display )  

        ## Check to see if this RFID is already registered in the database

        ## Check if this RFID is already in Use in the Database
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerCarClass from racerinfo WHERE RacerRFID= '"+ str(RFCardID) + "';"
        sql2 = "SELECT ID, PackName from packnames ;"
        ## print( sql ) 
        cursor.execute(sql)
        result = cursor.fetchone()
        if cursor.rowcount >= 1:
            print("RF ID Already Registered Pick Another " + str(result[0]) + " "+ str(result[1]) + " " + str(result[2]) + " " + str(RFCardID) )
            input('Press Enter')
        else :
            ## RFID is not already in use so this one can be used
            break
        ## end if

    ## End while
    
    ## At this point you should have a valid ID off of the card. 
    
    cursor = db.cursor(buffered=True)
        
    cursor.execute(sql2)

    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
        print(row)	
    cursor.close()
    
    GroupID = input('Group ID:')    
    CarName = input('Car Name:')
    RacerFirstName = input('Racer First Name:')
    RacerLastName = input('Racer Last Name:')
        
    print("Make sure Tag is on PAD")
    ## RFID not registered in the database so you can use it
    ## Write to the RFID Card the CarName and Racers Name
    reader.write(CarName + '|' + RacerFirstName + '|' + RacerLastName)
    print("Written")

    ## Now update the database 
    cursor = db.cursor()
    sql = "INSERT INTO racerinfo( RacerCarName, RacerFirstName, RacerLastName, RacerRFID, RacerPack) VALUES (%s, %s, %s, %s, %s)" 
    # print(str(RFCardID))
    val = (CarName, RacerFirstName, RacerLastName, str(RFCardID), GroupID)
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
    cursor.close()
    ## End if

## End RegisterRacer

############################################################################################################
## This routine will replace RFID in RacerInfo with a new RFID and will update all records in RaceResults that had old RFID with the new RFID.
## This routine will get used when a car has lost its RFID tag and a new one is needed.
############################################################################################################
def LostRFIDCard():
## This routine will replace RFID in RacerInfo with a new RFID and will update all records in RaceResults that had old RFID with the new RFID.
## This routine will get used when a car has lost its RFID tag and a new one is needed.

    ## Get RFID from new tag
    NewRFID = readRFIDCard('False')
    
    ## print(NewRFID['RacerRFID'])
    
    ## Check if RFID is already in use
    sql = "SELECT * from racerinfo WHERE RacerRFID = '" + NewRFID['RacerRFID'] + "';" 
    
    ## Add a check to see if records also exist in RaceResults
    ## ADD HERE
    
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
    if xx.upper() == 'Y':
        cursor = db.cursor(buffered=True)
        ## lookup database record
        ExistingRacer = lookupDBRacer()
        pprint( ExistingRacer )
        details = ExistingRacer[0]
        Racer = details['RacerID']
        sql = "UPDATE racerinfo SET RacerRFID = '" + str(NewRFID['RacerRFID']) + "' WHERE RacerID ='"+ str(Racer) + "';"
        cursor.execute(sql)
        db.commit()
        sql = "UPDATE raceresults SET RacerRFID = '" + str(NewRFID['RacerRFID']) + "' WHERE RacerID ='"+ str(Racer) + "';"
        cursor.execute(sql)
        db.commit()
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
    if 'RacerRFID' in kwargs :
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from racerinfo WHERE RacerRFID= '"+ kwargs['RacerRFID'] + "';"
    elif 'RacerID' in kwargs :
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from racerinfo WHERE RacerID= '"+ kwargs['RacerID'] + "';"
    else :
        RacerFirstName = input('Racer First Name:')
        RacerLastName = input('Racer Last Name:')
        sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from racerinfo WHERE RacerFirstName= '"+ RacerFirstName + "' AND RacerLastName= '"+ RacerLastName + "';"
    ## end if kwargs
          
    ## Assemble a dictionary to return as result set
    ## Check if this Racer is Registered in the Database
    cursor = db.cursor(buffered=True)
    cursor.execute(sql)
    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    y = 0
    for row in cursor:
        result.append(dict(zip(columns, row)))
        y = y + 1  ## Check to stop pandas from barfing
    # End for loop
    cursor.close()
    
    ## Create Panda frame if display = True
    if (display == 'True') :
        if (y > 0) :
            db_cursor = db.cursor(buffered=True)
            db_cursor.execute(sql)

            table_rows = db_cursor.fetchall()

            df = pd.DataFrame(table_rows)

            df.columns = [ 'RacerID','First Name','Last Name', 'Pack', 'Car Name','RFID' ]
            print (df.to_string(index = False))

            db_cursor.close()    
        else :  ## No rows in the cursor
            print("\n No DB Records Found")
        ## end else
        
    ## EndIf display == True
    
    return result
## end lookupDBRacer

############################################################################################################
## Read only RFID off the card
## if display = true then print results, otherwise just return results
## returns a dictionary of the card
############################################################################################################
def readRFIDCard(display = 'True'):
    ## Read only RFID off of card
    ## if display == true then print data, otherwise just return ID
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_display_string("Place Card ", 1)
    mylcd.lcd_display_string("On Pad ", 2)
    
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
            mx = int(hex(id)[2:-2], 16)  ## strip off leading 0x and last two digits and convert back to integer
            id = mx
            if text != OldText:
                if display == 'True':
                    mylcd.lcd_clear()
                    print(str(id) + "\n" + text + "\n")
                    mylcd.lcd_display_string(str(id), 1)
                    mylcd.lcd_display_string(text[:16], 2)  ## only display 16 char 
                else :
                    mylcd.lcd_clear()
                ## End if
                OldText=text            
                CardData = str(id)
                # CardData = { 'RacerRFID' : str(id), 'cardtext' : text  }
                NoCarFlag = 'N'
                break;
            else:
                print ("Same car")
            ## End If
        ## End If    
    ## End while loop waiting for card
          
    return CardData
## End def readRFIDCard()

############################################################################################################
## Read RFID Data off the card
## if display = true then print results, otherwise just return results
## returns a dictionary of the card
############################################################################################################
def READRFIDCard(display = 'True'):
    ## Read RFID Data off of card
    ## if display == true then print data, otherwise just return data
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_display_string("Place Card ", 1)
    mylcd.lcd_display_string("On Pad ", 2)
    print("\n Place RFID tag on PAD")
    CardData = ""
    OldText = ""
    while True:             ## Read ID off of car
        status,TagType = reader.read_no_block()
        # print(status)
        if status == 'None':
            ## only print "No Card Found" Once
            if NoCarFlag == 'N':
                print ("No Car Found")
            NoCarFlag = 'Y'        
        elif status != 'None':
            id,text = reader.read()
            mx = int(hex(id)[2:-2], 16)  ## strip off leading 0x and last two digits and convert back to integer
            id = mx
            if text != OldText:
                if display == 'True':
                    print(str(id) + "\n" + text + "\n")
                    mylcd.lcd_clear()
                    mylcd.lcd_display_string(str(id), 1)
                    mylcd.lcd_display_string(text[:16], 2)  ## only display 16 char              
                else :
                    mylcd.lcd_clear()
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
## UserRoster2 - Version using Pandas
############################################################################################################   
def RacerRoster2(display = 'True'): 
    sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from racerinfo;"    
    # print(sql)
        
    db_cursor = db.cursor(buffered=True)
    db_cursor.execute(sql)

    table_rows = db_cursor.fetchall()

    df = pd.DataFrame(table_rows)

    df.columns = [ 'RacerID','First Name','Last Name', 'Pack', 'Car Name','RFID' ]
    print (df.to_string(index = False))

    db_cursor.close()    

    return df

## end UserRoster2


############################################################################################################
## Full roster of all racers in the database.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results 
############################################################################################################   
def RacerRoster3(display = 'True'):
    ## prints roster 
    sql = "SELECT RacerID, RacerFirstName, RacerLastName, RacerPack,RacerCarName, RacerRFID from racerinfo;"
    cursor = db.cursor(buffered=True)
        
    ## Check if this Racer is Registered in the Database
    ## print(sql)
    cursor.execute(sql)
    for row in cursor:
        print(row)
    cursor.close()
        
    return 1

############################################################################################################
## Lookup Database Record based on RFID card on the reader.
## as there may be multiple records returns a list of dictionaries for all results found.
## if display = true then print results, otherwise just return results
############################################################################################################   
def FullLookup(display = 'True') :
    results = READRFIDCard('False')
    
    racerResults = lookupDBRacer('False', **results)
    if display == 'True' :
       # pprint(results)
        pprint( racerResults )
    ## end if should display results    
    return racerResults

## end FullLookup

############################################################################################################
## New Heat 
############################################################################################################
def NewHeat():
## Register a New Heat for a particular track

    cursor = db.cursor(buffered=True)
    Heat = input('Heat Number: ')
    Unit = input('Track ID : ')
           
    ## Delete any records for this given track  
    cursor = db.cursor()
    sql1 = "DELETE FROM TrackHeat WHERE TrackID = '" + str(Unit) + "';"
    cursor.execute(sql1)
    db.commit()
    
    sql2 = "INSERT INTO TrackHeat( [Heat], [Unit]) VALUES (%s, %s)" 
    val2 = (Heat, Unit)
    cursor.execute(sql2, val2)
    db.commit()
    
    cursor.close()
    print("Restart Track timer to take effect!")
    
## End NewHeat

############################################################################################################
## Lookup Race Statistics - RaceCounter, FastestTime, Fastest Lane etc.
## if display = true then print results, otherwise just return results
## Can pass Unit #, or will just lookup maxRacecounter if none specified 
############################################################################################################
## Unit = 1
## UnitDetails = { 'Unit' : Unit }
## RaceStats =  lookupRaceStats( 'True', **UnitDetails )
## details = RaceStats[0]
## RaceCounter = details['RaceCounter']
## Heat = details['Heat']
###########################################################################################################
def lookupRaceStats(display = 'True', **kwargs):
## if display = true then print results, otherwise just return results 
    if 'Unit' in kwargs :
        sql = "SELECT MAX(A.RaceCounter) AS RaceCounter, RIGHT( MIN(A.RaceTime), 9) AS RaceTime, B.Heat FROM raceresults A INNER JOIN	trackheat B	ON A.Unit = B.TrackID WHERE A.Unit = '"+ str(kwargs['Unit']) + "' AND A.RaceTime > 00 ;"
    
    else :
        sql = "SELECT MAX(RaceCounter) As RaceCounter from RaceResults ;"
    ## end if kwargs
    
    cursor = db.cursor(buffered=True)
        
    ## Return race statistics in a list of dictionaries. (Should only be 1 row)
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
## end lookupRaceStats

############################################################################################################
## Wipe out data on card, update database
## if display = true then print results, otherwise just return results
############################################################################################################   
def EraseCardData(display = 'True') :
    results = readRFIDCard(display)
    while 1:
        xx = '0'
        mylcd = I2C_LCD_driver.lcd()
        mylcd.lcd_display_string("Erase Card ", 1)
        mylcd.lcd_display_string("Y/N: ", 2)

        xx = input("Are you sure you want to blank this RFID Tag Y/N?")
    
        if xx.upper() == "Y":
            ## Erase Card
            mylcd.lcd_display_string("PUT RFID TAG ", 1)
            mylcd.lcd_display_string("ON PAD", 2)
            print("Make sure Tag is on PAD")
            
            sql = "UPDATE racerinfo SET RacerRFID = '' WHERE RacerRFID LIKE '"+ str(results) + "';"
            sql2 = "UPDATE raceresults SET RacerRFID = '' WHERE RacerRFID LIKE '"+ str(results) + "';"
            # print(sql)
            # print(sql2)
            cursor = db.cursor(buffered=True)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            cursor = db.cursor(buffered=True)
            cursor.execute(sql2)
            db.commit()
            cursor.close()
            reader.write('')     
            mylcd.lcd_display_string("RFID BLANKED    ", 1)
            mylcd.lcd_display_string("                ", 2)
            print("Erased")
            break
        elif xx.upper() == "N":
            break
        else :
            print("I dont understand your choice")
        # endif
    # end while
    mylcd.lcd_clear()
   
    
## end EraseCard

############################################################################################################
## Display a count of how many races a cub has run on each track
############################################################################################################   
def RacerSummary(display = 'True') :
    
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_clear()
    results = readRFIDCard('True')
    sql = "SELECT HeatTrackCount FROM LCDViewAgg WHERE RacerRFID ='" + str(results) + "' ;"

    sql2 = "SELECT RaceCounter, Unit, Heat, Lane, Placing, RIGHT(RaceTime,9) FROM raceresults WHERE RacerRFID ='" + str(results) + "' ORDER BY Heat, Unit, RaceCounter ;"

    cursor = db.cursor(buffered=True)
    cursor.execute(sql)

    mylcd.lcd_clear()
    y = 1
    for row in cursor:
        # print(row)
        print(y,row[0])
        # mylcd.lcd_display_string(row[0], 1, 0)
        mylcd.lcd_display_string(row[0], y, 0)
        y = y+1
    cursor.close()
    
        ## Create Panda frame if display = True
    if (display == 'True') :
        if (y > 1) :
            db_cursor = db.cursor(buffered=True)
            db_cursor.execute(sql2)

            table_rows = db_cursor.fetchall()

            df = pd.DataFrame(table_rows)

            df.columns = [ 'RaceCounter','Unit','Heat', 'Lane', 'Placing','RaceTime' ]
            print (df.to_string(index = False))

            db_cursor.close()    
        else :  ## No rows in the cursor
            print("\n No DB Records Found")
        ## end else
                
    ## EndIf display == True
        
    return results
    
## end RacerSummary
    
###################################################################################################################
## Begin Main part of the program
###################################################################################################################

while 1:
        
    CardData = ""
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_clear()
    Main()
    xx = '0'
    xx = input("Enter Your Choice: ")
    
    if xx == "12":
        break
    elif xx == "11":
        while 1:
            RacerSummary('True')
            time.sleep(10)
            os.system('clear')    
    elif xx == "10":
        RacerSummary('True')
        input("Press Enter")
    elif xx == "9":
        EraseCardData('True')
        input("Press Enter")
    elif xx == "8":
        FullLookup('True')
        input("Press Enter")
    elif xx == "7":
        # pprint(RacerRoster3('False'))
        RacerRoster2('True')
        input("Press Enter")
    elif xx == "6":
        ## UpdateRacerInfo()
        print("You are wildly optimistic if you think this function was written yet")
        input("Press Enter")
    elif xx == "5":
        NewHeat()
        input("Press Enter")
    elif xx == "4":
        LostRFIDCard()
        input("Press Enter")
    elif xx == "3":
        RegisterRacer('True')
        input("Press Enter")
    elif xx == "2":
        results = lookupDBRacer('True')
        ## pprint( results )
        input("Press Enter")
    elif xx == "1":
        results = readRFIDCard('True')
        pprint( results )
        input("Press Enter")
    else:
        print("I don't understand your choice.")  
    ## end if
       
## End While


