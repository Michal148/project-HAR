import pandas as pd
from scipy.interpolate import PchipInterpolator
from kasper.feats import *
from Michał.Characteristics import magnitude
from wiktor.feats import lag

# takes in raw data from sensor
def interpolation(data):
    # create a time vector with 0.01s interval between consecutive timestamps
    timeVec = [sample for sample in range(data['time'].iloc[0], data['time'].iloc[-1], 10000000)]
    interpDf = pd.DataFrame(timeVec, columns=['time'])

    # iterate over x, y, z columns, concat to final dataframe
    for column in data[['x', 'y', 'z']]:
        interpModel = PchipInterpolator(data['time'], data[column])
        axisData = pd.DataFrame(interpModel(timeVec), columns = [column])
        interpDf = pd.concat([interpDf, axisData], axis=1)

    # calculate magnitude, lag and rename axes of lag columns
    magDf = pd.DataFrame(magnitude(interpDf), columns=['mag'])
    laggerX, laggerY, laggerZ = lag(2, interpDf)

    laggerX.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
    laggerY.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
    laggerZ.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)
    
    # concat magnitude and lag
    frames = [interpDf, magDf, laggerX, laggerY, laggerZ]
    interpDf = pd.concat(frames, axis = 1)

    return interpDf
