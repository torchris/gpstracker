import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

prev_input = 1
LED_on = False
button_press = 0

while True:
  input = GPIO.input(24)
  if (not prev_input) and input:
    if (LED_on == False):
      print("Button pressed")
      LED_on = True
      GPIO.output(18,GPIO.HIGH)
      button_press = button_press +1
    elif (LED_on == True):
      print('Button pressed again')
      LED_on = False
      GPIO.output(18,GPIO.LOW) 
      button_press = button_press +1   
  prev_input = input
  if button_press > 4:
    button_press = 0
  print button_press
  time.sleep(0.05)

GPIO.cleanup()        
