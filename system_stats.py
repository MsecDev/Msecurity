import time
import os
import sys
import datetime
import psutil
from influxdb import InfluxDBClient

# Configure InfluxDB connection variables
host = "localhost" # My Ubuntu NUC
port = 8086 # default port
user = "root" # the user/password created for the pi, with write access
password = "root" 
dbname = "system_stats" # the database we created earlier
interval = 10 # Sample period in seconds
# Create the InfluxDB client object
client = InfluxDBClient(host, port, user, password, dbname)
# Enter the sensor details

# think of measurement as a SQL table, it's not...but...
measurement = "System_Stats"
# location will be used as a grouping tag later
location = "system"
# Run until you get a ctrl^c

# Return CPU temperature as a character string                                      
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list                                        
# Index 0: total RAM                                                                
# Index 1: used RAM                                                                 
# Index 2: free RAM                                                                 
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string                                
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Tasks\:/ {print $2}'").readline().strip(\
)))

# Return information about disk space as a list (unit included)                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                          
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                  
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])
            
try:
    while True:
        # Read the sensor using the configured driver and gpio
        # CPU informatiom
        CPU_temp = getCPUtemperature()
        CPU_usage = str(psutil.cpu_percent(interval=1))

        # RAM information
        # Output is in kb, here I convert it in Mb for readability
        RAM_stats = getRAMinfo()
        VRAM_used = str(psutil.virtual_memory().percent)
        RAM_used = round(int(RAM_stats[1]) / 1000,1)
        RAM_free = round(int(RAM_stats[2]) / 1000,1)

        # Disk information
        DISK_stats = getDiskSpace()
        DISK_total = DISK_stats[0]
        DISK_free = DISK_stats[1]
        DISK_perc = DISK_stats[3]
        
        iso = datetime.datetime.utcnow().isoformat()
        # Print for debugging, uncomment the below line
        #print("[%s] RAM_used: %s, VRAM_used: %s, RAM_free: %s, DISK_free: %s, DISK_perc: %s, CPU_temp: %s, CPU_usage: %s" % (iso, RAM_used, VRAM_used, RAM_free, DISK_free, DISK_perc, CPU_temp, CPU_usage)) 
        # Create the JSON data structure
        data = [
        {
          "measurement": measurement,
              "tags": {
                  "location": location,
              },
              "time": iso,
              "fields": {
                  "RAM_used" : RAM_used,
                  "VRAM_used" : RAM_used,
                  "RAM_free" : RAM_free,
                  "DISK_free": DISK_free,
                  "DISK_perc": DISK_perc,
                  "CPU_temp": CPU_temp,
                  "CPU_usage": CPU_usage
              }
          }
        ]
        # Send the JSON data to InfluxDB
        client.write_points(data)
        # Wait until it's time to query again...
        time.sleep(interval)
 
except KeyboardInterrupt:
    print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")

    
