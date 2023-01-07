import pandas as pd
import warnings
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
                    tempListX.append(sig['x'][iter - 1])
                    tempListY.append(sig['y'][iter - 1])
                    tempListZ.append(sig['z'][iter - 1])

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


