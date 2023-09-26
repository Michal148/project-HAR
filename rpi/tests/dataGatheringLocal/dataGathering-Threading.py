import time
import threading
import queue
import pandas as pd
import board
from adafruit_lis3mdl import LIS3MDL, Rate
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3 as LSM6DS

# setup data rate
mag_rate = Rate.RATE_300_HZ
gyr_rate = Rate.RATE_300_HZ
accel_rate = Rate.RATE_300_HZ

# setup sensors
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

# set data gathering rate
accel_gyro.gyro_data_rate = gyr_rate
accel_gyro.accelerometer_data_rate = accel_rate
mag.data_rate = mag_rate

# queues for passing data between threads
data_queue = queue.Queue()

# timestamp for naming output.csv file
timestamp = int(time.time())

def acquire_data():
    counter = 0
    print("Data gathering started..")
    while True:
        # scrape only every third sample for 100Hz data collection 
        if counter % 3 == 0:
            acceleration = accel_gyro.acceleration
            gyro = accel_gyro.gyro
            magnetic = mag.magnetic

            data_queue.put(
                {
                    "timestamp": int(time.time()),
                    "acc-x": acceleration[0],
                    "acc-y": acceleration[1],
                    "acc-z": acceleration[2],
                    "gyr-x": gyro[0],
                    "gyr-y": gyro[1],
                    "gyr-z": gyro[2],
                    "mag-x": magnetic[0],
                    "mag-y": magnetic[1],
                    "mag-z": magnetic[2],
                }
            )
        counter += 1

def write_data():
    data = []
    while True:
        # wait for up to 1 second for data to be available
        try:
            sample = data_queue.get(timeout=1)
        except queue.Empty:
            continue

        data.append(sample)

        # save data to output file every 1000 samples
        if len(data) % 1000 == 0: 
            df = pd.DataFrame(data)
            filename = "output-{}.csv".format(timestamp)
            with open(filename, "a") as file:  # Open the file in append mode
                df.to_csv(file, header=file.tell()==0, index=False)
            
            data = []  # empty the data list after writing to file

# start the threads
acquisition_thread = threading.Thread(target=acquire_data, daemon=True)
writing_thread = threading.Thread(target=write_data, daemon=True)

acquisition_thread.start()
writing_thread.start()

# wait for both threads to finish (they won't, in this case, because they have infinite loops)
acquisition_thread.join()
writing_thread.join()