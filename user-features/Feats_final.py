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
data = pd.read_csv('Accelerometer.csv')


def fft_sig(signal, fs=100):
    n = len(signal)
    frequency_vector = np.arange(0, fs, fs / n)
    com_fft = np.abs(np.fft.fft(signal)) / n
    com_fft[1:int(np.ceil(n/2)+1)] = com_fft[1:int(np.ceil(n/2) + 1)] * 2
    com_fft[int(np.ceil(n/2)+1):].fill(0)

    return frequency_vector, com_fft


# --------------------------------------------------- frequency ------------------------------------------------------ #


# Time and frequency
# Kurtosis
def kurtosis(data):
    kurtosis_value = []
    kurtosis_value_freq = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for n in datawt.columns:
        length = len(data[n])
        mean_value = sum(data[n]) / length
        std = (sum((var - mean_value) ** 2 for var in data[n]) / length) ** 0.5
        kurt = (sum((var - mean_value) ** 4 for var in data[n]) / (length * std ** 4))
        kurtosis_value.append(kurt)

        ff, ffv = fft_sig(data[n])
        lengthf = len(ffv)
        meanf = sum(ffv) / lengthf
        stdf = (sum((var - meanf) ** 2 for var in ffv) / lengthf) ** 0.5
        kurtf = (sum((var - meanf) ** 4 for var in ffv) / (lengthf * stdf ** 4))
        kurtosis_value_freq.append(kurtf)

    return kurtosis_value, kurtosis_value_freq


# Time and frequency
# Skewness
def skewness(data):
    skewness_value_time = []
    skewness_value_freq = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        n = len(data[col])
        mean_value = sum(data[col]) / n
        std = (sum((x - mean_value) ** 2 for x in data[col]) / n) ** 0.5
        skew = (sum((x - mean_value) ** 3 for x in data[col]) / (n * std ** 3))
        skewness_value_time.append(skew)

        ff, ffv = fft_sig(data[col])
        nf = len(ffv)
        meanf = sum(ffv) / nf
        std = (sum((x - meanf) ** 2 for x in ffv) / nf) ** 0.5
        skew = (sum((x - meanf) ** 3 for x in ffv) / (nf * std ** 3))
        skewness_value_freq.append(skew)

    return skewness_value_time, skewness_value_freq


# Energy wavelet coefficient
def enwatco(sig):
    enwatco_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for n in datawt.columns:
        db = pywt.Wavelet('sym4')
        decomp = pywt.dwt_max_level(len(sig), db) + 1
        x_vec = [None] * decomp
        x_vec = pywt.wavedec(sig[n], db)
        energy_x = []

        for row in range(decomp):
            energy_x.append(np.sqrt(np.sum(np.array(x_vec[row][-decomp]) ** 2)) / len(x_vec[-decomp]))
        enwatco_value.append(energy_x)

    return enwatco_value


# Entropy
def entropy(data, base=None):
    entropy_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for n in datawt.columns:
        ff, ffv = fft_sig(data[n])
        n_labels = len(ffv)

        if n_labels <= 1:
            return 0
        _, counts = np.unique(ffv, return_counts=True)
        probs = counts / n_labels
        n_classes = np.count_nonzero(probs)

        if n_classes <= 1:
            return 0
        ent = 0.
        base = math.e if base is None else base

        for i in probs:
            ent -= i * math.log(i, base)
        entropy_value.append(ent)

    return entropy_value


# Top 3 value
def top3(data):
    signal = np.sum(data.loc[:, ['x', 'y', 'z']], axis=1)
    frequency_sampling = np.sum(np.array(data['seconds_elapsed'] < 1).astype(int))/1

    n = len(signal)
    frequency_vector = np.arange(0, frequency_sampling, frequency_sampling / n)
    com_fft = np.abs(np.fft.fft(signal)) / n
    com_fft[1:int(np.ceil(n / 2) + 1)] = com_fft[1:int(np.ceil(n / 2) + 1)] * 2
    com_fft[int(np.ceil(n / 2) + 1):].fill(0)

    _, abs_fft_modified = frequency_vector, com_fft
    peaks_modified, _ = signal.find_peaks(abs_fft_modified, height=0)
    top3_value = np.in1d(abs_fft_modified, np.sort(abs_fft_modified[peaks_modified])[-3:]).nonzero()[0]

    return top3_value


