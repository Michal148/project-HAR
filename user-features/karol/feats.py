import numpy as np
import pandas as pd
import math
from scipy import fftpack
df = pd.read_csv("Accelerometer.csv")
df = df.drop(['time', 'seconds_elapsed'], axis=1)


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


# Calculating fft from signal and converting resulting list into data frame
def fourier(data, freq=100):
    n = len(data)
    fs = freq
    freq_vec = [fs/n * x for x in range(n)]
    dff = pd.DataFrame(np.abs(fftpack.fft(data)))
    dff.columns = ['x', 'y', 'z']
    return freq_vec, dff


# Calculating interquartile range
def iqr(dataf):
    cols = ['x', 'y', 'z']
    lst = []
    vec, dataff = fourier(dataf)

    for col in cols:
        q1 = np.percentile(dataff[col].sort_values(), 25, method='midpoint')
        q3 = np.percentile(dataff[col].sort_values(), 75, method='midpoint')
        lst.append(q1-q3)
    return lst



# Calculating Mean Power Frequency
def mpf(dataf):
    fvec, dff = fourier(dataf)
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        value = sum(p * f for p in dff[col] for f in fvec) / sum(p for p in dff[col])
        lst.append(value)
    return lst


# Calculating one quarter of frequency (especially needs revision)
def one_quarter(dataf):
    fvec, dff = fourier(dataf)
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        value = sum(p for p in dff[col].iloc[int(0.25*len(dff)):])
        lst.append(value)
    return lst


# Calculating three quarters of frequency (needs a revison)
def three_quarters(dataf):
    fvec, dff = fourier(dataf)
    cols = ['x', 'y', 'z']
    lst = []
    for col in cols:
        value = sum(p for p in dff[col].iloc[0:int(0.75 * len(dff))])
        lst.append(value)
    return lst

print(three_quarters(df))