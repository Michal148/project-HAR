# Based on
# [1] Valenti, R.G.; Dryanovski, I.; Xiao, J.
# Keeping a Good Attitude: A Quaternion-Based Orientation Filter for IMUs and MARGs.
# Sensors 2015, 15, 19302-19330. https://doi.org/10.3390/s150819302

import pandas as pd
import numpy as np


# min/max normalization of inputs
def normalize(df):
    result = df.copy()
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result


# acceleration quaternion calculation, based on Equation (25) from [1]
def quatacc(ax, ay, az):
    if az >= 0:
        matrix = [np.sqrt((az+1)/2), -ay/(np.sqrt(2*(az+1))), ax/(np.sqrt(2*(az+1))), 0]
    else:
        matrix = [-ay/(np.sqrt(2*(1-az))), np.sqrt((1-az)/2), 0, ax/(np.sqrt(2*(1-az)))]
    return np.array(matrix).transpose()


# magnetometer quaternion calculation, based on Equations (26), (28), (35) from [1]
def quatmag(mx, my, mz, qa):
    dmcmatrix = rotation(qa)
    mlocal = np.array([mx, my, mz])
    # Equation (26)
    rotated_mag_field = np.dot(dmcmatrix.transpose(), mlocal.transpose())
    # Equation(28)
    gamma = rotated_mag_field[0] ** 2 + rotated_mag_field[1] ** 2

    # Equation(35)
    if rotated_mag_field[0] >= 0:
        matrix = np.array([np.sqrt((gamma + rotated_mag_field[0] * np.sqrt(gamma)) / np.sqrt(2 * gamma)), 0, 0,
                           rotated_mag_field[1] / np.sqrt(2 * np.sqrt(gamma + rotated_mag_field[0] * np.sqrt(gamma)))])
    else:
        matrix = np.array([rotated_mag_field[1] / np.sqrt(2 * np.sqrt(gamma - rotated_mag_field[0] * np.sqrt(gamma))),
                           0, 0, np.sqrt((gamma - rotated_mag_field[0] * np.sqrt(gamma)) / np.sqrt(2 * gamma))])
    return matrix.transpose()


# multiplication of two quaternions, based on Equation (4) from [1]
def quatmult(p, q):
    quaternion = np.array([p[0]*q[0]-p[1]*q[1]-p[2]*q[2]-p[3]*q[3],
                           p[0]*q[1]+p[1]*q[0]+p[2]*q[3]-p[3]*q[2],
                           p[0]*q[2]-p[1]*q[3]+p[2]*q[0]+p[3]*q[1],
                           p[0]*q[3]+p[1]*q[2]-p[2]*q[1]+p[3]*q[0]])

    return quaternion


# rotating quaternion, based on equation (9) from [1]
def rotation(qa):
    dmcmatrix = np.array([[qa[0] ** 2 + qa[1] ** 2 - qa[2] ** 2 - qa[3] ** 2,
                           2 * (qa[1] * qa[2] - qa[0] * qa[3]),
                           2 * (qa[1]) * qa[3] + qa[0] * qa[2]],
                          [2 * (qa[1] * qa[2] + qa[0] * qa[3]),
                           qa[0] ** 2 - qa[1] ** 2 + qa[2] ** 2 - qa[3] ** 2,
                           2 * (qa[2] * qa[3] - qa[0] * qa[1])],
                          [2 * (qa[1] * qa[3] - qa[0] * qa[2]),
                           2 * (qa[2] * qa[3] + qa[0] * qa[1]),
                           qa[0] ** 2 - qa[1] ** 2 - qa[2] ** 2 + qa[3] ** 2]])

    return dmcmatrix

# compute inverse quaternion
def inverse(q):
    for i in range(1,4):
        q[i] = -q[i]

    return q


# loading data from sensors
acc = normalize(pd.read_csv('Accelerometer.csv').drop('time', axis=1).drop('seconds_elapsed', axis=1))
mag = normalize(pd.read_csv('Magnetometer.csv').drop('time', axis=1).drop('seconds_elapsed', axis=1))
gyr = pd.read_csv('Gyroscope.csv').drop('time', axis=1).drop('seconds_elapsed', axis=1)
# orientation = pd.read_csv('Orientation.csv').drop('time', axis=1).drop('seconds_elapsed', axis=1)

# sampling time
dt = 0.01

# epsilon value mentioned between Equations (49) and (50) in [1]
threshold = 0.01

# identity quaternion, based on Equation (49) in from [1]
quat_id = np.array([1, 0, 0, 0]).transpose()

