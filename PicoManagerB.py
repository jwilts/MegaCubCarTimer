# PicoManagerB.py
#!/usr/bin/env python

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##	Version: 4
##  Date: Sept 27 /2023
##  -- Massive rewrite essentially a whole new program
##  - Have RFID pad to run on a Pico via sockets instead of directly connected
##  - Add option to use programmable LED Strip instead of individual LEDS
##  - Change from .ini file for settings to a .py instead
##  
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
## Notes:
## Code should work both with python2 and python3
## Program is designed to work with MariaDB Database 
##
## Relay is a future consideration to allow for secondary button on RF PAD to kick off relay.
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
## Turn on the debugger if the program is being stupid.
# import pdb; pdb.set_trace()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# Import necessary libraries
import mysql.connector
import os
import RPi.GPIO as GPIO
import time

# New 3rd party libraries for Version 4
import threading
import I2C_LCD_driver
import socket
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import *   ## notice lowercase 't' in tkinter here
import tkinter.font as tkFont

# Import custom modules
import RMSettings
import RacerReg
from db_connection import get_db_connection
import SocComms as SC
from SocComms import LatestRFID  # Import LatestRFID from SocComms
from SocComms import *

LcdYN = RMSettings.LCD_yn # Look and see if LCD should be used
if LcdYN.upper() == "Y":
    print("Loading LCD")
    import I2C_LCD_driver
    LCDAddress = RMSettings.LCD_Address

wsled = RMSettings.wsled_yn # Look and see what type of LED's should be used
if wsled.upper() == "Y":
    print("Loading WS LEDs")
    import ledLibrary as ledr
    from rpi_ws281x import PixelStrip, Color    
    strip.begin()
else :  ## Import legacy LED 
    print("Loading Legacy LEDs")
    import ledr 

# Create a global variable for the server socket
server_socket = None

# Create a global variable for the RFID list
from RMSettings import rfid_list

# Define root as a global variable
root = None
# Define root and RaceLog as global variables
root = None
RaceLog = None

# Setup Class for full Screen
class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.bind('<Escape>', self.toggle_geom)

        # Create a Text widget to display RFID tags
        self.rfid_display = tk.Text(master, wrap=tk.WORD, height=10, width=40)

        self.rfid_display.grid()
        self.master.after(100, self.update_rfid_display)  # Start updating the RFID display

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom

    def update_rfid_display(self):
        try:
            if RMSettings.rfid_list:
                rfid_tag = RMSettings.rfid_list.pop()  # Remove and get the last RFID tag in the list (LIFO)
                RaceLog.insert(0.0, f"{rfid_tag}\n")
                # self.rfid_display.insert(tk.END, f"{rfid_tag}\n")
                # self.rfid_display.see(tk.END)  # Scroll to the end
        except IndexError:
            pass
        self.master.after(100, self.update_rfid_display)  # Update every 100ms

