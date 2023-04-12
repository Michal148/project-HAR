import pandas as pd
import numpy as np
import math
from scipy import signal


# skewness
def skewness(data):
    cols = ['x', 'y', 'z']
    featList = []

    for col in cols:
        N = len(data[col])
        mean = sum(data[col])/N
        std = (sum((x - mean) ** 2 for x in data[col]) / N) ** 0.5
        skew = (sum((x - mean) ** 3 for x in data[col]) / (N * std ** 3))
        featList.append(skew)

    return featList

# peak to peak
def p2p(data):
    cols = ['x', 'y', 'z']
    featList = []

    for col in cols:
        minim = min(data[col])
        maxim = max(data[col])
        featList.append(maxim - minim)

    return featList

# mean absolute value
def mav(data):
    cols = ['x', 'y', 'z']
    featList = []
    
    for col in cols:
        N = len(data[col])
        mean_sum = sum(abs(x) for x in data[col])
        featList.append(mean_sum)
    
    return featList

# waveform length
def wf(data):
    cols = ['x', 'y', 'z']
    featList = []
    
    for col in cols:
        N = len(data[col])
        waveform = 0

        for i in range(N-1):
            waveform += abs(data[col][i + 1] - data[col][i])

        featList.append(waveform)

    return featList

# log detector
def logdetect(data):
    cols = ['x', 'y', 'z']
    featList = []

    for col in cols:
        N = len(data[col])
        featList.append(math.exp(sum(math.log10(abs(x)) for x in data[col]) * 1/N))

    return featList

# jerk, return resultant jerk, as well as from X, Y, Z
def jerk(data):
    N = len(data['x'])
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
def haar(data, wFilt, wShift):
    # length of the signal
    comb = [['x', 'y'], ['x', 'z'], ['y', 'z']]

    length = len(data['x'])
    # check the length of window and based on that, set the interval for
    # the creation of window list

    if wFilt > 200:
        interval = 20
    else:
        interval = 10

    # create window list and an empty features list
    widthList = [x for x in range(10, wFilt, interval)]
    featList = []

    for i in range(3):
        featListTemp = []
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
                        pointTempA -= data[comb[i][0]][n*wShift + k]
                        pointTempB += data[comb[i][1]][n*wShift + k]
                    else:
                        pointTempA += data[comb[i][0]][n*wShift + k]
                        pointTempB -= data[comb[i][1]][n*wShift + k]

                # add asbsolut difference from current iteration
                axesSum += np.abs(pointTempA - pointTempB)

            # append the final feature value to the list 
            featListTemp.append(axesSum)     
        
        # append temporary list to final list containing three axes
        featList.append(featListTemp)
    
    return featList   