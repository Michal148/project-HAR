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

feat_col = ['z_mpf', 'y_mpf', 'x_mpf', 'z_one_quarter',
                                   'y_one_quarter',
                                   'x_one_quarter', 'z_three_quarters', 'y_three_quarters',
                                   'x_three_quarters', 'z_iqr', 'y_iqr', 'x_iqr', 'z_wilson_amp',
                                   'y_wilson_amp', 'x_wilson_amp', 'z_crossco', 'y_crossco',
                                   'x_crossco', 'z_corecoef', 'y_corecoef', 'x_corecoef', 'sma',
                                   'z_slope_change', 'y_slope_change', 'x_slope_change', 'z_rms',
                                   'y_rms', 'x_rms', 'z_stdev', 'y_stdev', 'x_stdev', 'z_mean',
                                   'y_mean', 'x_mean', 'z_mad', 'y_mad', 'x_mad', 'z_zerocr',
                                   'y_zerocr', 'x_zerocr', 'z_logdetect', 'y_logdetect',
                                   'x_logdetect', 'z_wf', 'y_wf', 'x_wf', 'z_mav', 'y_mav',
                                   'x_mav', 'z_p2p', 'y_p2p', 'x_p2p', 'z_median_frequency',
                                   'y_median_frequency', 'x_median_frequency', 'z_entropy', 'y_entropy',
                                   'x_entropy', 'z_kurtosis_t', 'y_kurtosis_t', 'x_kurtosis_t',
                                   'z_kurtosis_f', 'y_kurtosis_f', 'x_kurtosis_f', 'z_skewness_t',
                                   'y_skewness_t', 'x_skewness_t', 'z_skewness_f', 'y_skewness_f',
                                   'x_skewness_f', 'z_top3', 'y_top3', 'x_top3', 'z_autoregyw_1',
                                   'z_autoregyw_2', 'z_autoregyw_3', 'z_autoregyw_4', 'y_autoregyw_1',
                                   'y_autoregyw_2', 'y_autoregyw_3', 'y_autoregyw_4', 'x_autoregyw_1',
                                   'x_autoregyw_2', 'x_autoregyw_3', 'x_autoregyw_4', 'z_autoregburg_1',
                                   'z_autoregburg_2', 'z_autoregburg_3', 'z_autoregburg_4',
                                   'y_autoregburg_1', 'y_autoregburg_2', 'y_autoregburg_3',
                                   'y_autoregburg_4', 'x_autoregburg_1', 'x_autoregburg_2',
                                   'x_autoregburg_3', 'x_autoregburg_4']

# read database credentials
driver = os.environ['DBDriver']
server = os.environ['DBServer']
database = os.environ['DBDb']
username = os.environ['DBUser']
password = os.environ['DBPass']

# read table names and group them
# groupedList = groupTables()

# DELETE
groupedList = [['AccelerometerKarolDownstairs', 'GyroscopeKarolDownstairs', 'MagnetometerKarolDownstairs'], 
              ['AccelerometerKarolDownstairs2', 'GyroscopeKarolDownstairs2', 'MagnetometerKarolDownstairs2']]

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

    for idx, seg in enumerate(segList):
        currDf = pd.DataFrame(columns=feat_col)
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
                currSeg = range_df.iloc[i:i+501].reset_index(False)
                window_feat = feats_df(currSeg)
                currDf = pd.concat([window_feat, currDf])

        if idx == 0:
            currDf.to_csv(f"Features{group[0]}.csv")

        elif idx == 1:
            currDf.to_csv(f"Features{group[1]}.csv")

        else:
            currDf.to_csv(f"Features{group[2]}.csv")





