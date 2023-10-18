import board
import asyncio
import nats
from adafruit_lis3mdl import Rate
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3 as LSM6DS

# setup acceleration rate
accel_rate = Rate.RATE_300_HZ

# setup i2x and accelerometer
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
accel_gyro.accelerometer_data_rate = accel_rate

# async communication needed for NATS
# streaming with persistence using JetStream
async def main():
    # open connection to NATS and interface for JetStream
    nc = await nats.connect("nats://<token>@<nats_server_address>:4222")
    js = nc.jetstream()
    print("connected to NATS")
    # counter to keep track of samples
    counter = 0
    while True:
        if counter % 3 == 0:
            acceleration = accel_gyro.acceleration

            # publish data
            _ = await js.publish("x", f"{acceleration[0] / 9.80665}".encode(),stream="RPI")
            _ = await js.publish("y", f"{acceleration[1] / 9.80665}".encode(),stream="RPI")
            _ = await js.publish("z", f"{acceleration[2] / 9.80665}".encode(),stream="RPI")

        counter +=1 


if __name__ == '__main__':
    asyncio.run(main())