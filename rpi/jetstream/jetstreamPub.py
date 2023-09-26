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
    nc = await nats.connect("nats://<nats_server_address>:4222")
    js = nc.jetstream()

    while True:
        acceleration = accel_gyro.acceleration

        # publish data
        _ = await js.publish("x", f"{acceleration[0]}".encode(),stream="RPI")
        _ = await js.publish("y", f"{acceleration[1]}".encode(),stream="RPI")
        _ = await js.publish("z", f"{acceleration[2]}".encode(),stream="RPI")


if __name__ == '__main__':
    asyncio.run(main())