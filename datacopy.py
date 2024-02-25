import json
import websocket
import random
from datetime import datetime, timedelta
import serial
import pandas as pd
import warnings
import numpy as np
import time
import adafruit_gps
from pykalman import KalmanFilter
import requests

warnings.filterwarnings("ignore")

#####  -----   Global Variables ----- #####
wsaddress = "ws://192.168.0.120:8000/ws/data/"
serialport = "/dev/ttyS0"
tides = pd.read_csv("./core/assets/files/tides.csv")
dst = pd.read_csv("./core/assets/files/dst.csv")
previous_heading = 1
track_history = []
connected = False
last_print = time.monotonic()
counter = 100

#####  -----   Instantiate ----- #####
""" create websocket """
ws = websocket.WebSocket()
print("=> websocket created")
""" start the serial connection to read GPS data """
uart = serial.Serial(serialport, baudrate=9600, timeout=10)
print("=> serial established")
gps = adafruit_gps.GPS(uart, debug=False)
print("=> gps connected")
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")
print("=> commands sent")




rpm = 566
seconds = 300000
mph = 0
#### ------ main loop to read GPS sensor and send over websocket to frontend ------ ####
while True:
    #gps.update()
    try: #getting gps data can sometimes be corrupt, so if error then just continue and try to read data again
        current = time.monotonic()
        if current - last_print >= 1.0: #pulls from GPS data every second without a sleep
            last_print = current
            mph += 1
            seconds += 1
            #if not gps.has_fix: # ensure we have a fix to satellites
            #    print("Waiting for fix...")
            #    continue
            while not connected: # connect to the websocket
                try:
                    ws.connect(wsaddress)
                    print("=> websocket connected")
                    connected = True
                except Exception as e:
                    print("=> retrying websocket connect")
                    pass
            payload = {
                        "mph": mph,
                        "knts": mph,
                        "kph": mph,
                        "direction": "NW",
                        "heading": 360,
                        "time": "10:30",
                        "tide_type": "H",
                        "tide_time": "10:30",
                        "heights": [],
                        "times": [],
                        "lat": 39.28744,
                        "lon": -74.57098,
                        "track": []
                    }
            print(payload)
            end = time.time()
            #print(f"CALC TIME :: {end - start}")
            #print(payload) #print data to console for further review. This gets stored in /tmp/rclocal.out
            #response = requests.post("http://boatbuddy.live/record/", json=payload)
            ws.send(json.dumps(payload)) #send data over websocket
            #counter += 1 #counter for tide data loop
    except Exception as e:
        if e is KeyError:
            exit
        else:
            print(f"error! {e}")
            connected = False #reset the websocket connection and retry to connect
            continue

