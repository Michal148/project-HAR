from matplotlib import pyplot as plt
import pandas as pd
from scipy.interpolate import PchipInterpolator
from Feats_columns import *

# takes in raw data from sensor
def interpolation(acc, mag, gyr):
    # set first and last timestamp, create time vector
    startTimestamp = max(acc['time'].iloc[0], mag['time'].iloc[0], gyr['time'].iloc[0])
    endTimestamp = min(acc['time'].iloc[-1], mag['time'].iloc[-1], gyr['time'].iloc[-1])
    timeVec = [sample for sample in range(startTimestamp, endTimestamp, 10000000)]
    
    # create accelerometer, magnetometer and gyroscope dataframes
    accDf = pd.DataFrame(timeVec, columns=['time'])
    magDf = pd.DataFrame(timeVec, columns=['time'])
    gyrDf = pd.DataFrame(timeVec, columns=['time'])

    # iterate over axes and interpolate data
    for column in acc[['x', 'y', 'z']]:
        interpModel = PchipInterpolator(acc['time'], acc[column])
        axisData = pd.DataFrame(interpModel(timeVec), columns = [column])
        accDf = pd.concat([accDf, axisData], axis=1)

    for column in mag[['x', 'y', 'z']]:
        interpModel = PchipInterpolator(mag['time'], mag[column])
        axisData = pd.DataFrame(interpModel(timeVec), columns = [column])
        magDf = pd.concat([magDf, axisData], axis=1)

    for column in gyr[['x', 'y', 'z']]:
        interpModel = PchipInterpolator(gyr['time'], gyr[column])
        axisData = pd.DataFrame(interpModel(timeVec), columns = [column])
        gyrDf = pd.concat([gyrDf, axisData], axis=1)


    # create magnitude, lag and in case of accelerometer - jerk columns
    magMagDf = pd.DataFrame(magnitude(magDf), columns=['mag'])
    laggerXMag, laggerYMag, laggerZMag = lag(2, magDf)
    laggerXMag.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
    laggerYMag.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
    laggerZMag.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)
    framesMag = [magDf, magMagDf, laggerXMag, laggerXMag, laggerYMag]
    magDf = pd.concat(framesMag, axis = 1)

    gyrMagDf = pd.DataFrame(magnitude(gyrDf), columns=['mag'])
    laggerXGyr, laggerYGyr, laggerZGyr = lag(2, gyrDf)
    laggerXGyr.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
    laggerYGyr.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
    laggerZGyr.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)
    framesGyr = [gyrDf, gyrMagDf, laggerXGyr, laggerYGyr, laggerZGyr]
    gyrDf = pd.concat(framesGyr, axis = 1)

    accMagDf = pd.DataFrame(magnitude(accDf), columns=['mag'])
    laggerXAcc, laggerYAcc, laggerZAcc = lag(2, accDf)
    laggerXAcc.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
    laggerYAcc.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
    laggerZAcc.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)
    jerkM, jerkX, jerkY, jerkZ = jerk(accDf)
    mJerkDf = pd.DataFrame(jerkM, columns= ["jerkMag"])
    xJerkDf = pd.DataFrame(jerkX, columns= ["jerkX"])
    yJerkDf = pd.DataFrame(jerkY, columns= ["jerkY"])
    zJerkDf = pd.DataFrame(jerkZ, columns= ["jerkZ"])
    framesAcc = [accDf, accMagDf, laggerXAcc, laggerYAcc, laggerZAcc, mJerkDf, xJerkDf, yJerkDf, zJerkDf]
    accDf = pd.concat(framesAcc, axis = 1)

    # return dataframes with interpolated data
    return accDf, magDf, gyrDf