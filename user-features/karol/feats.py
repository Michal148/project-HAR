import numpy as np
import pandas as pd
import math
from scipy import fftpack
import matplotlib.pyplot as plt
# df = pd.read_csv("Accelerometer.csv")
# df = df.drop(['time', 'seconds_elapsed'], axis=1)


# Calculating mean value
def mean(dataf):
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        value = sum(dataf[col])/len(dataf[col])
        lst.append(value)
    return lst


# Calculating standard deviation
def stdev(dataf, correction=1):
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        n = len(dataf[col])
        value = sum(dataf[col]) / n
        dev = sum((x - value) ** 2 for x in dataf[col]) / (n - correction)
        lst.append(dev)
    return lst


# Calculating Root Mean Square
def rms(dataf):
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        n = len(dataf[col])
        value = math.sqrt(sum(x**2 for x in dataf[col])/n)
        lst.append(value)
    return lst


# Calculating energy
def energy(dataf):
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        n = len(dataf[col])
        value = sum(abs(x)**2 for x in dataf[col])/n
        lst.append(value)
    return lst


# Calculating fft from signal
def fourier(data, freq=100):
    arr = pd.DataFrame.to_numpy(data)
    arr = np.transpose(arr)
    n = len(arr[0])
    fs = freq
    lst = []
    fvec = [fs / n * x for x in range(int(n / 2))]
    for i in range(len(arr)):
        fur = np.abs(fftpack.fft(arr[i]) / n)
        fur = fur[:int(n / 2)]
        fur[1:-1] = fur[1:-1]
        lst.append(fur)
    return fvec, lst


# Calculating Mean Power Frequency
def mpf(dataf):
    fvec, dff = fourier(dataf)
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        value = sum(p * f for p in dff[col] for f in fvec) / sum(p for p in dff[col])
        lst.append(value)
    return lst


# Calculating one quarter of frequency (needs a check)
def one_quarter(dataf):
    fvec, dff = fourier(dataf)
    fvec = np.array(fvec)
    lst = []
    for i in range(len(dff)):
        arr = np.cumsum(dff[i])
        norm_arr = arr / arr[-1]
        for j in range(1, len(arr)):
            if norm_arr[j] < 0.25:
                continue
            if round(norm_arr[j],2) >= 0.25:
                lst.append(fvec[j])
                break
    return lst


# Calculating three quarters of frequency (needs a check)
def three_quarters(dataf):
    fvec, dff = fourier(dataf)
    fvec = np.array(fvec)
    lst = []
    for i in range(len(dff)):
        arr = np.cumsum(dff[i])
        norm_arr = arr / arr[-1]
        for j in range(1, len(arr)):
            if norm_arr[j] < 0.75:
                continue
            if round(norm_arr[j], 2) >= 0.75:
                lst.append(fvec[j])
                break
    return lst


# Calculating interquartile range (needs a check)
def iqr(dataf):
    cols = ['x', 'y', 'z']
    lst = []
    q1 = one_quarter(dataf)
    q3 = three_quarters(dataf)
    for i in range(len(q1)):
        lst.append(q3[i] - q1[i])
    return lst


