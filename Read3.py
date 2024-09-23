#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
reader = SimpleMFRC522()
OldText = ''
print("Put card on reader")
GPIO.cleanup()
while True:
   # GPIO.cleanup()
    time.sleep(1)
    try:
        status,TagType = reader.read_no_block()
        print(status)
        if status == 'None':
            print ("No Card Found")
        elif status != 'None':
            id,text = reader.read()
            if text != OldText:
                print(text)
                print(id)
                OldText=text

            else:
                print ("Same card")

    finally:
        GPIO.cleanup()
    time.sleep(5) 