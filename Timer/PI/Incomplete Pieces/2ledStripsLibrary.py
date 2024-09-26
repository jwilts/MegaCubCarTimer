#2ledStripsLibrary.py
#!/usr/bin/env python
## Leverage addressable LEDs. 

import RMSettings
import time
from rpi_ws281x import PixelStrip, Color
import RPi.GPIO as GPIO

# Configuration Information from RMSettings.py
RelayYN = RMSettings.relay_yn
leds = RMSettings.leds
leds = list(map(int, leds))  # Fix leds so that it is an array of integers
GPIO_relay_1 = RMSettings.GPIO_relay_1

# LED strip configuration
LED_COUNT = RMSettings.LED_COUNT
LED_COUNT2 = RMSettings.LED_COUNT2
LED_PIN2 = RMSettings.WinnerLight  # GPIO pin connected to the data input of the second LED strip
LED_PIN = RMSettings.Tracklight  # GPIO pin connected to the data input of the first LED strip

LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 100
LED_INVERT = False

# Initialize the first LED strip
strip1 = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip1.begin()

# Initialize the second LED strip
strip2 = PixelStrip(LED_COUNT2, LED_PIN2, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip2.begin()

# Reset LED's to an off state for both strips
def resetLEDS(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# Test cycle of the LEDs for the first strip
def testLEDS(strip, color=Color(255, 0, 0)):  # Default color is Red
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(2)
    resetLEDS(strip)

# Test cycle of the LEDs for the second strip
def testLEDS2(strip, color=Color(0, 255, 0)):  # Default color is Red
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(2)
    resetLEDS(strip)

# Define functions which animate LEDs in various ways for both strips

# Wipe color across display a pixel at a time for both strips
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Movie theater light style chaser animation for both strips
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

# Generate rainbow colors across 0-255 positions for both strips
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

# Draw rainbow that fades across all pixels at once for both strips
def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Draw rainbow that uniformly distributes itself across all pixels for both strips
def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Rainbow movie theater light style chaser animation for both strips
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


# Define a function to show the main test menu including relay options
def testMenu():
    while True:
        print("Test Menu:")
        print("1. Test LEDs Strip 1")
        print("2. Test LEDs Strip 2")
        print("3. Run Color Wipe on Strip 1")
        print("4. Run Color Wipe on Strip 2")
        print("5. Run Theater Chase on Strip 1")
        print("6. Run Theater Chase on Strip 2")
        print("7. Run Rainbow on Strip 1")
        print("8. Run Rainbow on Strip 2")
        print("9. Run Rainbow Cycle on Strip 1")
        print("10. Run Rainbow Cycle on Strip 2")
        print("11. Run Theater Chase Rainbow on Strip 1")
        print("12. Run Theater Chase Rainbow on Strip 2")
        print("13. Test Relays")
        print("14. Exit")

        choice = input("Enter your choice (1-14): ")

        if choice == '1':
            testLEDS(strip1)
        elif choice == '2':
            testLEDS2(strip2)
        elif choice == '3':
            colorWipe(strip1, Color(255, 0, 0))  # Red wipe on Strip 1
        elif choice == '4':
            colorWipe(strip2, Color(255, 0, 0))  # Red wipe on Strip 2
        elif choice == '5':
            theaterChase(strip1, Color(127, 127, 127))  # White theater chase on Strip 1
        elif choice == '6':
            theaterChase(strip2, Color(127, 127, 127))  # White theater chase on Strip 2
        elif choice == '7':
            rainbow(strip1)
        elif choice == '8':
            rainbow(strip2)
        elif choice == '9':
            rainbowCycle(strip1)
        elif choice == '10':
            rainbowCycle(strip2)
        elif choice == '11':
            theaterChaseRainbow(strip1)
        elif choice == '12':
            theaterChaseRainbow(strip2)
        elif choice == '13':
            testRelays()
        elif choice == '14':
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 14.")

        
# Main function to test your LED functions and relays
if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BOARD)
        
        resetLEDS(strip1)
        resetLEDS(strip2)

        # Display the test menu
        testMenu()

    except KeyboardInterrupt:
        # Clean up when done
        resetLEDS(strip1)
        resetLEDS(strip2)
        GPIO.cleanup()
