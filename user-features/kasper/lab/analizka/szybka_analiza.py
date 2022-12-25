#!/usr/bin/env python
# coding: utf-8

# In[20]:


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


# In[32]:


total = pd.read_csv("TotalAcceleration(1).csv")
total.tail()


# In[33]:


uncal = pd.read_csv("AccelerometerUncalibrated(1).csv")
uncal.tail()


# In[44]:


#plt.xcorr(total["z"], uncal["z"], usevlines=False, maxlags=5, normed=True, lw=5)
plt.grid(True)
plt.title("Cross-correlation")


# In[34]:


total = total[2:]
uncal = uncal[:-2]


# In[36]:


new_x = total["x"] - uncal["x"]
new_y = total["y"] - uncal["y"]
new_z = total["z"] - uncal["z"]
new_mag = np.sqrt(total["x"]**2+total["y"]**2+total["z"]**2) - np.sqrt(uncal["x"]**2+uncal["y"]**2+uncal["z"]**2)


# In[45]:
fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(18, 10))

ax[0,0].plot(new_x, label='x')
ax[0,1].plot(new_y, label='y')
ax[0,2].plot(new_z, label='z')
ax[1,0].plot(new_mag, label='mag diff')
ax[1,1].plot(total["z"], label='total z')
ax[1,2].plot(uncal["z"], label='uncal z')
ax[0,0].set_title("x roznice")
ax[0,1].set_title("y roznice")
ax[0,2].set_title("z roznice")
ax[1,0].set_title("amplituda roznice")
ax[1,1].set_title("total z")
ax[1,2].set_title("uncal z")

ax[0,0].ticklabel_format(useOffset=False)
#print(new_z)
plt.show()
# In[ ]:
new_x.to_csv('guwnio.csv')




