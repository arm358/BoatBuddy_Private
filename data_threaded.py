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
from threading import Thread
import os

warnings.filterwarnings("ignore")

#####  -----   Global Variables ----- #####
wsaddress = "ws://boatbuddy.live/ws/data/"
serialport = "/dev/ttyS0"
tides = pd.read_csv("./core/assets/files/tides.csv")
dst = pd.read_csv("./core/assets/files/dst.csv")
previous_heading = 1
track_history = []
last_print = time.monotonic()
counter = 60

#####  -----   Instantiate ----- #####
""" create websocket """
ws = websocket.WebSocket()

""" start the serial connection to read GPS data """
uart = serial.Serial(serialport, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")



def heading_cleanser(heading, speed):
    """ returns the heading only if > 2 degrees of difference between last heading
    this reduces the small incremental changes in heading from being  displayed on the map """
    global previous_heading
    try:
        heading = int(heading)
        speed = float(speed)
        if abs(previous_heading - heading) < 2 or speed < 1.0:
            return previous_heading
        else:
            previous_heading = heading
            return heading
    except:
        return previous_heading


def knot_conversion(knots, to_units):
    converstions = {"mph": 1.151, "kph": 1.852}
    return round(converstions[to_units] * 1.852, 2)


def _gmt_offset(now, dstflag, tz):
    pass

def gmt_offset(now, dstflag, tz):
    """since GPS time is GMT without daylight savings, converts current time to configured 
    timezone and accounts for DST"""
    year = int(now.strftime("%Y"))
    startdate = dst[dst["year"] == year].iloc[0]["startdate"]
    endday = dst[dst["year"] == year].iloc[0]["endday"]
    begin = datetime.strptime(str(year) + " 3 " + str(startdate), "%Y %m %d")
    end = datetime.strptime(str(year) + " 10 " + str(endday), "%Y %m %d")

    if now >= begin and now <= end and dstflag:
        now = now + timedelta(hours=tz+1)
    else:
        now = now + timedelta(hours=tz)

    return now


def filter(line):
    """ Kalman filter to remove erroneous GPS data and smooth the output """
    output = []

    measurements = np.asarray(line)
    initial_state_mean = [measurements[0, 0], 0, measurements[0, 1], 0]

    transition_matrix = [[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]

    observation_matrix = [[1, 0, 0, 0], [0, 0, 1, 0]]

    kf1 = KalmanFilter(
        transition_matrices=transition_matrix, observation_matrices=observation_matrix, initial_state_mean=initial_state_mean
    )
    kf1 = kf1.em(measurements, n_iter=5)

    kf2 = KalmanFilter(
        transition_matrices=transition_matrix,
        observation_matrices=observation_matrix,
        initial_state_mean=initial_state_mean,
        observation_covariance=10 * kf1.observation_covariance,
        em_vars=["transition_covariance", "initial_state_covariance"],
    )

    kf2 = kf2.em(measurements, n_iter=5)
    (smoothed_state_means, smoothed_state_covariances) = kf2.smooth(measurements)

    out = smoothed_state_means.tolist()

    for item in out:
        output.append([item[0], item[2]])

    return output


def gps_converter(lat, lon, track_history):
    """ Rounds the lat/lon from GPS data and creates the list of coordinates that shows the previous route taken
    this removes the last 15 data points due to those not being as smoothed as earlier points"""
    try:
        lat = round(lat,5)
        lon = round(lon,5)

        noduplicates = track_history[-10:]
        if not [lon, lat] in noduplicates:
            track_history.append([lon, lat])

        outline = filter(track_history[-15:])
        track_history = track_history[:-15]

        for item in outline:
            item[0] = round(item[0],5)
            item[1] = round(item[1],5)
            track_history.append(item)
        lat = track_history[-5][1]
        lon = track_history[-5][0]
        return lat, lon, track_history
    except:
        return lat, lon, track_history



def get_tide_data(now_time):
    """pulls tide data from the saved tides.csv file. This is only called every 100seconds to reduce overhead"""
    tides["datetime"] = tides.apply(lambda row: datetime.strptime(row["t"], "%m/%d/%Y %H:%M"), axis=1)
    next_tides = tides.loc[tides["datetime"] >= now_time]

    type = next_tides.iloc[0]["type"]
    tide_time = next_tides.iloc[0]["time"]

    today = now_time.strftime("%Y-%m-%d")
    tomorrow = now_time + timedelta(days=1)
    tomorrow = tomorrow.strftime("%Y-%m-%d")

    tide_window = tides.loc[(tides["date"] == today) | (tides["date"] == tomorrow)]
    heights = tide_window["v"].tolist()
    times = tide_window["time"].tolist()

    return (type, tide_time, heights, times)


def get_cardinal(heading, speed):
    global previous_heading
    heading = int(round(float(heading)))
    speed = float(speed)
    heading = heading if speed > 1 else previous_heading

    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ix = round(heading / (360. / len(dirs)))
    return dirs[ix % len(dirs)]



def _get_cardinal(heading, speed):
    """a non-optimized way of converting the heading in degrees to cardinal heading"""
    heading = int(round(float(heading)))
    speed = float(speed)
    global previous_heading
    heading = heading if speed > 1 else previous_heading
    if heading >= 337 or heading <= 23:
        cardinal = "N"
    elif heading > 23 and heading < 67:
        cardinal = "NE"
    elif heading >= 67 and heading <= 113:
        cardinal = "E"
    elif heading > 113 and heading < 157:
        cardinal = "SE"
    elif heading >= 157 and heading <= 203:
        cardinal = "S"
    elif heading > 203 and heading < 247:
        cardinal = "SW"
    elif heading >= 247 and heading <= 293:
        cardinal = "W"
    elif heading > 293 and heading < 337:
        cardinal = "NW"
    return cardinal


def update_gps():
    while True:
        gps.update()


def websocket_connect(wsaddress):
    #connect to websocket
    connected = False
    print("==> connecting to websocket")
    while not connected:
        try:
            ws.connect(wsaddress)
            connected = True
        except:
            time.sleep(1)
            continue
    print("==> websocket established")
    
def wait_for_fix():
    while not gps.has_fix: # ensure we have a fix to satellites
        print("==> waiting for fix")
        time.sleep(1)
    print("==> GPS fix acquired")

def set_system_date():
    print("==> setting system date from GPS")
    dt = datetime.fromtimestamp(time.mktime(gps.timestamp_utc))
    os.system(f"sudo date +'%Y%m%d %H:%M:%S' -u --set '{dt}'")
    print("==> system date set")



if __name__ == "__main__":
    
    #start gps update thread
    t1 = Thread(target=update_gps)
    t1.start()

    #connect to websocket
    websocket_connect(wsaddress)

    #wait for GPS signal fix
    wait_for_fix()

    #set system date
    set_system_date()

    #start data loop
    print("==> data loop starting")
    while True:
        time.sleep(1)
        current_time = datetime.now()
        if counter % 60 == 0: #only pulls tide data every 60 loops == every 60 seconds
            type, tide_time, heights, times = get_tide_data(current_time)
        lat, lon, track_history = gps_converter(gps.latitude, gps.longitude, track_history)
        heading = heading_cleanser(gps.track_angle_deg, gps.speed_knots)
        #this is the data package send over websocket and rendered in the browser
        payload = {
                    "mph": knot_conversion(float(gps.speed_knots), "mph"),
                    "knts": round(float(gps.speed_knots),2),
                    "kph": knot_conversion(float(gps.speed_knots), "kph"),
                    "direction": get_cardinal(heading, gps.speed_knots),
                    "heading": heading,
                    "depth": 0,
                    "air": 0,
                    "humidity": 0,
                    "time": current_time.strftime("%H:%M"),
                    "tide_type": type,
                    "tide_time": tide_time,
                    "heights": heights,
                    "times": times,
                    "lat": lat,
                    "lon": lon,
                    "track": track_history[:-4],
                }
        #print(payload)
        ws.send(json.dumps(payload)) #send data over websocket
        counter += 1 #counter for tide data loop





