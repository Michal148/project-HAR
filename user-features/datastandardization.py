import pandas as pd

# used to standardize Android devices data
# read the dataframe, check the platform. if device is Android - change the sign of the data in the Z column
# and divide each applicable column by the value of g

def ios_conversion(data):
    if data['platform'][0] == "apple":
        return data
    
    else:
        data['x'] = data['x'] / 9.80665
        data['y'] = data['z'] / 9.80665
        data['z'] = -data['z'] / 9.80665
        data['mag'] = data['mag'] / 9.80665
        
        data['lagX0'] = data['lagX0'] / 9.80665
        data['lagY0'] = data['lagY0'] / 9.80665
        data['lagZ0'] = data['lagZ0'] / 9.80665

        data['lagX1'].iloc[1:] = data['lagX1'].iloc[1:].astype(float) / 9.80665
        data['lagY1'].iloc[1:] = data['lagY1'].iloc[1:].astype(float) / 9.80665
        data['lagZ1'].iloc[1:] = data['lagZ1'].iloc[1:].astype(float) / 9.80665

        data['lagX2'].iloc[2:] = data['lagX2'].iloc[2:].astype(float) / 9.80665
        data['lagY2'].iloc[2:] = data['lagY2'].iloc[2:].astype(float) / 9.80665
        data['lagZ2'].iloc[2:] = data['lagZ2'].iloc[2:].astype(float) / 9.80665

        if 'jerkX' in data.columns:
            data['jerkX'].iloc[:-1] = data['jerkX'].iloc[:-1].astype(float) / 9.80665
            data['jerkY'].iloc[:-1] = data['jerkY'].iloc[:-1].astype(float)  / 9.80665
            data['jerkZ'].iloc[:-1] = data['jerkZ'].iloc[:-1].astype(float) / 9.80665
            data['jerkMag'].iloc[:-1] = data['jerkMag'].iloc[:-1].astype(float)  / 9.80665

        return data
        
