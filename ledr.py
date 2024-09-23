# LEDR.py
#!/usr/bin/env python

## Classic LED functions where each LED is independently controlled off of a GPIO

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
##  LED & Relay related functions
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

import RMSettings
import RPi.GPIO as GPIO
import time
from rpi_ws281x import Color

############################################################################################################
## Configuration Information from RMSettings.py
############################################################################################################
RelayYN = RMSettings.relay_yn
leds = RMSettings.leds
leds = list(map(int, leds))         ## Fix leds so that it is an array of integers
GPIO_relay_1 = RMSettings.GPIO_relay_1

############################################################################################################
# Reset LED's to an off state
############################################################################################################
def resetLEDS():
	x = 0
	while x < len(leds):
		GPIO.setup(leds[x],GPIO.OUT)
		GPIO.output(leds[x],GPIO.LOW)
		x +=1

############################################################################################################
# Run test cycle of the LEDs
############################################################################################################
def testLEDS(color=Color(255, 0, 0)):
    x = 0
    while x < len(leds) :
        GPIO.setup(leds[x],GPIO.OUT)
        GPIO.output(leds[x],GPIO.LOW)
        x +=1

        # Run test cycle of the LEDs
        x = 0
        while x < len(leds):
            GPIO.setup(leds[x],GPIO.OUT)

            GPIO.output(leds[x],GPIO.HIGH)
            time.sleep(0.03)
            # GPIO.output(leds[x],GPIO.LOW)
            x +=1
        time.sleep(0.03)
        x = 0

        # Turn LED's Off
        while x < len(leds):
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.LOW)
            x +=1

############################################################################################################
# 3 quick flashes of the LEDS
############################################################################################################
def flashLEDS(color=Color(255, 0, 0)) :

	x = 0
	y = 0
	while y < 3:
		while x < len(leds):
			GPIO.setup(leds[x],GPIO.OUT)
			GPIO.output(leds[x],GPIO.HIGH)
			x +=1
		time.sleep(0.03)
		resetLEDS()
		time.sleep(0.1)
		x=0
		y +=1

############################################################################################################
# Light all LED's in the bank
############################################################################################################
def lightLEDS(color=Color(255, 0, 0)) :

	x = 0
	y = 0
	while y < len(leds):
		while x < len(leds):
			GPIO.setup(leds[x],GPIO.OUT)
			GPIO.output(leds[x],GPIO.HIGH)
			x +=1
		x=0
		y +=1


############################################################################################################
# Light all LED's in specified bank
############################################################################################################
def LightLEDBank(LightBank, color=Color(255, 0, 0)) :

    if LightBank == 0:
        x = 0
        while x < 3:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1

    elif LightBank == 1:
        x = 3
        while x < 6:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1

    elif LightBank == 2:
        x = 6
        while x < 9:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1
    else:
        print("Whoops")

############################################################################################################
# Light a specific place in a specific light bank`
############################################################################################################
def LightPlace(LightBank, Place, color=Color(255, 0, 0)):
    if LightBank == 0:
        x = 0
        while x < Place:
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1

    elif LightBank == 1:
        x = 3
        while x < (Place + 3):
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1

    elif LightBank == 2:
        x = 6
        while x < (Place + 6):
            GPIO.setup(leds[x],GPIO.OUT)
            GPIO.output(leds[x],GPIO.HIGH)
            x +=1
    else:
        print("Whoops")

############################################################################################################
# Turn off Relay
############################################################################################################
def TurnRelayOff() :

    GPIO.output(GPIO_relay_1,GPIO.LOW)

############################################################################################################
# Turn On Relay
############################################################################################################
def TurnRelayOn() :

    GPIO.output(GPIO_relay_1,GPIO.HIGH)

############################################################################################################
# Turn On Relay for a fixed duration (Sleep)
# Caution with this as you can miss events that happen during sleep
############################################################################################################
def PulseRelay(duration) :

    GPIO.output(GPIO_relay_1,GPIO.HIGH)
    sleep(duration)
    GPIO.output(GPIO_relay_1,GPIO.LOW)


def testRelays():
    while True:
        print("Relay Test Menu:")
        print("1. Turn Relay ON")
        print("2. Turn Relay OFF")
        print("3. Pulse Relay")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            TurnRelayOn()
        elif choice == '2':
            TurnRelayOff()
        elif choice == '3':
            duration = float(input("Enter duration for pulsing relay (in seconds): "))
            PulseRelay(duration)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

# Define a function to show the main test menu including relay options
def testMenu():
    while True:
        print("Test Menu:")
        print("1. Test LEDs")
        print("2. Flash LEDs")
        print("3. Light all LEDs")
        print("4. Light LED Bank")
        print("5. Light Specific Place")
        print("6. Run Color Wipe")
        print("11. Test Relays")
        print("12. Exit")

        choice = input("Enter your choice (1-12): ")

        if choice == '1':
            testLEDS()
        elif choice == '2':
            flashLEDS()
        elif choice == '3':
            lightLEDS()
        elif choice == '4':
            bank = int(input("Enter bank number (0-2): "))
            LightLEDBank(bank)
        elif choice == '5':
            bank = int(input("Enter bank number (0-2): "))
            place = int(input("Enter place number (1-3): "))
            LightPlace(bank, place)
        elif choice == '6':
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
        elif choice == '11':
            testRelays()
        elif choice == '12':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 12.")

# Main function to test your LED functions and relays
if __name__ == "__main__":
    try:
        GPIO.setwarnings(False)
        GPIO.setmode (GPIO.BOARD)      ## Use GPIO PIN #'s instead of GPIO ID's.
                
        # Initialize the LED strip
        resetLEDS()

        # Display the test menu
        testMenu()

    except KeyboardInterrupt:
        cleanup()