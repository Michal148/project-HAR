import pandas as pd
import warnings
import pywt
import numpy as np
warnings.filterwarnings('ignore')

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

def energy(sig):
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


