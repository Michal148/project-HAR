import numpy as np
import math
import pandas as pd
from scipy import signal
import warnings
import pywt
import statsmodels.api as sm
from antropy import spectral_entropy

warnings.filterwarnings('ignore')

global gg
gg = []



def fft_sig(sig, fs=100):
    n = len(sig)
    frequency_vector = np.arange(0, fs, fs / n)
    com_fft = np.abs(np.fft.fft(sig)) / n
    com_fft[1:int(np.ceil(n / 2) + 1)] = com_fft[1:int(np.ceil(n / 2) + 1)] * 2
    com_fft[int(np.ceil(n / 2) + 1):].fill(0)

    return frequency_vector, com_fft


# --------------------------------------------------- frequency ------------------------------------------------------ #


# Time and frequency
# Kurtosis
def kurtosis(data):
    kurtosis_value = []
    global gg

    datawt = data
    for l in ['t', 'f']:
        for n in datawt.columns:
            gg.append(f"acc_{n}_kurtosis_{l}")

    for n in datawt.columns:
        length = len(data[n])
        mean_value = sum(data[n]) / length
        std = (sum((var - mean_value) ** 2 for var in data[n]) / length) ** 0.5
        kurt = (sum((var - mean_value) ** 4 for var in data[n]) / (length * std ** 4))
        kurtosis_value.append(kurt)

    for n in datawt.columns:
        ff, ffv = fft_sig(data[n])
        lengthf = len(ffv)
        meanf = sum(ffv) / lengthf
        stdf = (sum((var - meanf) ** 2 for var in ffv) / lengthf) ** 0.5
        kurtf = (sum((var - meanf) ** 4 for var in ffv) / (lengthf * stdf ** 4))
        kurtosis_value.append(kurtf)

    return kurtosis_value


# Time and frequency
# Skewness
def skewness(data):
    skewness_value = []
    global gg
    datawt = data
    for l in ['t', 'f']:
        for n in datawt.columns:
            gg.append(f"acc_{n}_skewness_{l}")

    for col in datawt.columns:
        n = len(data[col])
        mean_value = sum(data[col]) / n
        std = (sum((x - mean_value) ** 2 for x in data[col]) / n) ** 0.5
        skew = (sum((x - mean_value) ** 3 for x in data[col]) / (n * std ** 3))
        skewness_value.append(skew)

    for col in datawt.columns:
        ff, ffv = fft_sig(data[col])
        nf = len(ffv)
        meanf = sum(ffv) / nf
        std = (sum((x - meanf) ** 2 for x in ffv) / nf) ** 0.5
        skew = (sum((x - meanf) ** 3 for x in ffv) / (nf * std ** 3))
        skewness_value.append(skew)

    return skewness_value


# Energy wavelet coefficient
def enwatco(data):
    enwatco_value = []
    datawt = data
    for n in datawt.columns:

        db = pywt.Wavelet('sym4')
        decomp = pywt.dwt_max_level(len(data), db) + 1
        x_vec = [None] * decomp
        x_vec = pywt.wavedec(data[n], db)
        energy_x = []

        for row in range(decomp):
            energy_x.append(np.sqrt(np.sum(np.array(x_vec[row][-decomp]) ** 2)) / len(x_vec[-decomp]))
        enwatco_value.append(energy_x)

    n = len(enwatco_value[0])
    for m in ['z', 'y', 'x']:

        for i in range(1, n + 1):
            gg.append(f"acc_{m}_enwacto_{i}")

    enwacto_final = [*enwatco_value[0], *enwatco_value[1], *enwatco_value[2]]

    return enwacto_final


# Top 3 value
def top3(data):
    sig = np.sum(data.loc[:, ['x', 'y', 'z']], axis=1)
    frequency_sampling = 100
    n = len(sig)
    frequency_vector = np.arange(0, frequency_sampling, frequency_sampling / n)
    com_fft = np.abs(np.fft.fft(sig)) / n
    com_fft[1:int(np.ceil(n / 2) + 1)] = com_fft[1:int(np.ceil(n / 2) + 1)] * 2
    com_fft[int(np.ceil(n / 2) + 1):].fill(0)

    _, abs_fft_modified = frequency_vector, com_fft
    peaks_modified, _ = signal.find_peaks(abs_fft_modified, height=0)
    top3_value = np.in1d(abs_fft_modified, np.sort(abs_fft_modified[peaks_modified])[-3:]).nonzero()[0]
    global gg
    datawt = data
    for n in datawt.columns:
        gg.append(f"acc_{n}_top3")

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
    global gg
    datawt = data
    for n in datawt.columns:
        gg.append(f"acc_{n}_median_frequency")
        _, m = fft_sig(data[n])
        _, c = medianenergy(m)
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
    global gg
    datawt = data
    for col in datawt.columns:
        minim = min(data[col])
        maxim = max(data[col])
        p2p_value.append(maxim - minim)
        gg.append(f"acc_{col}_p2p")

    return p2p_value


