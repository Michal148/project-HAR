import pandas as pd
import warnings
import pywt
import numpy as np
warnings.filterwarnings('ignore')
import statsmodels.api as sm


def lag(N, sig):
    colNames = ['lag ' + str(el) for el in range(N + 1)]
    laggedDfX = pd.DataFrame(columns=colNames)
    laggedDfY = pd.DataFrame(columns=colNames)
    laggedDfZ = pd.DataFrame(columns=colNames)
    iter = 0
    for mag in range(len(sig)):
        tempListX = []
        tempListY = []
        tempListZ = []
        tempListX.append(sig['x'][mag])
        tempListY.append(sig['y'][mag])
        tempListZ.append(sig['z'][mag])

        if mag < N:
            if iter > 0:
                for i in range(iter):
                    tempListX.append(sig['x'][iter - i - 1])
                    tempListY.append(sig['y'][iter - i - 1])
                    tempListZ.append(sig['z'][iter - i - 1])

            for i in range(N - mag):
                tempListX.append(None)
                tempListY.append(None)
                tempListZ.append(None)
            
        else:
            for i in range(N):
                tempListX.append(sig['x'][mag - i - 1])
                tempListY.append(sig['y'][mag - i - 1])
                tempListZ.append(sig['z'][mag - i - 1])

        laggedDfX = laggedDfX.append(pd.Series(tempListX, index=laggedDfX.columns[:len(tempListX)]), ignore_index=True)
        laggedDfY = laggedDfY.append(pd.Series(tempListY, index=laggedDfY.columns[:len(tempListY)]), ignore_index=True)
        laggedDfZ = laggedDfZ.append(pd.Series(tempListZ, index=laggedDfZ.columns[:len(tempListZ)]), ignore_index=True)
        iter += 1
 
    return laggedDfX, laggedDfY, laggedDfZ

def energyWaveletCoeff(sig):
    sigX = sig['x']
    sigY = sig['y']
    sigZ = sig['z']

    db = pywt.Wavelet('sym4')
    decomp= pywt.dwt_max_level(len(sig), db) + 1

    xVec = [None] * decomp
    yVec = [None] * decomp
    zVec = [None] * decomp

    xVec = pywt.wavedec(sigX, db)
    yVec = pywt.wavedec(sigY, db)
    zVec = pywt.wavedec(sigZ, db)

    energyX = []
    energyY = []
    energyZ = []

    for row in range(decomp):
        energyX.append(np.sqrt(np.sum(np.array(xVec[row][-decomp]) ** 2)) / len(xVec[-decomp]))
        energyY.append(np.sqrt(np.sum(np.array(yVec[row][-decomp]) ** 2)) / len(yVec[-decomp]))
        energyZ.append(np.sqrt(np.sum(np.array(zVec[row][-decomp]) ** 2)) / len(zVec[-decomp]))

    return energyX, energyY, energyZ

def wilsonAmp(data, T):
    cols = ['x', 'y', 'z']
    WA = []
    for col in cols:
        N = len(data[col])
        amp = 0
        
        for i in range(N - 1):
            amp += np.sign(abs(data[col][i + 1] - data[col][i]) - T)
        
        WA.append(amp)

    return WA

def sma(data):
    N=len(data)
    x=data['x']
    y=data['y']
    z=data['z']
    sma=0
    for i in range(N):
        sma += np.abs(x[i]) + np.abs(y[i]) + np.abs(z[i])

    return sma

def fftMag(sig):
    sig['mag'] = np.sqrt(sig['x']**2 + sig['y']**2 + sig['z']**2)
    N = len(sig['mag'])
    fs = 100
    
    #window = signal.get_window('hanning', N)
    #sig['mag'] = sig['mag'] * window

    freqVec = [fs/N * x for x in range(N)]
    sigMag = np.abs((np.fft.fft(sig['mag'].to_numpy())))
    
    return freqVec, sigMag

def slopeChange(sig):
    change = 0
    cols = ['x', 'y', 'z']
    signList = []
    for col in cols:
        change = 0
        
        for i in range(1, len(sig)):
            if np.sign(sig[col][i]) != np.sign(sig[col][i - 1]):
                change += 1
        
        signList.append(change)

    return signList

def fft_top3(data):
    N = len(data)

    fs = 100
    freq_vec = [fs/N * x for x in range(N)]
    freq_vec.sort()
    top3v = freq_vec[-1:-4:-1]

    return top3v


def autoregyw(data):
    for col in data.columns:
        a, sigma = sm.regression.yule_walker(data[col], order=4)
        predicted = list(data[col].values[0:4])
        for i in range(4, data[col].shape[0]-1):
            predicted.append(np.sum(np.multiply(a, predicted[i-4:i])))

    return predicted


def autoregburg(data):
    for col in data.columns:
        a, sigma = sm.regression.linear_model.burg(data[col], order=4)
        predicted_1 = list(data[col].values[0:4])
        for i in range(4, data[col].shape[0]-1):
            predicted_1.append(np.sum(np.multiply(a, predicted_1[i - 4:i])))

    return predicted_1
