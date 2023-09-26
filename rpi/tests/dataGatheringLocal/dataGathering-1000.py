import time
import board
from adafruit_lis3mdl import LIS3MDL, Rate
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3 as LSM6DS
import pandas as pd

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

# counter to keep track of samples
# list to store gathered data
# timestamp for naming output.csv file
counter = 0
data = []
timestamp = int(time.time())

print("Data gathering started..")
while True:
    # scrape only every third sample for 100Hz data collection 
    if counter % 3 == 0:
        acceleration = accel_gyro.acceleration
        gyro = accel_gyro.gyro
        magnetic = mag.magnetic
        
        data.append(
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
              
        # save data to output file every 60 samples
        if counter % 1000  == 0: 
            df = pd.DataFrame(data)
            filename = "output-{}.csv".format(timestamp)
            with open(filename, "a") as file:  # Open the file in append mode
                df.to_csv(file, header=file.tell()==0, index=False)
            
            data = []  
            
    counter += 1