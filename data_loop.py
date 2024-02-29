from json import dumps
from websocket import WebSocket
from datetime import datetime, timedelta
from serial import Serial
import pandas as pd
from warnings import filterwarnings
import numpy as np
import time
from adafruit_gps import GPS
from pykalman import KalmanFilter
from threading import Thread
import os
from requests import post


filterwarnings("ignore")

#####  -----   Global Variables ----- #####
wsaddress = "ws://boatbuddy.live/ws/data/"
serialport = "/dev/ttyS0"
tides = pd.read_csv("./core/assets/files/tides.csv")
dst = pd.read_csv("./core/assets/files/dst.csv")
previous_heading = 1
track_history = []
counter = 60



""" create websocket """
ws = WebSocket()

""" start the serial connection to read GPS data """
uart = Serial(serialport, baudrate=9600, timeout=10)
gps = GPS(uart, debug=False)
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
    date_set = False
    while not date_set:
        try:
            dt = datetime.fromtimestamp(time.mktime(gps.timestamp_utc))
            os.system(f"sudo date +'%Y%m%d %H:%M:%S' -u --set '{dt}'")
            date_set = True
            print("==> system date set")
        except:
            print("==> error setting date, trying again")
            time.sleep(1)







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

        #pause and get current time
        time.sleep(1)
        current_time = datetime.now()

        #get tide data every 60 seconds
        if counter % 60 == 0:
            counter = 0
            type, tide_time, heights, times = get_tide_data(current_time)
        
        #cleanse data
        lat, lon, track_history = gps_converter(gps.latitude, gps.longitude, track_history)
        heading = heading_cleanser(gps.track_angle_deg, gps.speed_knots)

        #construct payload dict
        payload = {
                    "mph": knot_conversion(float(gps.speed_knots), "mph"),
                    "knts": round(float(gps.speed_knots),2),
                    "kph": knot_conversion(float(gps.speed_knots), "kph"),
                    "direction": get_cardinal(heading, gps.speed_knots),
                    "heading": heading,
                    "time": current_time.strftime("%H:%M"),
                    "tide_type": type,
                    "tide_time": tide_time,
                    "heights": heights,
                    "times": times,
                    "lat": lat,
                    "lon": lon,
                    "track": track_history[:-4],
                }
        
        #send payload for recording
        post("http://boatbuddy.live/record/", json=payload)

        #send payload to frontend
        ws.send(dumps(payload))

        counter += 1





