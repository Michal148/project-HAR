#!/bin/bash

# used for faster data export to DB, as well as delete invisible MacOS .DS_Store files
find . -name ".DS_Store" -type f -delete
find . -name "Accelerometer.csv" -type f -delete
find . -name "Gyroscope.csv" -type f -delete
find . -name "Magnetometer.csv" -type f -delete
find . -name "Annotation.csv" -type f -delete
find . -name "Metadata.csv" -type f -delete
find . -name "Gravity.csv" -type f -delete
find . -name "Orientation.csv" -type f -delete
find . -name "TotalAcceleration.csv" -type f -delete
find . -name "Light.csv" -type f -delete
find . -name "Microphone.csv" -type f -delete