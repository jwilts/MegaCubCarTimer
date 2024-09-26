# main.py

import time
import network
import socket
from mfrc522 import MFRC522
from rotary_irq_rp2 import RotaryIRQ  
from pico_i2c_lcd import I2cLcd
from machine import Pin, I2C, reset
from secret import ssid, password
import RMSettings  # RMSettings contains SERVER_IP, SERVER_PORT
import LEDStrip2 as LED # LED Library that mimics PI

lcd = None  # Define lcd as a global variable
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Define button PIN as a global variable
client_socket = None  # Define client_socket as a global variable

# Function to handle button press
def is_button_pressed(button_pin):
    button_state = button_pin.value()
    print(f"Button state: {button_state}")
    return button_state == 0

# Function to convert UID to decimal string
def uid_to_decimal_str(uid):
    decimal_id = 0
    for byte in uid:
        decimal_id = decimal_id * 256 + byte
    return str(decimal_id)

# Function to display RFID tag information on LCD
def display_rfid_tag(lcd, tag_id):
    lcd.clear()
    lcd.putstr("RFID Tag ID:")
    lcd.move_to(0, 1)
    lcd.putstr(tag_id)
    
# Function to display RFID tag information on LCD
def display_socketResponse(lcd, data):
    lcd.clear()
    lcd.putstr("Data:")
    lcd.move_to(0, 1)
    lcd.putstr(data)
   
# Function to display error information on LCD
def display_err(lcd, err_id):
    lcd.clear()
    lcd.move_to(0, 1)
    lcd.putstr(err_id)

# Function to display "Next Tag Please" on LCD
def display_next_tag_message(lcd):
    lcd.clear()
    lcd.putstr("Next Tag Please")

def init_LCD():
    global lcd  # Declare lcd as global
    # Initialize I2C for the LCD
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    I2C_ADDR = 0x27
    lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)
    lcd.clear()
    lcd.putstr('Starting ' + ssid + "\n")
    return lcd

def init_WIFI():
    global lcd  # Declare lcd as global
    lcd = init_LCD()  # Initialize LCD and assign to the global variable
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password, channel=2)

    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            print(str(wlan.status()))
            lcd.clear()
            lcd.putstr(str(wlan.status()) + "\n")
            if wlan.status() == -1:
                lcd.clear()
                lcd.putstr('Connect Fail' + "\n")
                reset()
            break
        max_wait -= 1
        print('waiting for connection')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        lcd.clear()
        lcd.putstr('SSID = ' + ssid + "\n")
        lcd.putstr('ip = ' + status[0] + "\n")
        lcd.putstr('pi = ' + RMSettings.SERVER_IP + "\n")
        return 0

def init_SOCKET():
    global lcd, client_socket  # Declare lcd and client_socket as global
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((RMSettings.SERVER_IP, RMSettings.SERVER_PORT))
        lcd.putstr('Socket Connected\n')
    except OSError as e:
        lcd.putstr('Socket Error\n')
        print("Socket Error:", e)

def init_LED():
        LED.resetLEDS()
        LED.flashLEDS(color=(0, 0, 255))

def main():
    global button_pin, client_socket
    LED.testLEDS(color=(255, 0, 0))
    init_WIFI()
    init_SOCKET()
    init_LED()
    while button_pin.value() == 1:
        continue
    print('INIT COMPLETE')
    lcd.clear()
    lcd.putstr('Start Scanning\n')
    while True:
        reader = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)
        reader.init()
        (stat, tag_type) = reader.request(reader.REQIDL)

        if stat == reader.OK:
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                card = uid_to_decimal_str(uid)
                print("CARD ID: " + card)

                client_socket.send(card.encode())

                response = client_socket.recv(1024).decode()
                print(f"Response: {response}")
                
                # display_rfid_tag(lcd, card)
                display_socketResponse(lcd, response)
                
                # Lookup the lane number from response
                lane = int(response[0])
                LED.LightLEDBank(lane, color=(255, 0, 0))
                
                while button_pin.value() == 1:
                    continue
                
                # client_socket.send(bytes([88]))
                client_socket.send(b'88')

                response = client_socket.recv(1024).decode()
                print(f"Response: {response}")
                
                LED.resetLEDS()
                display_next_tag_message(lcd)   

# Call the main function to execute the code
if __name__ == "__main__":
    main()
