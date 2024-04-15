import RPi.GPIO as GPIO
import os
import time

GPIO_PIN_IN = 26
STALL_TIME = 15 #in minutes

#####  -----   Instantiate ----- #####
""" set up GPIO """
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def power_watcher():
    print("==> power watcher starting")
    while True:
        time.sleep(1)
        state = GPIO.input(GPIO_PIN_IN)
        if state == 0:
            continue
        else:
            print(f"==> key off, shutting down in {STALL_TIME} minutes")
            start_time = time.monotonic()
            #time.sleep(STALL_TIME*60)
            while True:
                state = GPIO.input(GPIO_PIN_IN)
                if state == 0:
                    print("==> key on, restarting loop")
                    break
                elif time.monotonic() - start_time > STALL_TIME*60:
                    print("==> system shutdown")
                    os.system("sudo shutdown -h now")

power_watcher()