# LEDStrip2.py
# LED Strip For Game Pad
# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
import rp2

# Configure the number of WS2812 LEDs.
NUM_LEDS = 9
PIN_NUM = 2  #GPIO
brightness = 0.2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin  (PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

# Reset LED's to an off state
def resetLEDS():
    pixels_fill((0, 0, 0))
    pixels_show()
    time.sleep(0.2)

# Run test cycle of the LEDs
def testLEDS(color=(255, 0, 0)):  # Default color is Red
    pixels_fill(color)
    pixels_show()
    time.sleep(0.5)
    resetLEDS()

# 3 quick flashes of the LEDs
def flashLEDS(color=(255, 0, 0)):  # Default color is Red
    for _ in range(3):
        pixels_fill(color)
        pixels_show()
        time.sleep(0.2)
        resetLEDS()

# Light all LED's in the bank
def lightLEDS(color=(255, 0, 0)):  # Default color is Red
    pixels_fill(color)
    pixels_show()
    time.sleep(0.5)

# Light all LED's in specified bank
def LightLEDBank(LightBank, color=(255, 0, 0)):  # Default color is Red
    if LightBank > 3 or LightBank < 1:
        # Invalid Place value, do nothing
        return
    start_index = (LightBank -1) * 3
    end_index = start_index + 3
    for i in range(start_index, end_index):
        pixels_set(i, color)
    pixels_show()
    # time.sleep(0.5)

# Light a specific place in a specific light bank
def LightPlace(LightBank, Place, color=(255, 0, 0)):  # Default color is Red
    if Place > 3 or Place < 1:
        # Invalid Place value, do nothing
        return
    
    if LightBank > 3 or LightBank < 1:
        # Invalid Place value, do nothing
        return
            
    start_index = (LightBank-1) * 3
    end_index = start_index + Place
    for i in range(start_index, end_index):
        pixels_set(i, color)
    pixels_show()
    

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
            time.sleep(wait)
            pixels_show()
        time.sleep(wait)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)


# Call the main function to execute the code
if __name__ == "__main__":    # print("fills")
    #for color in COLORS:       
    #    pixels_fill(color)
    #    pixels_show()
    #    time.sleep(0.2)

    # print("chases")
    #for color in COLORS:       
    #    color_chase(color, 0.01)

    # print("rainbow")
    # rainbow_cycle(0)
    #time.sleep(4)

    print("Reset LEDs")
    resetLEDS()

    print("Flash LEDs")
    flashLEDS()

    print("light Bank")
    LightLEDBank(3, color=(0, 255, 255))
    LightLEDBank(2, color=(0, 255, 0))
    LightLEDBank(1, color=(255, 0, 0))
    time.sleep(4)
    resetLEDS()

    print("light Bank")
    LightPlace(1,1,color=(255, 0, 0))
    LightPlace(2,2,color=(0, 255, 0))
    LightPlace(3,3,color=(0, 0, 255))