# Mean absolute value
def mav(data):
    mav_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        mean_sum = sum(abs(x) for x in data[col])
        mav_value.append(mean_sum)
        gg.append(f"acc_{col}_mav")

    return mav_value


# Waveform length
def wf(data):
    wf_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        n = len(data[col])
        waveform = 0

        for i in range(n - 1):
            waveform += abs(data[col][i + 1] - data[col][i])
        wf_value.append(waveform)
        gg.append(f"acc_{col}_wf")

    return wf_value


# Log detector
def logdetect(data):
    logdetect_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        n = len(data[col])
        logdetect_value.append(math.exp(sum(math.log10(abs(x)) for x in data[col]) * 1 / n))
        gg.append(f"acc_{col}_logdetect")

    return logdetect_value


# Zero crossing
def zerocr(data):
    zerocr_value = []
    global gg
    datawt = data
    for n in datawt.columns:
        zero_crossinga = np.where(np.diff(np.sign(data[n])))[0]
        zc1 = len(zero_crossinga)
        zerocr_value.append(zc1)
        gg.append(f"acc_{n}_zerocr")

    return zerocr_value


# Median absolute deviation
def mad(data):
    mad_value = []
    global gg
    datawt = data
    for n in datawt.columns:
        median_number = np.median(data[n])
        mad1 = np.median([abs(var - median_number) for var in data[n]])
        mad_value.append(mad1)
        gg.append(f"acc_{n}_mad")

    return mad_value


# Mean value
def mean(data):
    mean_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        value = sum(data[col]) / len(data[col])
        mean_value.append(value)
        gg.append(f"acc_{col}_mean")

    return mean_value


# Standard deviation
def stdev(data, correction=1):
    stdev_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        n = len(data[col])
        value = sum(data[col]) / n
        dev = sum((x - value) ** 2 for x in data[col]) / (n - correction)
        stdev_value.append(dev)
        gg.append(f"acc_{col}_stdev")

    return stdev_value


# Root mean square
def rms(data):
    rms_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        n = len(data[col])
        value = math.sqrt(sum(x ** 2 for x in data[col]) / n)
        rms_value.append(value)
        gg.append(f"acc_{col}_rms")

    return rms_value


# Energy
def energy(data):
    energy_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        n = len(data[col])
        value = sum(abs(x) ** 2 for x in data[col]) / n
        energy_value.append(value)
        gg.append(f"acc_{col}_energy")

    return energy_value


# Slope sign change
def slope_change(data):
    change = 0
    slope_change_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        change = 0

        for i in range(1, len(data)):

            if np.sign(data[col][i]) != np.sign(data[col][i - 1]):
                change += 1

        slope_change_value.append(change)
        gg.append(f"acc_{col}_slope_change")

    return slope_change_value


# 4th order auto regressive coefficient
def autoregyw(data):
    autoregyw_value = []

    global gg
    datawt = data
    for col in datawt.columns:
        a, sigma = sm.regression.yule_walker(data[col], order=4)
        autoregyw_value.append(a)

        for i in range(1, 5):
            gg.append(f"acc_{col}_autoregyw_{i}")

    autoregyw_value_final = [*autoregyw_value[0], *autoregyw_value[1], *autoregyw_value[2]]

    return autoregyw_value_final


# Auto-regression coefficients with Burg order equal to four correlation coefficients between two signals
def autoregburg(data):
    autoregburg_value = []
    global gg
    datawt = data
    for col in datawt.columns:
        a, _ = sm.regression.linear_model.burg(data[col], order=4)
        autoregburg_value.append(a)

        for i in range(1, 5):
            gg.append(f"acc_{col}_autoregburg_{i}")

    autoregburg_value_final = [*autoregburg_value[0], *autoregburg_value[1], *autoregburg_value[2]]

    return autoregburg_value_final


# Signal magnitude area
def sma(data):
    n = len(data)
    x = data['x']
    y = data['y']
    z = data['z']
    sma_value = 0
    global gg
    gg.append("acc_mpf")

    for i in range(n):
        sma_value += np.abs(x[i]) + np.abs(y[i]) + np.abs(z[i])

    return sma_value / n


