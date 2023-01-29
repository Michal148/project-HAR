import pyodbc
import pandas as pd 
import os
from kasper.feats import *
from Michał.Characteristics import magnitude
from wiktor.feats import lag
from Orientation import *

driver = os.environ['DBDriver']
server = os.environ['DBServer']
database = os.environ['DBDb']
username = os.environ['DBUser']
password = os.environ['DBPass']

margFolders = [f.path for f in os.scandir("./user-features/streaming-work-dir") if f.is_dir()]
margFiles = []

for folder in margFolders:
    margFiles.append(os.listdir(folder))

with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        for path in margFolders:
            for dirContents in margFiles:
                for file in dirContents:
                    try:
                        tableQuery = f"CREATE TABLE [dbo].[{file.replace('.csv', '')}] ( \
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
                                        [lagZ2]              VARCHAR (MAX) NULL);"
                        cursor.execute(tableQuery)
                    
                        pathString = (path+'/'+file)
                        exportDf = pd.read_csv(pathString)

                        if pathString.find('ccel') > 0:
                            jerkM, jerkX, jerkY, jerkZ = jerk(exportDf)
                            mag = magnitude(exportDf)
                            laggerX, laggerY, laggerZ = lag(3, exportDf)

                            jerkCol = f"ALTER TABLE [dbo].[{file}]  \
                                        ADD jerkZ VARCHAR (MAX) NULL,  \
                                        jerkY VARCHAR (MAX) NULL,  \
                                        jerkX VARCHAR (MAX) NULL,  \
                                        jerkMag VARCHAR (MAX) NULL;"
                            cursor.execute(jerkCol)
                            conn.commit()

                            for id_ in range(len(jerkZ)):
                                insertQuery = f"INSERT INTO [dbo].[{file}] (time, seconds_elapsed, x, y, \
                                                z, mag, lagX0, lagX1, lagX2, lagY0, lagY1, lagY2, lagZ0, \
                                                lagZ1, lagZ2, jerkZ, jerkY, jerkX, jerkMag) VALUES ('{exportDf['time'].iloc[id_]}', '{exportDf['seconds_elapsed'].iloc[id_]}', \
                                                '{exportDf['x'].iloc[id_]}', '{exportDf['y'].iloc[id_]}', '{exportDf['z'].iloc[id_]}', '{mag[id_]}', \
                                                '{laggerX['lag 0'][id_]}', '{laggerX['lag 1'][id_]}', '{laggerX['lag 2'][id_]}', \
                                                '{laggerY['lag 0'][id_]}', '{laggerY['lag 1'][id_]}', '{laggerY['lag 2'][id_]}', \
                                                '{laggerZ['lag 0'][id_]}', '{laggerZ['lag 1'][id_]}', '{laggerZ['lag 2'][id_]}', \
                                                '{jerkZ[id_]}', '{jerkY[id_]}', '{jerkX[id_]}', '{jerkM[id_]}');"
                                cursor.execute(insertQuery)

                            missingQuery =f"INSERT INTO [dbo].[{file}] (time, seconds_elapsed, x, y, \
                                            z, mag, lagX0, lagX1, lagX2, lagY0, lagY1, lagY2, lagZ0, \
                                            lagZ1, lagZ2, jerkZ, jerkY, jerkX, jerkMag) VALUES ('{exportDf['time'].iloc[-1]}', '{exportDf['seconds_elapsed'].iloc[1]}', \
                                            '{exportDf['x'].iloc[-1]}', '{exportDf['y'].iloc[-1]}', '{exportDf['z'].iloc[-1]}', '{mag[-1]}', \
                                            '{laggerX['lag 0'].iloc[-1]}', '{laggerX['lag 1'].iloc[-1]}', '{laggerX['lag 2'].iloc[-1]}', \
                                            '{laggerY['lag 0'].iloc[-1]}', '{laggerY['lag 1'].iloc[-1]}', '{laggerY['lag 2'].iloc[-1]}', \
                                            '{laggerZ['lag 0'].iloc[-1]}', '{laggerZ['lag 1'].iloc[-1]}', '{laggerZ['lag 2'].iloc[-1]}', \
                                            'nan', 'nan', 'nan', 'nan');"

                            cursor.execute(missingQuery)
                            print("successfully uploaded: "+file)
                        
                        else:
                            mag = magnitude(exportDf)
                            laggerX, laggerY, laggerZ = lag(3, exportDf)

                            for id_ in range(len(exportDf)):
                                insertQuery = f"INSERT INTO [dbo].[{file}] (time, seconds_elapsed, x, y, \
                                                z, mag, lagX0, lagX1, lagX2, lagY0, lagY1, lagY2, lagZ0, \
                                                lagZ1, lagZ2) VALUES ('{exportDf['time'].iloc[id_]}', '{exportDf['seconds_elapsed'].iloc[id_]}', \
                                                '{exportDf['x'].iloc[id_]}', {exportDf['y'].iloc[id_]}, '{exportDf['z'].iloc[id_]}', '{mag[id_]}', \
                                                '{laggerX['lag 0'][id_]}', '{laggerX['lag 1'][id_]}', '{laggerX['lag 2'][id_]}', \
                                                '{laggerY['lag 0'][id_]}', '{laggerY['lag 1'][id_]}', '{laggerY['lag 2'][id_]}', \
                                                '{laggerZ['lag 0'][id_]}', '{laggerZ['lag 1'][id_]}', '{laggerZ['lag 2'][id_]}');"
                                cursor.execute(insertQuery)
                            print("successfully uploaded: "+file)

                        conn.commit()
                    except Exception as e:
                        print("file name:"+file)
                        print(e)
                        continue

        for path in margFolders:
            for dirContents in margFiles:
                for file in dirContents:
                    pathString = (path+'/'+file)
                    
                    if pathString.find("ccel") > 1:
                        acc = pathString
                            
                    elif pathString.find("Gyr") > 1:
                        gyr = pathString

                    elif pathString.find("Mag") > 1:
                        mag = pathString
    
            try:
                orient = orientation(acc, mag, gyr)
                timeDf = pd.read_csv(acc).drop('x', axis=1).drop('y', axis=1).drop('z', axis=1)
                tableName = path.split(os.sep)[-1]
                createOrientationTable = f"CREATE TABLE [dbo].[{tableName}] ( \
                                                [time]            BIGINT       NULL, \
                                                [seconds_elapsed] VARCHAR (MAX) NULL, \
                                                [q0]             VARCHAR (MAX) NULL, \
                                                [q1]              VARCHAR (MAX) NULL, \
                                                [q2]              VARCHAR (MAX) NULL, \
                                                [q3]              VARCHAR (MAX) NULL);"
                cursor.execute(createOrientationTable)
                conn.commit()
                
                for iter in range(len(orient)):
                    orientationQuery = f"INSERT INTO [dbo].[{tableName}] (time, seconds_elapsed, q0, q1, \
                                        q2, q3) VALUES ('{timeDf['time'].iloc[iter]}', '{timeDf['seconds_elapsed'].iloc[iter]}', \
                                        '{orient['q0'].iloc[iter]}', '{orient['q1'].iloc[iter]}', '{orient['q2'].iloc[iter]}', '{orient['q3'].iloc[iter]}');"
                    cursor.execute(orientationQuery)

                conn.commit()

            except Exception as e:
                print(e)
                continue