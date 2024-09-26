import RPi.GPIO as GPIO
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BOARD)

# Define the switch GPIO pin
switch = 16  # Switch is connected to pin number 16

# Set up GPIO for the switch
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set switch as input with pull-up

try:
    print("Press the switch to test it...")
    while True:
        # Check the state of the switch
        if GPIO.input(switch) == GPIO.LOW:
            print("Switch Pressed!")
        else:
            print("Switch Released!")

        # Small delay to avoid rapid printing
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Test interrupted.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up. Test finished.")
