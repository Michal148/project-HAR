import pandas as pd
import numpy as np

acc = pd.read_csv('Accelerometer.csv').drop('time', axis=1)
mag = pd.read_csv('Magnetometer.csv').drop('time', axis=1)
orientation = pd.read_csv('Orientation.csv').drop('time', axis=1)


# w razie dziwnych wynikow normalizowac wektory akcelerometra i magnometra (na razie wrecz pogarsza sprawe, moze wina
# braku filtra

def normalize(df):
    result = df.copy()
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result


def quatacc(ax, ay, az):
    if az >= 0:
        matrix = [np.sqrt((az+1)/2), -ay/(np.sqrt(2*(az+1))), ax/(np.sqrt(2*(az+1))), 0]
    else:
        matrix = [-ay/(np.sqrt(2*(1-az))), np.sqrt((1-az)/2), 0, ax/(np.sqrt(2*(1-az)))]
    return np.array(matrix).transpose()


def quatmag(mx, my, mz, qa):
    dmcmatrix = np.array(
        [[qa[0]**2+qa[1]**2-qa[2]**2-qa[3]**2, 2*(qa[1]*qa[2]-qa[0]*qa[3]), 2*(qa[1])*qa[3]+qa[0]*qa[2]],
         [2*(qa[1]*qa[2]+qa[0]*qa[3]), qa[0]**2-qa[1]**2+qa[2]**2-qa[3]**2, 2*(qa[2]*qa[3]-qa[0]*qa[1])],
         [2*(qa[1]*qa[3]-qa[0]*qa[2]), 2*(qa[2]*qa[3]+qa[0]*qa[1]), qa[0]**2-qa[1]**2-qa[2]**2+qa[3]**2]])
    mlocal = np.array([mx, my, mz])
    rotated_mag_field = np.dot(dmcmatrix.transpose(), mlocal.transpose())
    gamma = rotated_mag_field[0] ** 2 + rotated_mag_field[1] ** 2
    if rotated_mag_field[0] >= 0:
        matrix = np.array([np.sqrt((gamma + rotated_mag_field[0] * np.sqrt(gamma)) / np.sqrt(2 * gamma)), 0, 0,
                           rotated_mag_field[1] / np.sqrt(2 * np.sqrt(gamma + rotated_mag_field[0] * np.sqrt(gamma)))])
    else:
        matrix = np.array([rotated_mag_field[1] / np.sqrt(2 * np.sqrt(gamma - rotated_mag_field[0] * np.sqrt(gamma))),
                           0, 0, np.sqrt((gamma - rotated_mag_field[0] * np.sqrt(gamma)) / np.sqrt(2 * gamma))])
    return matrix.transpose()


qac = quatacc(acc['x'][6], acc['y'][6], acc['z'][6])
qmag = quatmag(mag['x'][6], mag['y'][6], mag['z'][6], qac)
# quaterion = qac * qmag
p = qac
q = qmag
quaterion = np.array([p[0]*q[0]-p[1]*q[1]-p[2]*q[2]-p[3]*q[3],
                      p[0]*q[1]+p[1]*q[0]+p[2]*q[3]-p[3]*q[2],
                      p[0]*q[2]-p[1]*q[3]+p[2]*q[0]+p[3]*q[1],
                      p[0]*q[3]+p[1]*q[2]-p[2]*q[1]+p[3]*q[0]])

print(orientation.iloc[[6]])
print(quaterion)
