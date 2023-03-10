import pandas as pd
import numpy as np
import warnings
from Orientation import *
from interpolation import *
from datastandardization import *
from groupTableNames import *
from Feats_columns import *
from Feats_final import *
warnings.filterwarnings('ignore')


# read database credentials
driver = os.environ['DBDriver']
server = os.environ['DBServer']
database = os.environ['DBDb']
username = os.environ['DBUser']
password = os.environ['DBPass']

# read table names and group them
groupedList = groupTables()

clearCols = ['jerkX', 'jerkY', 'jerkZ', 'jerkMag']

# main pipeline loop
for group in groupedList:
    # create database table refereneces for queries
    accTableName = f'[dbo].[{group[0]}]'
    gyrTableName = f'[dbo].[{group[1]}]'
    magTableName = f'[dbo].[{group[2]}]'

    # open connection to database, import sensors data
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            accDownloadQuery = f"SELECT * FROM {accTableName}"
            accTable = pd.read_sql(accDownloadQuery, conn)
            accTable[clearCols] = accTable[clearCols].replace({'n.n':np.nan})
            accTable = accTable.sort_values('time')

            gyrDownloadQuery = f"SELECT * FROM {gyrTableName}"
            gyrTable = pd.read_sql(gyrDownloadQuery, conn)
            gyrTable = gyrTable.sort_values('time')

            magDownloadQuery = f"SELECT * FROM {magTableName}"
            magTable = pd.read_sql(magDownloadQuery, conn)
            magTable = magTable.sort_values('time')

        cursor.close()
    conn.close()


    # if platform is android, convert to ios units
    accTable = ios_conversion(accTable)

    # data interpolation
    interpAcc, interpMag, interpGyr = interpolation(accTable, magTable, gyrTable)
    
    interpAcc.to_csv(f"Interpolation{group[0]}.csv")
    interpMag.to_csv(f"Interpolation{group[1]}.csv")
    interpGyr.to_csv(f"Interpolation{group[2]}.csv")

    # orientation
    orientationDf = orientation(interpAcc, interpMag, interpGyr)
    joinedDfs = orientationDf.join(interpAcc, how='outer')
    exportOrientation = joinedDfs[['time', 'q0', 'q1', 'q2', 'q3']]
    
    exportOrientation.to_csv(f"Orientation{group[0].replace('Accelerometer', '')}.csv")

    # data segmentation
    segList = [interpAcc, interpMag, interpGyr]

    try:
        for idx, seg in enumerate(segList):
            windows = []
            seg = seg[['time', 'x', 'y', 'z']]
            df_len = len(seg)

            # head and tail cut-off seconds
            head = 5
            tail = 5

            # select range based on head and tail seconds
            # adj is used to cut off signal at good point
            range_df = seg.iloc[head*100:df_len-tail*100]
            adj = len(range_df)%500
            
            for i in range(df_len-tail*100-adj):
                if i % 500 == 0:    
                    currSeg = range_df.iloc[i:i+501].reset_index(False).drop(columns = ['index'])
                    window_feat = feats_df(currSeg)
                    windows.append(window_feat)

            currDf = pd.concat(windows)
            if idx == 0:
                currDf.to_csv(f"Features{group[0]}.csv")
                print(f"Completed: Features{group[0]}.csv")

            elif idx == 1:
                currDf.to_csv(f"Features{group[1]}.csv")
                print(f"Completed: Features{group[1]}.csv")

            else:
                currDf.to_csv(f"Features{group[2]}.csv")
                print(f"Completed: Features{group[2]}.csv")

    except:
        continue


