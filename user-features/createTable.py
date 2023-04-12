import pyodbc
import pandas as pd 
from pathlib import Path
import os
from Feats_columns import *

# naming convention
# SensorNameActivityPlatform.csv

# read connection variables from env
driver = os.environ['DBDriver']
server = os.environ['DBServer']
database = os.environ['DBDb']
username = os.environ['DBUser']
password = os.environ['DBPass']

# list directories in streaming-work-dir
directory = './user-features/streaming-work-dir'
dirs = sorted(Path(directory).glob('*'))

# initial connection for table creation
with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        # iterate over files in directories
        for dir in dirs:
            files = sorted(Path(dir).glob('*'))

            for file in files:
                sensorTableName = os.path.basename(os.path.normpath(file)).replace('.csv', '')

                # check if file name has "ccel" in it
                # if so, add jerk columns
                if sensorTableName.find("ccel") > 0:
                    tableQuery = f"CREATE TABLE [dbo].[{sensorTableName}] ( \
                                        [time]            BIGINT       NULL, \
                                        [seconds_elapsed] VARCHAR (MAX) NULL, \
                                        [x]             VARCHAR (MAX) NULL, \
                                        [y]              VARCHAR (MAX) NULL, \
                                        [z]              VARCHAR (MAX) NULL, \
                                        [mag]              VARCHAR (MAX) NULL, \
                                        [lagX0]              VARCHAR (MAX) NULL, \
                                        [lagX1]              VARCHAR (MAX) NULL, \
                                        [lagX2]              VARCHAR (MAX) NULL, \
                                        [lagY0]              VARCHAR (MAX) NULL, \
                                        [lagY1]              VARCHAR (MAX) NULL, \
                                        [lagY2]              VARCHAR (MAX) NULL, \
                                        [lagZ0]              VARCHAR (MAX) NULL, \
                                        [lagZ1]              VARCHAR (MAX) NULL, \
                                        [lagZ2]              VARCHAR (MAX) NULL, \
                                        [jerkX]              VARCHAR (MAX) NULL, \
                                        [jerkY]              VARCHAR (MAX) NULL, \
                                        [jerkZ]              VARCHAR (MAX) NULL, \
                                        [jerkMag]              VARCHAR (MAX) NULL, \
                                        [platform]              VARCHAR (MAX) NULL, \
                                        [activity]              VARCHAR (MAX) NULL, \
                                        [activityPackage]              VARCHAR (MAX) NULL);"
                    
                    cursor.execute(tableQuery)
                    conn.commit()
                
                else:
                    tableQuery = f"CREATE TABLE [dbo].[{sensorTableName}] ( \
                                        [time]            BIGINT       NULL, \
                                        [seconds_elapsed] VARCHAR (MAX) NULL, \
                                        [x]             VARCHAR (MAX) NULL, \
                                        [y]              VARCHAR (MAX) NULL, \
                                        [z]              VARCHAR (MAX) NULL, \
                                        [mag]              VARCHAR (MAX) NULL, \
                                        [lagX0]              VARCHAR (MAX) NULL, \
                                        [lagX1]              VARCHAR (MAX) NULL, \
                                        [lagX2]              VARCHAR (MAX) NULL, \
                                        [lagY0]              VARCHAR (MAX) NULL, \
                                        [lagY1]              VARCHAR (MAX) NULL, \
                                        [lagY2]              VARCHAR (MAX) NULL, \
                                        [lagZ0]              VARCHAR (MAX) NULL, \
                                        [lagZ1]              VARCHAR (MAX) NULL, \
                                        [lagZ2]              VARCHAR (MAX) NULL, \
                                        [platform]              VARCHAR (MAX) NULL, \
                                        [activity]              VARCHAR (MAX) NULL, \
                                        [activityPackage]              VARCHAR (MAX) NULL);"

                    cursor.execute(tableQuery)
                    conn.commit()
                
# acknowledge the end of the table creation part
print("tables created successfully")

