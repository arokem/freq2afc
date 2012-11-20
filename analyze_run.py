import sys

from matplotlib.mlab import csv2rec
import matplotlib.pyplot as plt
import numpy as np

import analysis_utils as a

if __name__=="__main__":

    path_to_files = '/Volumes/Plata1/Shared/Ariel/fiorentini_data/'
    file_name =  sys.argv[1]
    p,l,data_rec = a.get_data('%s/%s'%(path_to_files,file_name))
    fix_idx = np.where(data_rec['task']=='fixation')

    per_idx = np.where(data_rec['task']=='periphery')
    fix_idx = np.where(data_rec['task']=='fixation')
    c = data_rec['correct']
    amp = data_rec['contrast']

    th_per = a.analyze(amp[per_idx],c[per_idx])
    th_fix = a.analyze(amp[fix_idx],c[fix_idx])

    x,y = th_per[4],th_per[5]
    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    ax.plot(x,y,'o')
    x_for_plot = np.linspace(np.min(x),np.max(x),100)

    ax.plot(x_for_plot,a.weibull(x_for_plot,th_per[0],th_per[3]))

    fig.suptitle('Periphery task:thresh=%1.2f, slope=%1.2f'%(th_per[0],th_per[3]))

    staircase = amp[per_idx]

    ax = fig.add_subplot(1,2,2)

    ax.plot(staircase,'o-')
    

    fig = plt.figure()
    ax = fig.add_subplot(1,2,1)
    ax.plot(x,y,'o')
    x_for_plot = np.linspace(np.min(x),np.max(x),100)

    ax.plot(x_for_plot,a.weibull(x_for_plot,th_fix[0],th_fix[3]))

    fig.suptitle('Fixation task:thresh=%1.2f, slope=%1.2f'%(th_fix[0],th_fix[3]))

    staircase = amp[fix_idx]

    ax = fig.add_subplot(1,2,2)

    ax.plot(staircase,'o-')