# alpha and beta parameters mentioned between Equations (50) and (51)  as well as before Equation (59) in [1]
alpha = 0.01
beta = 0.01

# filter loop, testing for first 100 records
for id_ in range(100):
    # for prediction step of filter, we take quaternion created by the first readings from
    # accelerometer and magnetometer during first iteration
    if id_ == 0:
        qac = quatacc(acc['x'][0], acc['y'][0], acc['z'][0])
        qmag = quatmag(mag['x'][0], mag['y'][0], mag['z'][0], qac)
        q_t_1 = quatmult(qac, qmag)
    else:
        q_t_1 = q_t

    # compute the first derivative of q quaternion using qyroscope data, based on Equation (38) from [1]
    q_prim = np.array([0, -0.5 * gyr['x'][id_ + 1], -0.5 * gyr['y'][id_ + 1], -0.5 * gyr['z'][id_ + 1]])
    q_der = quatmult(q_prim, q_t_1)

    # compute quaternion for current time step, using numerical integration, based on Equation (42) from [1]
    q_t = q_t_1 + np.array([q_der[0] * dt, q_der[1] * dt, q_der[2] * dt, q_der[3] * dt])

    # create local acceleration vector used for predicted gravity vector, based on Equation (44) from [1]
    a = np.array([acc['x'][id_ + 1], acc['y'][id_ + 1], acc['z'][id_ + 1]])
    gp = np.dot(rotation(inverse(q_t)), a)

    # compute delta quaternion, based on Equation (47) from [1]
    delta_q_acc = np.array(
        [np.sqrt((gp[2]+1)/2), -gp[1]/np.sqrt(2*(gp[2]+1)), gp[0]/np.sqrt(2*(gp[2]+1)), 0]).transpose()

    # cosine of omega, as in Equation (48) in [1]
    cos_omega = np.dot(quat_id, delta_q_acc)

    # if .. else based on Equations (50) and (51) from [1]
    if cos_omega > threshold:
        delta_q_line = (1 - alpha) * quat_id + alpha * delta_q_acc
        norm_nums = np.sqrt(delta_q_line[0]**2 + delta_q_line[1]**2 + delta_q_line[2]**2 + delta_q_line[3]**2)
        norm_delta_q = np.array([delta_q_line[0]/norm_nums, delta_q_line[1]/norm_nums, delta_q_line[2]/norm_nums, delta_q_line[3]/norm_nums])
    else:
        omega = np.arccos(cos_omega)
        norm_delta_q = np.sin((1 - alpha) * omega)/np.sin(omega) * quat_id + np.sin(alpha * omega)/np.sin(omega) * delta_q_acc

    # quaternion estimated from gyroscope data is multiplied by the filtered delta quaternion, based on Equation (53) from [1]
    q_apostrophe = quatmult(q_t, norm_delta_q)

    # create magnetic vector used for predicted magnetic field vector, based on Equation (54) from [1]
    m = np.array([mag['x'][id_ + 1], mag['y'][id_ + 1], mag['z'][id_ + 1]])
    l_ = np.dot(rotation(inverse(q_apostrophe)), m)

    # compute gamma, based on Equation (28) from [1]
    gamma = l_[0]**2 + l_[1]**2

    # compute delta quaternion, based on Equation (58) from [1]
    delta_q_mag = np.array(
        [np.sqrt(gamma+l_[0]*np.sqrt(gamma))/np.sqrt(2*gamma), 0, 0,
         l_[1]/np.sqrt(2*(gamma+l_[0]*np.sqrt(gamma)))]).transpose()

    # init another branch of filter - magnetometer based as mentioned below Equation (58) from [1]
    cos_omega_mag = np.dot(quat_id, delta_q_mag)

    # magnetometer if .. else based on Equations (50) and (51) from [1]
    if cos_omega_mag > threshold:
        delta_q_line = (1 - beta) * quat_id + beta * delta_q_mag
        norm_nums = np.sqrt(delta_q_line[0]**2 + delta_q_line[1]**2 + delta_q_line[2]**2 + delta_q_line[3]**2)
        norm_delta_q = np.array([delta_q_line[0]/norm_nums, delta_q_line[1]/norm_nums, delta_q_line[2]/norm_nums, delta_q_line[3]/norm_nums])
    else:
        omega = np.arccos(cos_omega_mag)
        norm_delta_q = np.sin((1 - beta) * omega)/np.sin(omega) * quat_id + np.sin(beta * omega)/np.sin(omega) * delta_q_mag

    # final quaternion after accelerometer and magnetometer correction, based on Equation (59) from [1]
    q_t = quatmult(q_apostrophe, norm_delta_q)
    print(q_t)
