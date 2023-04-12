import numpy as np
from math import log, e
import pandas as pd
import scipy.stats as ss
from scipy.fft import fft, fftfreq
from scipy import signal
import statistics as stat

# changing time signal to frequency
def fft_sig(data):
    length = len(data)

    fs = 100
    freq_vec = [fs/length * var for var in range(length)]
    window = signal.get_window('flattop', length)

    return freq_vec, np.abs((np.fft.fft(data.to_numpy()*window)))

# time
def zero_crossing(data):
    zc = []
    for n in ['x', 'y', 'z']:
        zero_crossinga = np.where(np.diff(np.sign(data[n])))[0]
        zc.append(zero_crossinga)
    return zc

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

# frequency
def entropy(data, base=None):
    entr = []
    for n in ['x', 'y', 'z']:
        ff, ffv = fft_sig(data[n])
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

# median_frequency
def energy(data):

    energy_df = pd.DataFrame(data)
    length = len(energy_df)
    if length % 2 != 0:
        length -= 1
    energy_arr = []
    total_energy = 0

    for i in range(int(length / 2)):
        temp_energy = np.abs(energy_df[0][i]) ** 2
        energy_arr.append(temp_energy)
        total_energy += temp_energy
    total_energy = total_energy / (length / 2)

    return total_energy, energy_arr


# time
def median_absolute_deviation(data):
    mad1 = []
    for n in ['x', 'y', 'z']:
        median_number = np.median(data[n])
        mad = np.median([abs(var - median_number) for var in data[n]])
        mad1.append(mad)

    return mad1

# signal
def magnitude(data):
    length = len(data)
    mag = []
    for i in range(length):
        mag_wynik = np.sqrt(data['x'][i]**2 + data['y'][i]**2 + data['z'][i]**2)
        mag.append(mag_wynik)

    return mag

# time
def corelation_coefficient(data):
    ccxy = np.corrcoef(data['x'], data['y'])
    ccxz = np.corrcoef(data['x'], data['z'])
    ccyz = np.corrcoef(data['y'], data['z'])

    return ccxy[1, 0], ccxz[1, 0], ccyz[1, 0]


# time
def cross_corelation(data):
    corrxy = np.correlate(data['x'], data['y'])
    corrxz = np.correlate(data['x'], data['z'])
    corryz = np.correlate(data['y'], data['z'])

    return corrxy[0], corrxz[0], corryz[0]















