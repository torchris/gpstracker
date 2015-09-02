import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

def blink(pin):
        GPIO.output(pin,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(pin,GPIO.LOW)
        time.sleep(1)
        return

button_press = 0

while True:
    input_state = GPIO.input(24)
    if input_state == False:
        button_press = button_press + 1
        print'Button Pressed: ', button_press
        blink(18)
        time.sleep(0.2)
