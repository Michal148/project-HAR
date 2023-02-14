import numpy as np
import math
import pandas as pd
import scipy.stats as ss
from scipy.fft import fft, fftfreq
from scipy import signal
import warnings
import pywt
import statsmodels.api as sm
warnings.filterwarnings('ignore')


def lag(n, sig):
    col_names = ['lag ' + str(el) for el in range(n + 1)]
    lagged_df_x = pd.DataFrame(columns=col_names)
    lagged_df_y = pd.DataFrame(columns=col_names)
    lagged_df_z = pd.DataFrame(columns=col_names)
    iter_ = 0
    for mag in range(len(sig)):
        temp_list_x = []
        temp_list_y = []
        temp_list_z = []
        temp_list_x.append(sig['x'][mag])
        temp_list_y.append(sig['y'][mag])
        temp_list_z.append(sig['z'][mag])

        if mag < n:

            if iter_ > 0:
                for i in range(iter_):
                    temp_list_x.append(sig['x'][iter_ - i - 1])
                    temp_list_y.append(sig['y'][iter_ - i - 1])
                    temp_list_z.append(sig['z'][iter_ - i - 1])

            for i in range(n - mag):
                temp_list_x.append(None)
                temp_list_y.append(None)
                temp_list_z.append(None)

        else:

            for i in range(n):
                temp_list_x.append(sig['x'][mag - i - 1])
                temp_list_y.append(sig['y'][mag - i - 1])
                temp_list_z.append(sig['z'][mag - i - 1])

        lagged_df_x = lagged_df_x.append(pd.Series(temp_list_x, index=lagged_df_x.columns[:len(temp_list_x)]),
                                         ignore_index=True)
        lagged_df_y = lagged_df_y.append(pd.Series(tempListY, index=lagged_df_y.columns[:len(temp_list_y)]),
                                         ignore_index=True)
        lagged_df_z = lagged_df_z.append(pd.Series(temp_list_z, index=lagged_df_z.columns[:len(temp_list_z)]),
                                         ignore_index=True)
        iter_ += 1

    return lagged_df_x, lagged_df_y, lagged_df_z


# jerk, return resultant jerk, as well as from X, Y, Z
def jerk(data):
    n = len(data['x'])
    cols = ['x', 'y', 'z']
    jerk1 = []
    jerk_x = []
    jerk_y = []
    jerk_z = []

    for i in range(1, n):
        temp_jerk = 0

        for col in cols:
            temp_jerk += (data[col][i] - data[col][i - 1]) ** 2

        jerk1.append(0.5 * temp_jerk)
        jerk_x.append(0.5 * ((data['x'][i] - data['x'][i - 1]) ** 2))
        jerk_y.append(0.5 * ((data['y'][i] - data['y'][i - 1]) ** 2))
        jerk_z.append(0.5 * ((data['z'][i] - data['z'][i - 1]) ** 2))

    return jerk1, jerk_x, jerk_y, jerk_z


def magnitude(data):
    length = len(data)
    mag = []
    for i in range(length):
        mag_wynik = np.sqrt(data['x'][i]**2 + data['y'][i]**2 + data['z'][i]**2)
        mag.append(mag_wynik)

    return mag