# Energy needed to median frequency
def medianenergy(data):
    energy_df = pd.DataFrame(data)
    n = len(energy_df)
    if n % 2 != 0:
        n -= 1
    energy_arr = []
    total_energy = 0

    for i in range(int(n / 2)):
        temp_energy = np.abs(energy_df[0][i]) ** 2
        energy_arr.append(temp_energy)
        total_energy += temp_energy
    total_energy = total_energy / n

    return total_energy, energy_arr


# Median frequency
def median_frequency(data):
    median_frequency_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for n in datawt.columns:
        f, m = fft_sig(data[n])
        a, c = medianenergy(m)
        n = len(c)
        prev_bep = int(n / 2)
        bep = int(n / 2)
        counter = 2
        prev_diff = 10e12
        rep_count = 0
        prev_left = 10e13

        while True:
            sum_left = sum(x for x in c[:bep])
            sum_right = sum(y for y in c[bep:])

            if sum_left < sum_right:
                bep = prev_bep + int(n / (2 ** counter))

            elif sum_left > sum_right:
                bep = prev_bep - int(n / (2 ** counter))

            else:
                break

            curr_diff = np.abs(sum_right - sum_left)

            if sum_left == prev_left:
                rep_count += 1

            if rep_count == 10:
                break

            if curr_diff >= 15 * prev_diff:
                break

            else:
                prev_bep = bep
                prev_diff = curr_diff
                counter += 1
                prev_left = sum_left
        median_frequency_value.append(prev_bep)
    return median_frequency_value


# ------------------------------------------------------ time -------------------------------------------------------- #


# Peak to peak
def p2p(data):
    p2p_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        minim = min(data[col])
        maxim = max(data[col])
        p2p_value.append(maxim - minim)

    return p2p_value


# Mean absolute value
def mav(data):
    mav_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:

        mean_sum = sum(abs(x) for x in data[col])
        mav_value.append(mean_sum)

    return mav_value


# Waveform length
def wf(data):
    wf_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        n = len(data[col])
        waveform = 0

        for i in range(n - 1):
            waveform += abs(data[col][i + 1] - data[col][i])
        wf_value.append(waveform)

    return wf_value


# Log detector
def logdetect(data):
    logdetect_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        n = len(data[col])
        logdetect_value.append(math.exp(sum(math.log10(abs(x)) for x in data[col]) * 1 / n))

    return logdetect_value


# Zero crossing
def zerocr(data):
    zerocr_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for n in datawt.columns:
        zero_crossinga = np.where(np.diff(np.sign(data[n])))[0]
        zc1 = len(zero_crossinga)
        zerocr_value.append(zc1)

    return zerocr_value


# Median absolute deviation
def mad(data):
    mad_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for n in datawt.columns:
        median_number = np.median(data[n])
        mad1 = np.median([abs(var - median_number) for var in data[n]])
        mad_value.append(mad1)

    return mad_value


# Mean value
def mean(dataf):
    mean_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        value = sum(dataf[col]) / len(dataf[col])
        mean_value.append(value)

    return mean_value


# Standard deviation
def stdev(dataf, correction=1):
    stdev_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        n = len(dataf[col])
        value = sum(dataf[col]) / n
        dev = sum((x - value)**2 for x in dataf[col]) / (n - correction)
        stdev_value.append(dev)

    return stdev_value