# open new connection to insert data to the tables 
with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        # enable fast_executemany attribute for quicker data pushing
        cursor.fast_executemany = True 
        
        for dir in dirs:
            print("currently processed directory: "+ str(dir))
            files = sorted(Path(dir).glob('*'))
            
            # check if currently processed file has "ccel" string in it
            # if so, compute jerk data; insert data into database
            for file in files:
                
                # check platform and activity name
                if "Apple" in str(file):
                    platform = "apple"
                else:
                    platform = "android"

                if "Upstairs" in str(file):
                    activityName = "upstairs"
                elif "Downstairs" in str(file):
                    activityName = "downstairs"
                elif "Squats" in str(file):
                    activityName = "squats"
                elif "Sitting" in str(file):
                    activityName = "sitting"
                elif "Standing" in str(file):
                    activityName = "standing"
                elif "Lying" in str(file):
                    activityName = "lying"
                elif "Walking" in str(file):
                    activityName = "walking"
                elif "Jogging" in str(file):
                    activityName = "jogging"

                # for each sensor file calculate magnitude and lag; in case of accelerometer add jerk values
                
                if str(file).find("ccel") > 0:
                    activityPackage = os.path.basename(os.path.normpath(file)).replace('.csv', '').replace('Accelerometer', '')
                    print("processing: " + str(file))
                    accDf = pd.read_csv(str(file))
                    
                    jerkM, jerkX, jerkY, jerkZ = jerk(accDf)
                    mJerkDf = pd.DataFrame(jerkM, columns= ["jerkMag"])
                    xJerkDf = pd.DataFrame(jerkX, columns= ["jerkX"])
                    yJerkDf = pd.DataFrame(jerkY, columns= ["jerkY"])
                    zJerkDf = pd.DataFrame(jerkZ, columns= ["jerkZ"])
                    
                    mag = pd.DataFrame(magnitude(accDf), columns=['mag'])
                    
                    platformDf = pd.DataFrame(data=[platform for _ in range(len(mag))], columns=['platform'])
                    activityDf = pd.DataFrame(data=[activityName for _ in range(len(mag))], columns=['activity'])
                    activityPackageDf = pd.DataFrame(data=[activityPackage for _ in range(len(mag))], columns=['activityPackage'])

                    laggerX, laggerY, laggerZ = lag(2, accDf)
                    laggerX.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
                    laggerY.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
                    laggerZ.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)

                    frames = [accDf, mag, laggerX, laggerY, laggerZ, xJerkDf, yJerkDf, zJerkDf, mJerkDf, platformDf, activityDf, activityPackageDf]
                    finalAccDf = pd.concat(frames, axis = 1)

                    sensorTableName = os.path.basename(os.path.normpath(file)).replace('.csv', '')
                    insertQuery = f"INSERT INTO [dbo].[{sensorTableName}] (time, seconds_elapsed, x, y, \
                                    z, mag, lagX0, lagX1, lagX2, lagY0, lagY1, lagY2, lagZ0, \
                                    lagZ1, lagZ2, jerkX, jerkY, jerkZ, jerkMag, platform, activity, activityPackage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                    
                    accTuples = list(finalAccDf.itertuples(index=False))
                    cursor.executemany(insertQuery, accTuples)
                    print("sent: " + str(file))

                elif str(file).find("Gyr") > 0:
                    activityPackage = os.path.basename(os.path.normpath(file)).replace('.csv', '').replace('Gyroscope', '')
                    print("processing: " + str(file))
                    gyrDf = pd.read_csv(str(file))

                    mag = pd.DataFrame(magnitude(gyrDf), columns=['mag'])

                    platformDf = pd.DataFrame(data=[platform for _ in range(len(mag))], columns=['platform'])
                    activityDf = pd.DataFrame(data=[activityName for _ in range(len(mag))], columns=['activity'])
                    activityPackageDf = pd.DataFrame(data=[activityPackage for _ in range(len(mag))], columns=['activityPackage'])
                    
                    laggerX, laggerY, laggerZ = lag(2, gyrDf)
                    laggerX.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
                    laggerY.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
                    laggerZ.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)

                    frames = [gyrDf, mag, laggerX, laggerY, laggerZ, platformDf, activityDf, activityPackageDf]
                    finalGyrDf = pd.concat(frames, axis = 1)

                    sensorTableName = os.path.basename(os.path.normpath(file)).replace('.csv', '')
                    insertQuery = f"INSERT INTO [dbo].[{sensorTableName}] (time, seconds_elapsed, x, y, \
                                    z, mag, lagX0, lagX1, lagX2, lagY0, lagY1, lagY2, lagZ0, \
                                    lagZ1, lagZ2, platform, activity, activityPackage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                    
                    gyrTuples = list(finalGyrDf.itertuples(index=False))
                    cursor.executemany(insertQuery, gyrTuples)
                    print("sent: " + str(file))

                elif str(file).find("Mag") > 0:
                    activityPackage = os.path.basename(os.path.normpath(file)).replace('.csv', '').replace('Magnetometer', '')
                    print("processing: " + str(file))
                    magDf = pd.read_csv(str(file))

                    mag = pd.DataFrame(magnitude(magDf), columns=['mag'])

                    platformDf = pd.DataFrame(data=[platform for _ in range(len(mag))], columns=['platform'])
                    activityDf = pd.DataFrame(data=[activityName for _ in range(len(mag))], columns=['activity'])
                    activityPackageDf = pd.DataFrame(data=[activityPackage for _ in range(len(mag))], columns=['activityPackage'])
                    
                    laggerX, laggerY, laggerZ = lag(2, magDf)
                    laggerX.rename(columns = { "lag 0": "lagX0", "lag 1": "lagX1", "lag 2": "lagX2"}, inplace = True)
                    laggerY.rename(columns = { "lag 0": "lagY0", "lag 1": "lagY1", "lag 2": "lagY2"}, inplace = True)
                    laggerZ.rename(columns = { "lag 0": "lagZ0", "lag 1": "lagZ1", "lag 2": "lagZ2"}, inplace = True)

                    frames = [magDf, mag, laggerX, laggerY, laggerZ, platformDf, activityDf, activityPackageDf]
                    finalMagDf = pd.concat(frames, axis = 1)
                    
                    sensorTableName = os.path.basename(os.path.normpath(file)).replace('.csv', '')
                    insertQuery = f"INSERT INTO [dbo].[{sensorTableName}] (time, seconds_elapsed, x, y, \
                                    z, mag, lagX0, lagX1, lagX2, lagY0, lagY1, lagY2, lagZ0, \
                                    lagZ1, lagZ2, platform, activity, activityPackage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                    
                    magTuples = list(finalMagDf.itertuples(index=False))
                    cursor.executemany(insertQuery, magTuples)
                    print("sent: " + str(file))

            # acknowledge the end of the pushing data in directory
            # commit the changes
            print("processed: " + str(dir))
            conn.commit()
            print("committed")







            
                    

            

    