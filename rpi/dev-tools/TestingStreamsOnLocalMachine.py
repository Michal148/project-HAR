import asyncio
import nats
import random

# async communication needed for NATS
# streaming with persistence using JetStream
async def main():
    # open connection to NATS and interface for JetStream
    nc = await nats.connect("nats://haslo@localhost:4222")
    js = nc.jetstream()
    i = 0
    while True:
        

        # publish data
        _ = await js.publish("x", f"{random.random()}".encode(),stream="RPI")
        _ = await js.publish("y", f"{random.random()}".encode(),stream="RPI")
        _ = await js.publish("z", f"{random.random()}".encode(),stream="RPI")
        print(f"published {i}")
        i+=1

if __name__ == '__main__':
    asyncio.run(main())