import time


while True:
    start_time = time.monotonic()
    time.sleep(5)
    print(time.monotonic() - start_time)