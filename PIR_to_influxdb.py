import time
import os
import sys
import datetime
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(36, GPIO.IN)
GPIO.setup(37, GPIO.IN)
GPIO.setup(38, GPIO.IN)
from influxdb import InfluxDBClient


# Configure InfluxDB connection variables
host = "localhost" # My Ubuntu NUC
port = 8086 # default port
user = "" # the user/password created for the pi, with write access
password = "" 
dbname = "" # the database we created earlier
interval = 5 # Sample period in seconds
# Create the InfluxDB client object
client = InfluxDBClient(host, port, user, password, dbname)
# Enter the sensor details


# think of measurement as a SQL table, it's not...but...
measurement = "DTH22"
# location will be used as a grouping tag later
location = "office"
# Run until you get a ctrl^c
try:
    while True:
        PIR=GPIO.input(11)
        CO=(1-(GPIO.input(36)))
        DYM=(1-(GPIO.input(37)))
        SOUND=GPIO.input(38)
        iso = datetime.datetime.utcnow().isoformat()
        # Print for debugging, uncomment the below line
       # print(PIR)
        #print(CO) 
        # Create the JSON data structure
        data = [
        {
          "measurement": measurement,
              "tags": {
                  "location": location,
              },
              "time": iso,
              "fields": {
                  "PIR" : PIR,
                  "SOUND" : SOUND,
                  "CO" : CO,
                  "DYM" : DYM, 
              }
          }
        ]
        # Send the JSON data to InfluxDB
        client.write_points(data)
        # Wait until it's time to query again...
        time.sleep(interval)
 
except KeyboardInterrupt:
    print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")

    