# Correlation coefficient
def corecoef(data):
    ccxy = np.corrcoef(data['x'], data['y'])
    ccxz = np.corrcoef(data['x'], data['z'])
    ccyz = np.corrcoef(data['y'], data['z'])
    datawt = data
    for i in datawt.columns:
        gg.append(f"acc_{i}_corecoef")

    return ccxy[1, 0], ccxz[1, 0], ccyz[1, 0]


# Cross correlation between axes
def crossco(data):
    global gg
    corrxy = np.correlate(data['x'], data['y'])
    corrxz = np.correlate(data['x'], data['z'])
    corryz = np.correlate(data['y'], data['z'])

    datawt = data
    for i in datawt.columns:
        gg.append(f"acc_{i}_crossco")

    return corrxy[0], corrxz[0], corryz[0]


# Wilson amplitude
def wilson_amp(data, t=0.05):
    cols = ['x', 'y', 'z']
    wa = []
    for col in cols:
        gg.append(f"acc_{col}_wilson_amp")
        n = len(data[col])
        amp = 0

        for i in range(n - 1):
            amp += np.sign(abs(data[col][i + 1] - data[col][i]) - t)

        wa.append(amp)

    return wa


# Interquartile range
def iqr(dataf):
    iqr_value = []
    global gg 
    q1 = one_quarter(dataf, flag=False)
    q3 = three_quarters(dataf, flag=False)
    for i in range(len(q1)):
        iqr_value.append(q3[i] - q1[i])

    datawt = dataf
    for i in datawt.columns:
        gg.append(f"acc_{i}_iqr")

    return iqr_value


# Three quarters of frequency
def three_quarters(data, flag=True):
    three_quarters_value = []
    global gg
    datawt = data
    for i in datawt.columns:
        fvec, dff = fft_sig(data[i])
        arr = np.cumsum(dff)
        norm_arr = arr / arr[-1]

        for j in range(1, len(arr)):

            if norm_arr[j] < 0.75:
                continue

            if round(norm_arr[j], 2) >= 0.75:
                three_quarters_value.append(fvec[j])

                gg.append(f"acc_{i}_three_quarters") if flag == True else None
                break
    return three_quarters_value


# One quarter of frequency
def one_quarter(data, flag=True):
    one_quarter_values = []
    global gg
    datawt = data
    for i in datawt.columns:

        fvec, dff = fft_sig(data[i])
        arr = np.cumsum(dff)
        norm_arr = arr / arr[-1]

        for j in range(1, len(arr)):

            if norm_arr[j] < 0.25:
                continue

            if round(norm_arr[j], 2) >= 0.25:
                one_quarter_values.append(fvec[j])
                gg.append(f"acc_{i}_one_quarter") if flag == True else None
                break

    return one_quarter_values


# Mean power frequency
def mpf(data):
    mean_power_frequency = []
    datawt = data

    global gg

    for i in datawt.columns:
        gg.append(f"acc_{i}_mpf")
        fvec, dff = fft_sig(data[i])
        value = np.sum(np.multiply(dff, fvec)) / np.sum(dff)
        mean_power_frequency.append(value)

    return mean_power_frequency


# Entropy
def entropy(data):
    global gg
    entropy_value = []
    datawt = data
    for i in datawt.columns:
        gg.append(f"acc_{i}_entropy")
        val = spectral_entropy(data[i], sf=100, method='fft')
        entropy_value.append(val)

    return entropy_value


def feats_df(data):
    global gg

    try:
        mpf_ = (*mpf(data), *iqr(data), *wilson_amp(data), *crossco(data), *three_quarters(data), *one_quarter(data),
                *corecoef(data), sma(data), *slope_change(data), *rms(data), *stdev(data), *mean(data), *mad(data),
                *zerocr(data), *wf(data), *mav(data), *p2p(data), *median_frequency(data), *entropy(data),
                *kurtosis(data), *skewness(data), *top3(data),
                *autoregyw(data), *autoregburg(data), *enwatco(data)
                )

        data_frame = pd.DataFrame([mpf_], columns=[*gg])
        gg = []
        return data_frame
    except Exception as err:
        gg = []
        print("=====")
        print(err)
        print("=====")
        return None


def windowing(data, l):
    curr_df = pd.DataFrame(columns=[*gg])
    n = len(data)

    # head and tail cut-off seconds
    head = 0
    tail = 9

    # select range based on head and tail seconds
    # adj is used to cut off signal at good point
    dp = data.iloc[head * 100:n - tail * 100]
    a = len(dp)

    # window size
    v = round(l) * 100
    b = a % v

    dd = pd.DataFrame()
    for i in range(0, n - tail * 100 - b, v):
        dd = dp.iloc[i:i + v + 1].reset_index(False)
        window_feat = feats_df(dd)
        curr_df = pd.concat([window_feat, curr_df])

    return dd



