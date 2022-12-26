import pandas as pd
#from scipy.stats import skew # prawdopodbnie do wyjebania
import numpy as np
#import matplotlib.pyplot as plt # do wyjebania
import math
from scipy import signal

# skewness
def skewness(data):
    N = len(data)
    mean = sum(data)/N
    std = (sum((x - mean) ** 2 for x in data) / N) ** 0.5
    skew = (sum((x - mean) ** 3 for x in data) / (N * std ** 3))

    return skew

# peak to peak
def p2p(data):
    minim = min(data)
    maxim = max(data)

    return maxim - minim

# mean absolute value
def mav(data):
    N = len(data)
    mean_sum = sum(abs(x) for x in data)
    
    return mean_sum/N

# waveform length
def wf(data):
    N = len(data)
    waveform = 0

    for i in range(N-1):
        waveform += abs(data[i + 1] - data[i])

    return waveform

# log detector
def logdetect(data):
    N = len(data)

    return math.exp(sum(math.log10(abs(x)) for x in data) * 1/N)

# jerk, return resultant jerk, as well as from X, Y, Z
def jerk(data):
    N = len(data)
    cols = ['x', 'y', 'z']
    jerk = []
    jerk_x = []
    jerk_y = []
    jerk_z = []

    for i in range(1, N):
        temp_jerk = 0

        for col in cols:
            temp_jerk += (data[col][i] - data[col][i - 1]) ** 2

        jerk.append(0.5 * temp_jerk)

        jerk_x.append(0.5 * ((data['x'][i] - data['x'][i - 1]) ** 2))
        jerk_y.append(0.5 * ((data['y'][i] - data['y'][i - 1]) ** 2))
        jerk_z.append(0.5 * ((data['z'][i] - data['z'][i - 1]) ** 2))

    return jerk, jerk_x, jerk_y, jerk_z

# calculate fft from signal, possible window usage
def fftSig(data):
    N = len(data)
    #window = signal.get_window('hanning', N)
    #data = data * window
    fs = 100
    freq_vec = [fs/N * x for x in range(N)]

    return freq_vec, np.abs((np.fft.fft(data.to_numpy())))

# sigA and sigB are signals from axes, wFilt is a maximum filter length, 
# wShift is a shift between each iteration of filtering
def haar(sigA, sigB, wFilt, wShift):
    # length of the signal
    length = len(sigA)
    
    # check the length of window and based on that, set the interval for
    # the creation of window list
    if wFilt > 200:
        interval = 20
    else:
        interval = 10

    # create window list and an empty features list
    widthList = [x for x in range(10, wFilt, interval)]
    featList = []

    # main loop, iterate through window list
    for width in widthList:
        # equation (8) from paper
        N = int((length - wFilt)/wShift + 1)
        
        # variable used for storing absolute difference between axes
        axesSum = 0

        # first sigma from paper, equation (9)
        for n in range(N):
            pointTempA = 0
            pointTempB = 0

            # sigmas inside the absolute value in equation (9)
            for k in range(width):
                if k < width/2:
                    pointTempA -= sigA[n*wShift + k]
                    pointTempB += sigB[n*wShift + k]
                else:
                    pointTempA += sigA[n*wShift + k]
                    pointTempB -= sigB[n*wShift + k]

            # add asbsolut difference from current iteration
            axesSum += np.abs(pointTempA - pointTempB)

        # append the final feature value to the list 
        featList.append(axesSum)     

    return featList   