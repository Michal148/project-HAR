import asyncio
import nats
import random
import ssl

# async communication needed for NATS
# streaming with persistence using JetStream
async def main():
    # read ssl files
    ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_ctx.load_verify_locations('./CA.pem')
    ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2  
    ssl_ctx.load_cert_chain(
        certfile='./container4-cert.pem',
        keyfile='./container4-key.pem')
    
    # open connection to NATS and interface for JetStream
    nc = await nats.connect("nats://haslo@localhost:4222", tls=ssl_ctx, tls_hostname="nats")
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