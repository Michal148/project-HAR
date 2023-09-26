import asyncio
import nats
from nats.errors import TimeoutError
import pandas as pd

# async communication needed for NATS
async def main():
    nc = await nats.connect("nats://localhost:4222")
    js = nc.jetstream()

    # probably need to change to ephemeral consumers
    # create consumers
    sub_x = await js.pull_subscribe("x","RPI-sub-x","RPI")
    sub_y = await js.pull_subscribe("y","RPI-sub-y","RPI")
    sub_z = await js.pull_subscribe("z","RPI-sub-z","RPI")

    # consume data in 100-data-points tranches
    while True:
        windowDf = pd.DataFrame(columns=['x', 'y', 'z'])
        x_data = await sub_x.fetch(100)
        y_data = await sub_y.fetch(100)
        z_data = await sub_z.fetch(100)

        x_data_list = [m.data.decode() for m in x_data]
        y_data_list = [m.data.decode() for m in y_data]
        z_data_list = [m.data.decode() for m in z_data]
        
        # export data from sensors to pandas DataFrame
        windowDf['x'] = x_data_list
        windowDf['y'] = y_data_list
        windowDf['z'] = z_data_list


if __name__ == '__main__':
    asyncio.run(main())