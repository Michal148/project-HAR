# Comaprsion of outputs
| variant | real output frequency |
| --- | ---|
|`scraping: every three samples, writing: every 300 samples` | from 91 to 100 samples/second|
|`scraping: every three samples, writing: every 1000 samples` | from 68 to 104 samples/second; big range due to long writing time |
| `scraping: every three samples, writing: every 1000 samples using second thread` | from 63 to 97 samples/second; irregular gathering frequency in the middle of the run|
|`scraping: every 0.01s, writing: every 300 samples` | from 75 to 100 samples/second; mostly within 90-100 samples/second range|
|`scraping: every three samples - forwarding data to NATS, writing: remote device` | stable rate of approx. ~97 samples/second; doesn't choke| 

# Gathering MARG data using NATS messaging
## Setup NATS
Run NATS docker container with 4222 port exposed. Remove container after `Ctrl+C`.
```bash
docker run --name nats --network nats --rm -p 4222:4222 -p 8222:8222 nats --http_port 8222
```
## Setting up python scripts
After successfully setting up NATS container, on local machine, run `python3 dataGatheringNatsSub.py`. On Raspberry Pi change to IP address of the machine where NATS is running and execute `python3 dataGatheringNatsPub.py`. Be sure to install all dependencies. 

## How it works
Data from **LSM6DS3TR-C + LIS3MDL** sensors is gathered at 300Hz. Since our models and features are based on 100Hz data gathering frequency, every third data sample is collected and saved as dictionary. Then, script sends data to NATS subject "sensor_data". From PC where NATS container is running, we connect to NATS and read the data from "sensor_data" and save it to `output.csv` file (it's also possible to connect from any other part of the world, however one would need to expose NATS address using, for instance, Cloudflare services for secure connection).