def run_gui():
    global root, RaceLog  # Make root and RaceLog global variables
    root = tk.Tk()
    app = FullScreenApp(root)
    root.wm_title("Race Day")
    root.config(background="#FFFFFF")
    global circleCanvas
    global RCounter, LLane1, LLane2, LLane3
    
    # Configure a default font
    myfont = tk.font.Font(family='Helvetica', size=20, weight="bold")
    myfont2 = tk.font.Font(family='Helvetica', size=12, weight="bold")

    # Left Frame and its contents
    leftFrame = tk.Frame(root, width=1, height=1)
    leftFrame.grid(row=0, column=0, padx=2, pady=2)

    # Right Frame and its contents
    rightFrame = tk.Frame(root, width=1, height=1, relief=tk.RIDGE)
    rightFrame.grid(row=0, column=1, padx=10, pady=10)

    # Start filling the left frame
    tk.Label(leftFrame, text="Ready to Race", width=20, font=myfont, relief=tk.RIDGE).grid(columnspan=2, row=0,
                                                                                          column=0, padx=4, pady=2)

    # Create Ready to Race circleCanvas
    circleCanvas = tk.Canvas(leftFrame, width=100, height=100, bg='white')
    circleCanvas.grid(columnspan=2, row=1, column=0, padx=10, pady=2, sticky=tk.N)

    # Add Race counter
    tk.Label(leftFrame, text="Race Counter", width=20, font=myfont, relief=tk.RIDGE).grid(columnspan=2, row=2,
                                                                                            column=0, padx=2, pady=2)
    RCounter = tk.Text(leftFrame, width=5, height=1, takefocus=0, font=myfont2)
    RCounter.grid(columnspan=2, row=3, column=0, padx=2, pady=8)

    # Fastest Racer Today
    tk.Label(leftFrame, text="Fastest Time Today", width=20, font=myfont, relief=tk.RIDGE).grid(columnspan=2, row=4,
                                                                                                column=0, padx=10,
                                                                                                pady=1)

    tk.Label(leftFrame, text="Lane", font=myfont2).grid(row=5, column=0, padx=1, pady=1)
    FastestLane = tk.Text(leftFrame, width=12, height=1, takefocus=0, font=myfont2)
    FastestLane.grid(row=5, column=1, padx=2, pady=2)

    tk.Label(leftFrame, text="Time", font=myfont2).grid(row=6, column=0, padx=1, pady=1)
    FastestTime = tk.Text(leftFrame, width=12, height=1, takefocus=0, font=myfont2)
    FastestTime.grid(row=6, column=1, padx=2, pady=2)

    tk.Label(leftFrame, text="Race", font=myfont2).grid(row=7, column=0, padx=1, pady=1)
    FastestRace = tk.Text(leftFrame, width=12, height=1, takefocus=0, font=myfont2)
    FastestRace.grid(row=7, column=1, padx=2, pady=2)

    # Labels on Right Frame
    tk.Label(rightFrame, text="Current Race", width=20, font=myfont, relief=tk.RIDGE).grid(columnspan=2, row=0,
                                                                                            column=0, padx=2, pady=2)

    RaceLog = tk.Text(rightFrame, width=30, height=10, takefocus=0)
    RaceLog.grid(columnspan=2, row=14, column=0, padx=2, pady=2)

    # Create labels and inputs for the various Lanes
    tk.Label(rightFrame, text=" 1st", font=myfont).grid(row=5, column=0, sticky=tk.W, padx=2, pady=2)
    tk.Label(rightFrame, text="", font=myfont2).grid(row=4, column=1, sticky=tk.S, padx=2, pady=1)

    tk.Label(rightFrame, text=" 2nd", font=myfont).grid(row=7, column=0, sticky=tk.W, padx=2, pady=2)
    tk.Label(rightFrame, text="", font=myfont2).grid(row=6, column=1, sticky=tk.S, padx=2, pady=1)

    tk.Label(rightFrame, text=" 3rd", font=myfont).grid(row=9, column=0, sticky=tk.W, padx=2, pady=2)
    tk.Label(rightFrame, text="", font=myfont2).grid(row=8, column=1, sticky=tk.S, padx=2, pady=1)

    LLane1 = tk.Text(rightFrame, width=18, height=2, takefocus=0, font=myfont)
    LLane1.grid(row=5, column=1, sticky=tk.S, padx=10, pady=1)

    LLane2 = tk.Text(rightFrame, width=18, height=2, takefocus=0, font=myfont)
    LLane2.grid(row=7, column=1, sticky=tk.S, padx=10, pady=1)

    LLane3 = tk.Text(rightFrame, width=18, height=2, takefocus=0, font=myfont)
    LLane3.grid(row=9, column=1, sticky=tk.S, padx=10, pady=1)

    # Start the Tkinter main loop
    root.mainloop()

############################################################################################################
# Red Circle
############################################################################################################
def redCircle():
	circleCanvas.create_oval(10, 10, 80, 80, width=0, fill='red')
	root.update()

############################################################################################################
# Yellow Circle
############################################################################################################
def yelCircle():
	circleCanvas.create_oval(10, 10, 80, 80, width=0, fill='yellow')

############################################################################################################
# Green Circle
############################################################################################################
def grnCircle():
    circleCanvas.create_oval(10, 10, 80, 80, width=0, fill='green')
    # colorLog.insert(0.0, "Green\n")


# Define the Race class
class Race:
    def __init__(self, unit_number, racer_rfid, racer_id, racer_first_name, racer_last_name,
                 car_name, pack, lane_number, race_counter, place, finishing_time, FullName):
        self.UnitNumber = unit_number
        self.RacerRFID = racer_rfid
        self.RacerID = racer_id
        self.RacerFirstName = racer_first_name
        self.RacerLastName = racer_last_name
        self.CarName = car_name
        self.Pack = pack
        self.LaneNumber = lane_number
        self.RaceCounter = race_counter
        self.Place = place
        self.FinishingTime = finishing_time
        self.FullName = FullName
        
    def lookup_racer_by_lane(self, lane):
        if self.LaneNumber == lane:
            return {
                'UnitNumber': self.UnitNumber,
                'RacerRFID': self.RacerRFID,
                'RacerID': self.RacerID,
                'RacerFirstName': self.RacerFirstName,
                'RacerLastName': self.RacerLastName,
                'CarName': self.CarName,
                'Pack': self.Pack,
                'LaneNumber': self.LaneNumber,
                'RaceCounter': self.RaceCounter,
                'Place': self.Place,
                'FinishingTime': self.FinishingTime,
                'FullName': self.FullName
            }
        else:
            return None
        
        
    def update_racer_by_lane(self, lane, new_place, new_finishing_time):
        if self.LaneNumber == lane:
            self.Place = new_place
            self.FinishingTime = new_finishing_time
            return True
        else:
            return False

