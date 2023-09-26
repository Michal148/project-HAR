import time
import board
import asyncio
import json
import nats
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

# async communication needed for NATS
async def run(loop):
    nc = await nats.connect("nats://<nats_server_address>:4222")
    print("Data gathering started..")
    # counter to keep track of samples
    counter = 0
    while True:
        # scrape only every third sample for 100Hz data collection 
        if counter % 3 == 0:
            acceleration = accel_gyro.acceleration
            gyro = accel_gyro.gyro
            magnetic = mag.magnetic
            
            data = {
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

            # Publish data
            await nc.publish("sensor_data", json.dumps(data).encode('utf-8'))

        counter += 1

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
