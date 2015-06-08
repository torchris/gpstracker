#! /usr/bin/python
# GPA tracking system for RaspBerry Pi
# By Chris Armour 7 June 2015
# Some sections created by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import os
from gps import *
from time import *
import time
import threading
import math
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)

prev_input = 1
LED_on = False

from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont

font = ImageFont.load_default()
device = sh1106(port=1, address=0x3C)
 
gpsd = None #setting the global variable
cummDist = 0
old_lati = 0
old_longi = 0
current_distance = 0
 
os.system('clear') #clear the terminal (optional)
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

def getDistance(lat1,lon1,lat2,lon2):
    # This uses the haversine formula, which remains a good numberical computation,
    # even at small distances, unlike the Shperical Law of Cosines.
    # This method has ~0.3% error built in.
    R = 6371 # Radius of Earth in km

    dLat = math.radians(float(lat2) - float(lat1))
    dLon = math.radians(float(lon2) - float(lon1))
    lat1 = math.radians(float(lat1))
    lat2 = math.radians(float(lat2))

    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2) * math.sin(dLon/2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = (R * c) * 1000 #output in meters

    return d
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      global cummDist
      global old_lati
      global old_longi
      global current_distance
      #It may take a second or two to get good data
      #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc

      os.system('clear')

#      print
      print ' GPS reading'
      print '----------------------------------------'
      print 'latitude    ' , round(gpsd.fix.latitude,5)
      print 'longitude   ' , round(gpsd.fix.longitude,5)
      print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
      print 'altitude (m)' , gpsd.fix.altitude
#      print 'eps         ' , gpsd.fix.eps
#      print 'epx         ' , gpsd.fix.epx
#      print 'epv         ' , gpsd.fix.epv
#      print 'ept         ' , gpsd.fix.ept
#      print 'speed (m/s) ' , gpsd.fix.speed
#      print 'climb       ' , gpsd.fix.climb
#      print 'track       ' , gpsd.fix.track
#      print 'mode        ' , gpsd.fix.mode
#      print
#      print 'sats        ' , gpsd.satellites
      

      lati = str(round(gpsd.fix.latitude,5))
      longi = str(round(gpsd.fix.longitude,5))
      alti = str(gpsd.fix.altitude)
      sped = str(gpsd.fix.speed)
      print "Old Latitude:  ", old_lati
      print "Old Longitude:  ", old_longi
      current_distance = round(getDistance(old_lati,old_longi,gpsd.fix.latitude,gpsd.fix.longitude),2)
      current_distance_string = str(current_distance)
      print "Distance between samples: ", current_distance
      input = GPIO.input(24)
      if current_distance < 9000:
       if (not prev_input) and input:
         if (LED_on == False):
           print("Button pressed")
           LED_on = True
           GPIO.output(18,GPIO.HIGH)
           cummDist = cummDist + current_distance
         elif (LED_on == True):
           print('Button pressed again')
           LED_on = False
           GPIO.output(18,GPIO.LOW)    
      prev_input = input
      print "Distance since button pressed: ", cummDist

      with canvas(device) as draw:
       font = ImageFont.load_default()
       draw.text((5, 3), "Lat: ", font=font, fill=255)       
       draw.text((35,3), lati, font=font, fill=255)
       draw.text((5, 15), "Long: ", font=font, fill=255)       
       draw.text((35,15), longi, font=font, fill=255)
       draw.text((5, 27), "Alt: ", font=font, fill=255)       
       draw.text((35,27), alti, font=font, fill=255)
       draw.text((5, 40), "Spd: ", font=font, fill=255)       
       draw.text((35,40), sped, font=font, fill=255) 
       draw.text((5, 52), "Dst: ", font=font, fill=255)       
       draw.text((35,52), current_distance_string, font=font, fill=255) 
      
      old_lati = round(gpsd.fix.latitude,5)
      old_longi = round(gpsd.fix.longitude,5)
      time.sleep(0.25) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."

  GPIO.cleanup() 