# Function to handle program exit
def exit_program():
    try:
        if 'db' in globals():
            db.close()
        if server_socket:
            server_socket.close()
        GPIO.cleanup()
        root.quit()
        print("Clean up and exit")
    except Exception as cleanup_error:
        print("Error during cleanup:", str(cleanup_error))

# Function to start the socket server in a separate thread
def start_socket_server():
    global server_socket
    server_host = "0.0.0.0"
    server_port = RMSettings.SERVER_PORT
    try:
        SC.start_server(server_host, server_port)
    except KeyboardInterrupt:
        print(f"Keyboard interrupt")
        exit_program()
    except Exception as e:
        print(f"Socket server error: {e}")
        traceback.print_exc()
        exit_program()

def init_program():
    ledr.resetLEDS()
    ledr.TurnRelayOff()
    ledr.testLEDS()
    ledr.flashLEDS()

def socket_server_and_mainloop():
    global mylcd, LoadLCD, Unit, db, server_socket, root, LatestRFID, MaxRaceTime  # Add LatestRFID to global variables
    global StartSwitch, Pad_Switch
    global RCounter
    global LaneOne, LaneTwo, LaneThree
    global LLane1, LLane2, LLane3

    # Get a database connection
    db = get_db_connection()
    cursor = db.cursor()
    UnitDetails = {'Unit': Unit}
    RaceStats = RacerReg.lookupRaceStats('True', **UnitDetails)
    details = RaceStats[0]
    RaceCounter = details['RaceCounter']
    Heat = details['Heat']

    # Create a thread for the socket server
    socket_server_thread = threading.Thread(target=start_socket_server)
    socket_server_thread.start()
    
    reset_CurrentLane()
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LaneOne,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(LaneTwo,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(LaneThree,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    
    GPIO.setup(Pad_Switch,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(StartSwitch,GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(GPIO_relay_1, GPIO.OUT)
    
    GPIO.add_event_detect(LaneOne, GPIO.RISING, bouncetime=track_switch_bounce_time)
    GPIO.add_event_detect(LaneTwo, GPIO.RISING, bouncetime=track_switch_bounce_time)
    GPIO.add_event_detect(LaneThree, GPIO.RISING, bouncetime=track_switch_bounce_time)
    
    GPIO.add_event_detect(Pad_Switch, GPIO.RISING, bouncetime = track_switch_bounce_time)
    GPIO.add_event_detect(StartSwitch, GPIO.RISING, bouncetime = TrackBounceTime) 
         
    # Big Loop
    while True:
                      
        if root is not None:  # Check if root is created
            root.update()
        print("Lane Count:" + str(lane_count) + "\n")
        
        Finishers = 0  # reset Finishers Count to zero
        
        RaceCounter +=1  # Increment Race Counter
        RCounter.delete(1.0, END)  #Clear out Race Counter on the GUI
        Msg = " " + str(RaceCounter)
        RCounter.insert(0.0, Msg)
        
        reset_CurrentLane() ## Reset Lane Counter
        
        # Create a new set of Race instances for the current race
        race_instances = []
        
        print ("Press start Button")
        RaceLog.insert(0.0, "Press Start\n")
        
        redCircle()
        root.update()

        ## wait for start button to be pushed
        ## At this point the switch on the track should get closed and cars get loaded.
        
        GPIO.wait_for_edge(StartSwitch, GPIO.RISING, bouncetime = TrackBounceTime )
        
        LLane1.delete(1.0, END)  #Clear out Lane1 Text
        LLane2.delete(1.0, END)  #Clear out Lane2 Text
        LLane3.delete(1.0, END)  #Clear out Lane3 Text
        root.update()
        SC.reset_latest_rfid()
        latest_rfid = None
                
        # Turn all LED's off
        ledr.resetLEDS()
        yelCircle()        
        while get_CurrentLane() <= lane_count:
            # Read RFID Tags from reader
            RaceLog.insert(0.0, "Scan Car\n")
            print ("Scan Car\n")
            # Loop through until valid RFID comes in
            while True:
                latest_rfid = SC.get_latest_rfid()
                if latest_rfid is not None:
                    print("Latest RFID:", str(latest_rfid) + "\n")
        
                    # Lookup racer details from the database
                    racer_details_list = RacerReg.lookupDBRacer(display='True', RacerRFID=str(latest_rfid))

                    # Check if the list is not empty
                    if len(racer_details_list) > 0:
                        RacerDetails = racer_details_list[0]
            
                        # Create a new instance of the Race class for each racer
                        current_race = Race(Unit, latest_rfid, RacerDetails['RacerID'], RacerDetails['RacerFirstName'], RacerDetails['RacerLastName'], RacerDetails['RacerCarName'], RacerDetails['RacerPack'], get_CurrentLane(), 1, 0, 0, RacerDetails['FullName'])
            
                        race_instances.append(current_race)
                                
                        RaceLog.insert(0.0, str(get_CurrentLane()) + ":" + str(latest_rfid) + "\n" )
                        SC.update_latest_rfid(None)
                        print( RacerDetails['FullName'] ) 
                        
                        if get_CurrentLane() == 1 :
                            # LLane1.delete(1.0, END)  #Clear out Lane1 Text
                            LLane1.insert(0.0, RacerDetails['FullName'])
                        if get_CurrentLane() == 2 :
                            # LLane2.delete(1.0, END)  #Clear out Lane2 Text
                            LLane2.insert(0.0, RacerDetails['FullName'])
                        if get_CurrentLane() == 3 :
                            # LLane3.delete(1.0, END)  #Clear out Lane2 Text
                            LLane3.insert(0.0, RacerDetails['FullName'])
                        break
                    else:
                        RaceLog.insert(0.0, "No Record Found\n" )
                        print("No Record:", str(latest_rfid) + "\n")
                        SC.update_latest_rfid(None)
                        ledr.flashLEDS()
                        # break
                    # end if check for no record found
                # end if check that RFID is not null           
                
            ## end while waiting for a RFID to come in            
            ledr.resetLEDS()
            ledr.LightLEDBank( int(get_CurrentLane() -1) )    
            increment_CurrentLane()  # Increment the lane counter
            time.sleep(0.1)
        # End While Current Lane < Lane Count
        
        # wait for clear button to be pushed on pad
        ## Need to write the code to do that
        
        # Now in a position to execute the race
        RaceLog.insert(0.0, "Race Start\n")
        
        GPIO.wait_for_edge(StartSwitch, GPIO.FALLING, bouncetime = TrackBounceTime )
        # Capture Race start time
        StartTime = time.monotonic() 
        grnCircle()
        root.update()
        RaceLog.insert(0.0, "Racers Away\n")
        LLane1.delete(1.0, END)
        LLane2.delete(1.0, END)
        LLane3.delete(1.0, END)
        root.update()
        
        ledr.flashLEDS()        
        # Race Started - Run Until Timeout or all 3 racers finished
        while (time.monotonic() - StartTime) < MaxRaceTime and Finishers < 4:
            if ( time.monotonic() - StartTime ) > ShortRaceTime:
                if GPIO.event_detected( LaneOne ):
                    for current_race in race_instances:
                        racer_data = current_race.lookup_racer_by_lane(1)
                        
                        if racer_data and racer_data.get("Place", 0) == 0:
                            Finishers = Finishers + 1
                            RaceTime = time.monotonic() - StartTime
                            current_race.update_racer_by_lane(1, new_place=Finishers, new_finishing_time=RaceTime)
                            ledr.LightPlace(0, Finishers)
                            msg = racer_data['FullName'] + "\n" + str(RaceTime)[0:7]
                            
                            if Finishers == 1 :
                                LLane1.insert(0.0, msg )
                            elif Finishers == 2 :
                                LLane2.insert(0.0, msg )
                            elif Finishers == 3 :
                                LLane3.insert(0.0, msg )
                                root.update
                                break
                            # end if

                    print("GPIO 1")
                                        
                if GPIO.event_detected( LaneTwo ):
                    for current_race in race_instances:
                        racer_data = current_race.lookup_racer_by_lane(2)
                        
                        if racer_data and racer_data.get("Place", 0) == 0:
                            Finishers = Finishers + 1
                            RaceTime = time.monotonic() - StartTime
                            current_race.update_racer_by_lane(2, new_place=Finishers, new_finishing_time=RaceTime)
                            ledr.LightPlace(1, Finishers)
                            msg = racer_data['FullName'] + "\n" + str(RaceTime)[0:7]

                            if Finishers == 1 :
                                LLane1.insert(0.0, msg )
                            elif Finishers == 2 :
                                LLane2.insert(0.0, msg )
                            elif Finishers == 3 :
                                LLane3.insert(0.0, msg )
                                root.update
                                break
                            # end if

                    print("GPIO 2")

                if GPIO.event_detected( LaneThree ):
                    for current_race in race_instances:
                        racer_data = current_race.lookup_racer_by_lane(3)
                        
                        if racer_data and racer_data.get("Place", 0) == 0:
                            Finishers = Finishers + 1
                            RaceTime = time.monotonic() - StartTime
                            current_race.update_racer_by_lane(3, new_place=Finishers, new_finishing_time=RaceTime)
                            ledr.LightPlace(2, Finishers)
                            msg = racer_data['FullName'] + "\n" + str(RaceTime)[0:7]

                            if Finishers == 1 :
                                LLane1.insert(0.0, msg )
                            elif Finishers == 2 :
                                LLane2.insert(0.0, msg )
                            elif Finishers == 3 :
                                LLane3.insert(0.0, msg )
                                root.update
                                break
                            # end if

                    print("GPIO 3")

                              
                root.update()
            
            # end if check for short race 
            
        # end while check for race timeout or all racers finished
       
        # Loop through all race instances and write Records to the Database
        for current_race in race_instances:
            RaceTime = current_race.FinishingTime
            Placing = current_race.Place
            RacerID = current_race.RacerID
            CarName = current_race.CarName
            RacerFirstName = current_race.RacerFirstName
            RacerLastName = current_race.RacerLastName
            Pack = current_race.Pack
            RacerRFID = current_race.RacerRFID

            # Assuming you have a cursor object from the database connection
            sql = "INSERT INTO raceresults (RaceCounter, Unit, Heat, Lane, RacerID, CarName, RacerFirstName, RacerLastName, Pack, RaceTime, Placing, RacerRFID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (str(RaceCounter), str(Unit), str(Heat), str(current_race.LaneNumber), str(RacerID), CarName, RacerFirstName, RacerLastName, str(Pack), str(RaceTime), str(Placing), str(RacerRFID))
    
            cursor.execute(sql, val)
            db.commit()
       
        RaceLog.insert(0.0, "Restarting Race\n")
                      
    
    ## End of Big Loop
    
    try:
        # Schedule the socket_server_and_mainloop function to run again after a delay (in milliseconds)
        if root is not None:  # Check if root is created
            root.after(1000, socket_server_and_mainloop)  # Re-schedule the function
    except KeyboardInterrupt:
        print("\nRaceCounter:", RaceCounter)
        exit_program()
    except Exception as e:
        print("An issue has been found:")
        print(str(e))
        traceback.print_exc()
        exit_program()

         
if __name__ == "__main__":
    # Load settings from RMSettings.py
    
    global LaneOne, LaneTwo, LaneThree
    global StartSwitch, Pad_Switch
    global Unit
    global MaxRaceTime
    global LaneOne, LaneTwo, LaneThree
    
    LaneOne = RMSettings.Lane1
    LaneTwo = RMSettings.Lane2
    LaneThree = RMSettings.Lane3
    MaxRaceTime = RMSettings.max_race_time
    ShortRaceTime = RMSettings.min_race_time
    Unit = RMSettings.unit
    RelayYN = RMSettings.relay_yn
    TrackBounceTime = RMSettings.track_switch_bounce_time
    track_switch_bounce_time = RMSettings.track_switch_bounce_time
    leds = RMSettings.leds
    leds = list(map(int, leds))
    LDRList = RMSettings.LDRList
    LDRList = list(map(int, LDRList))
    StartSwitch = RMSettings.GPIO_track_switch                      # Track Start Switch
    GPIO_relay_1 = RMSettings.GPIO_relay_1
    car_select_bounce_time = RMSettings.car_select_bounce_time
    Pad_Switch = RMSettings.GPIO_car_select_switch      # Pad Switches
    LcdYN = RMSettings.LCD_yn
    LCDAddress = RMSettings.LCD_Address
    lane_count = RMSettings.lane_count

    # Initialize the LCD if enabled
    if LcdYN == "Y":
        mylcd = I2C_LCD_driver.lcd()

    # Create a thread for the GUI
    gui_thread = threading.Thread(target=run_gui)

    # Start the GUI thread
    gui_thread.start()

    # Create a thread for the socket server and main loop
    socket_and_mainloop_thread = threading.Thread(target=socket_server_and_mainloop)

    # Start the socket server and main loop thread
    socket_and_mainloop_thread.start()