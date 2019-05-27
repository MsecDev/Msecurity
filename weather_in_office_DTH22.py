import time
import os
import sys
import datetime
import Adafruit_DHT
sensor = Adafruit_DHT.DHT22
pin = 21
from influxdb import InfluxDBClient


# Configure InfluxDB connection variables
host = "localhost" # My Ubuntu NUC
port = 8086 # default port
user = "root" # the user/password created for the pi, with write access
password = "root" 
dbname = "weather_condition" # the database we created earlier
interval = 5# Sample period in seconds
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
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        iso = datetime.datetime.utcnow().isoformat()
        # Print for debugging, uncomment the below line
        # print("[%s] Temp: %s, Humidity: %s" % (iso, ((temperature) -4.5), humidity)) 
        # Create the JSON data structure
        data = [
        {
          "measurement": measurement,
              "tags": {
                  "location": location,
              },
              "time": iso,
              "fields": {
                  "temperature" : ((temperature) -2.5),
                  "humidity": humidity
              }
          }
        ]
        # Send the JSON data to InfluxDB
        client.write_points(data)
        # Wait until it's time to query again...
        time.sleep(interval)
 
except KeyboardInterrupt:
    print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")

    