# Root mean square
def rms(dataf):
    rms_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        n = len(dataf[col])
        value = math.sqrt(sum(x**2 for x in dataf[col])/n)
        rms_value.append(value)

    return rms_value


# Energy
def energy(dataf):
    energy_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        n = len(dataf[col])
        value = sum(abs(x)**2 for x in dataf[col])/n
        energy_value.append(value)

    return energy_value


# Slope sign change
def slope_change(sig):
    change = 0
    slope_change_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        change = 0

        for i in range(1, len(sig)):

            if np.sign(sig[col][i]) != np.sign(sig[col][i - 1]):
                change += 1

        slope_change_value.append(change)

    return slope_change_value


# 4th order auto regressive coefficient
def autoregyw(data):
    autoregyw_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for col in datawt.columns:
        a, sigma = sm.regression.yule_walker(data[col], order=4)
        autoregyw_value.append(a)

    return autoregyw_value


# Auto-regression coefficients with Burg order equal to four correlation coefficients between two signals
def autoregburg(data):
    autoregburg_value = []
    for col in data.columns:
        a, _ = sm.regression.linear_model.burg(data[col], order=4)
        autoregburg_value.append(a)

    return autoregburg_value


# Signal magnitude area
def sma(data):
    N = len(data)
    x = data['x']
    y = data['y']
    z = data['z']
    sma_value = 0
    for i in range(N):
        sma += np.abs(x[i]) + np.abs(y[i]) + np.abs(z[i])

    return sma_value / N


# Correlation coefficient
def corecoef(data):
    ccxy = np.corrcoef(data['x'], data['y'])
    ccxz = np.corrcoef(data['x'], data['z'])
    ccyz = np.corrcoef(data['y'], data['z'])

    return ccxy[1, 0], ccxz[1, 0], ccyz[1, 0]


# Cross correlation between axes
def crossco(data):
    corrxy = np.correlate(data['x'], data['y'])
    corrxz = np.correlate(data['x'], data['z'])
    corryz = np.correlate(data['y'], data['z'])

    return corrxy[0], corrxz[0], corryz[0]


# Wilson amplitude
def wilson_amp(data, t=0):
    cols = ['x', 'y', 'z']
    wa = []
    for col in cols:
        n = len(data[col])
        amp = 0

        for i in range(n - 1):
            amp += np.sign(abs(data[col][i + 1] - data[col][i]) - t)

        wa.append(amp)

    return wa


# Interquartile range
def iqr(dataf):
    iqr_value = []
    q1 = one_quarter(dataf)
    q3 = three_quarters(dataf)
    for i in range(len(q1)):
        iqr_value.append(q3[i] - q1[i])

    return iqr_value


# Three quarters of frequency
def three_quarters(data):
    three_quarters_value = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for i in datawt.columns:
        fvec, dff = fft_sig(data[i])
        arr = np.cumsum(dff)
        norm_arr = arr / arr[-1]

        for j in range(1, len(arr)):

            if norm_arr[j] < 0.75:
                continue

            if round(norm_arr[j], 2) >= 0.75:
                three_quarters_value.append(fvec[j])
                break
    return three_quarters_value


# One quarter of frequency
def one_quarter(data):
    one_quarter_values = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for i in datawt.columns:
        fvec, dff = fft_sig(data[i])
        arr = np.cumsum(dff)
        norm_arr = arr / arr[-1]

        for j in range(1, len(arr)):

            if norm_arr[j] < 0.25:
                continue

            if round(norm_arr[j], 2) >= 0.25:
                one_quarter_values.append(fvec[j])
                break

    return one_quarter_values


# Mean power frequency
def mpf(data):
    mean_power_frequency = []
    datawt = data.drop(['time', 'seconds_elapsed'], axis=1)
    for i in datawt.columns:
        fvec, dff = fft_sig(data[i])
        value = sum(p * f for p in dff for f in fvec) / sum(p for p in dff)
        mean_power_frequency.append(value)

    return mean_power_frequency



