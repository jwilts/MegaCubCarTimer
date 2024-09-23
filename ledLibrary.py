#ledLibrary.py
#!/usr/bin/env python
## Leverage addressable LEDs. 

import RMSettings
import time
from rpi_ws281x import PixelStrip, Color

# Configuration Information from RMSettings.py
RelayYN = RMSettings.relay_yn
leds = RMSettings.leds
leds = list(map(int, leds))  # Fix leds so that it is an array of integers
GPIO_relay_1 = RMSettings.GPIO_relay_1

# LED strip configuration
# LED_COUNT = len(leds)
LED_COUNT = RMSettings.LED_COUNT
LED_PIN = RMSettings.wsled  # GPIO pin connected to the data input of the LED strip
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 200
LED_INVERT = False

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

# Initialize the LED strip
strip.begin()

# Reset LED's to an off state
def resetLEDS():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# Functions to handle different RGB orders
def setPixelColorCorrected(strip, i, color):
    if RMSettings.RGB_ORDER == 'RGB':
        strip.setPixelColor(i, color)
    elif RMSettings.RGB_ORDER == 'GRB':
        strip.setPixelColor(i, Color(color.green, color.red, color.blue))
    elif RMSettings.RGB_ORDER == 'BGR':
        strip.setPixelColor(i, Color(color.blue, color.green, color.red))
    # Add more conditions for other RGB orders if necessary

# Run test cycle of the LEDs
def testLEDS(color=Color(255, 0, 0)):  # Default color is Red
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(2)
    resetLEDS()

# 3 quick flashes of the LEDS
def flashLEDS(color=Color(255, 0, 0)):  # Default color is Red
    for _ in range(3):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()
        time.sleep(0.1)
        resetLEDS()
        time.sleep(0.1)

# Light all LED's in the bank
def lightLEDS(color=Color(255, 0, 0)):  # Default color is Red
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

# Light all LED's in specified bank
def LightLEDBank(LightBank, color=Color(255, 0, 0)):  # Default color is Red
    resetLEDS()
    for i in range(LightBank * 3, (LightBank * 3) + 3):
        strip.setPixelColor(i, color)
    strip.show()

# Light a specific place in a specific light bank
def LightPlace(LightBank, Place, color=Color(255, 0, 0)):  # Default color is Red
    resetLEDS()
    for i in range(LightBank * 3, (LightBank * 3) + Place):
        strip.setPixelColor(i, color)
    strip.show()

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

# Clean up when done
def cleanup():
    resetLEDS()
    strip.show()
    strip.stop()

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
        print("7. Run Theater Chase")
        print("8. Run Rainbow")
        print("9. Run Rainbow Cycle")
        print("10. Run Theater Chase Rainbow")
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
        elif choice == '7':
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
        elif choice == '8':
            rainbow(strip)
        elif choice == '9':
            rainbowCycle(strip)
        elif choice == '10':
            theaterChaseRainbow(strip)
        elif choice == '11':
            testRelays()
        elif choice == '12':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 12.")

# Main function to test your LED functions and relays
if __name__ == "__main__":
    try:
        # Initialize the LED strip
        strip.begin()
        
        resetLEDS()

        # Display the test menu
        testMenu()

    except KeyboardInterrupt:
        cleanup()