import asyncio
import nats
import pandas as pd
import base64
import os
from SignalFeatures import *

# read env variables needed to connect to NATS
TOKEN = os.getenv('NATS_TOKEN')
NATS_ADDRESS = os.getenv('NATS_ADDRESS')

# async communication needed for NATS
async def main():
    nc = await nats.connect(f"nats://{TOKEN}@{NATS_ADDRESS}:4222")
    js = nc.jetstream()

    # probably need to change to ephemeral consumers
    # create consumers
    sub_x = await js.pull_subscribe("x","RPI-sub-x","RPI")
    sub_y = await js.pull_subscribe("y","RPI-sub-y","RPI")
    sub_z = await js.pull_subscribe("z","RPI-sub-z","RPI")

    # consume data in 100-data-points tranches
    while True:
        windowDf = pd.DataFrame(columns=['x', 'y', 'z'])
        x_data = await sub_x.fetch(500, timeout=None)
        y_data = await sub_y.fetch(500, timeout=None)
        z_data = await sub_z.fetch(500, timeout=None)

        x_data_list = [m.data.decode() for m in x_data]
        y_data_list = [m.data.decode() for m in y_data]
        z_data_list = [m.data.decode() for m in z_data]
        
        # export data from sensors to pandas DataFrame
        windowDf['x'] = x_data_list
        windowDf['y'] = y_data_list
        windowDf['z'] = z_data_list

        # treat data points as floats
        windowDf['x'] = windowDf['x'].astype(float)
        windowDf['y'] = windowDf['y'].astype(float)
        windowDf['z'] = windowDf['z'].astype(float)

        # calculate features of given window
        # send them to feats subject
        feats = feats_df(windowDf)
        json_data = feats.to_json(orient='split')
        base64_encoded_data = base64.b64encode(json_data.encode()).decode()

        _ = await js.publish("feats", f"{base64_encoded_data}".encode(),stream="RPI")
        

if __name__ == '__main__':
    asyncio.run(main())