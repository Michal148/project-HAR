import numpy as np
from math import log, e
import pandas as pd
import scipy.stats as ss
from scipy.fft import fft, fftfreq
from scipy import signal
import statistics as stat
import matplotlib.pyplot as plot
import time as tim


t0 = tim.time()

a2 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
da = pd.read_csv('Accelerometer.csv')
x = da['x']
y = da['y']
z = da['z']
time = da['time']


# changing time signal to frequency
def fftSig(data):
    N = len(data)
    fs = 100
    freq_vec = [fs/N * x for x in range(N)]
    window = signal.get_window('flattop', N)

    return freq_vec, np.abs((np.fft.fft(data.to_numpy()*window)))

f, fv = fftSig(y)


# time
def zero_crossing(data):

    zero_crossinga = np.where(np.diff(np.sign(data)))[0]

    return zero_crossinga
#print(zero_crossing(x))


# time and frequency
def kurtosis1(data):

    kurto = []
    for n in ['x', 'y', 'z']:
        length = len(data[n])
        mean = sum(data[n]) / length
        std = (sum((var - mean) ** 2 for var in data[n]) / length) ** 0.5
        kurt = (sum((var - mean) ** 4 for var in data[n]) / (length * std ** 4))

        kurto.append(kurt)

    return kurto
#print(kurtosis1(da))


# frequency
def entropy(data, base=None):

    entr = []
    for n in ['x', 'y', 'z']:
        ff, ffv = fftSig(data[n])
        n_labels = len(ffv)

        if n_labels <= 1:
            return 0
        value, counts = np.unique(ffv, return_counts=True)
        probs = counts / n_labels
        n_classes = np.count_nonzero(probs)

        if n_classes <= 1:
            return 0
        ent = 0.
        # Compute entropy
        base = e if base is None else base

        for i in probs:
            ent -= i * log(i, base)
        entr.append(ent)

    return entr
#print(entropy(da))


#median_frequency
def energy(data):

    energyDf = pd.DataFrame(data)
    N = len(energyDf)
    if N % 2 != 0:
        N -= 1
    energyArr = []
    totalEnergy = 0
    for i in range(int(N / 2)):
        tempEnergy = np.abs(energyDf[0][i]) ** 2
        energyArr.append(tempEnergy)
        totalEnergy += tempEnergy
    totalEnergy = totalEnergy / (N / 2)

    return totalEnergy, energyArr


# time
def median_absolute_deviation(data):

    mad1 = []
    for n in ['x', 'y', 'z']:
        median_number = np.median(data[n])
        mad = np.median([abs(var - median_number) for var in data[n]])
        mad1.append(mad)

    return mad1
#print(median_absolute_deviation(da))


# signal
def magnitude(data):

    length = len(data)
    mag = []
    for i in range(length):
        mag_wynik = np.sqrt(x[i]**2 + y[i]**2 + z[i]**2)
        mag.append(mag_wynik)

    return mag
#print(magnitude(da))





#do zobacnie jaki błąd w formule
#def cross_corelation(data, data1):
#    N = len(data)
#    mean_x = sum(data) / N
#    mean_y = sum(data1) / N
#    cc = sum(((x - mean_x) * (y - mean_y)) for x, y in data, data1)
#    ccm = np.sqrt(sum((x - mean_x)**2 for x in data)) * (sum((y - mean_y)**2 for y in data1))
#    ccn = cc / ccm
#    return ccn
#pl = cross_corelation(x,y)
#print(pl)


# time
def corelation_coefficient(data):
    mad1 = []
    for n in range(1:4):
        arr = ['x','y','z']
        ccxy = np.corrcoef(data[arr(n)], data[arr(n+1)])
        ccxz = np.corrcoef(data['x'], data['z'])
        ccyz = np.corrcoef(data['y'], data['z'])
    return ccxy[1, 0], ccxz[1, 0], ccyz[1, 0]


# time
def cross_corelation(data):
    corrxy = np.correlate(data['x'], data['y'])
    corrxz = np.correlate(data['x'], data['z'])
    corryz = np.correlate(data['y'], data['z'])
    return corrxy[0], corrxz[0], corryz[0]




# time calculating
t1 = tim.time()
total = t1-t0
print('czas to', total)











