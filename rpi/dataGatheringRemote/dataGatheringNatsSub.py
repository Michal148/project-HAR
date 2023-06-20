from nats.aio.client import Client as NATS
import asyncio
import csv
import json

# init NATS connection, async communication needed
async def run(loop):
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    async def message_handler(msg):
        subject = msg.subject
        data = json.loads(msg.data.decode())
        print(f"Received a message on '{subject}': {data}")

        # save the collected data to output.csv file
        with open('output.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            # if file is empty, write a header
            if file.tell() == 0: 
                writer.writeheader()
            writer.writerow(data)

    await nc.subscribe("sensor_data", cb=message_handler)

    # run until ctrl+c
    stop = asyncio.Future()
    await stop

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
