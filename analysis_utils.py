import numpy as np
from matplotlib.mlab import csv2rec
from scipy.optimize import leastsq

def weibull(x,threshx,slope,guess=0.5,flake=0.99,threshy=None):
    if threshy is None:
        threshy = 1-(1-guess)*np.exp(-1)

    k = (-np.log( (1-threshy)/(1-guess) ))**(1/slope)
    weib = flake - (flake-guess)*np.exp(-(k*x/threshx)**slope)
    return weib 


def get_data(file_name):
    file_read = file(file_name,'r')
    l = file_read.readline()
    p = {} #This will hold the params
    l = file_read.readline()
    data_rec = []
    
    if l=='':
        return p,l,data_rec

    while l[0]=='#':
        try:
            p[l[1:l.find(':')-1]]=float(l[l.find(':')+1:l.find('\n')]) 

        #Not all the parameters can be cast as float (the task and the
        #subject): 
        except:
            p[l[2:l.find(':')-1]]=l[l.find(':')+1:l.find('\n')]

        l = file_read.readline()

    try:
        data_rec = csv2rec(file_name)
    except ValueError:
        p = []
    
    return p,l,data_rec

def analyze(amp,correct,n_up=3,guess=0.5,flake=0.01,slope=3.5,fig_name=None,
            bootstrap_n=1000):
    """
    Perform a psychometric curve analysis of the data in the staircase and
    save a figure, if needed.

    Parameters
    ----------

    guess: The expected hit rate when the subject is blind-folded (default:
    0.5)

    flake: The expected rate of misses on trials on which the subjects
    should actually succeed, if they are really doing the task (default: 0.1)

    slope: The slope of the psychometric curve at the inflection point
    (default to 3.5)

    fig_name: string
       A file name for saving a figure. If none provided, don't save the
       generated figure

    bootstrap_n: int
       The number of boot samples to take for the bootstrapping analysis

    Note
    ----

    The fitting procedure is applied to the slope, as well as to the
    threshold.

    """
    def weibull(x,threshx,slope,guess,flake,threshy=None):
            if threshy is None:
                threshy = 1-(1-guess)*np.exp(-1)

            k = (-np.log( (1-threshy)/(1-guess) ))**(1/slope)
            weib = flake - (flake-guess)*np.exp(-(k*x/threshx)**slope)
            return weib 

    def get_thresh(amp,c):
        """Calculate a threshold given amp, c(orrect) values  """ 
        #Helper functions for fitting the psychometric curve, need to be
        #defined within the local scope, so that they can grok the data:

        def weib_fit(pars):
            thresh,slope = pars
            return weibull(x,thresh,slope,guess,flake)

        def err_func(pars):
            return y-weib_fit(pars)

        #Throw away the None's:
        hit_amps = amp[c==1]
        miss_amps = amp[c==0]

        all_amps = np.hstack([hit_amps,miss_amps])
        stim_intensities = np.unique(all_amps)

        n_correct = [len(np.where(hit_amps==i)[0]) for i in stim_intensities]
        n_trials = [len(np.where(all_amps==i)[0]) for i in stim_intensities]
        Data = zip(stim_intensities,n_correct,n_trials)
        x = []
        y = []
        n = []
        for idx,this in enumerate(Data):
            #Take only cases where there were at least n_up observations:
            if n_trials[idx]>=n_up:
                #Contrast values: 
                x = np.hstack([x,this[2] * [this[0]]])
                #% correct:
                y = np.hstack([y,this[2] * [this[1]/float(this[2])]])

        initial = np.mean(x),slope
        this_fit , msg = leastsq(err_func,initial)
        return this_fit,x,y

    #Convert the flake into the expected format for the weibull function:
    flake = 1-flake
    amp = np.array(amp) 
    c = np.array(correct)
    this_fit,keep_x,keep_y = get_thresh(amp,c)
    #print keep_x
    #print keep_y

    bootstrap_th = []
    bootstrap_slope = []
    keep_amp = amp
    keep_c = c
    keep_slope = this_fit[1]
    keep_th = this_fit[0]
    for b in xrange(bootstrap_n):
        b_idx = np.random.randint(0,c.shape[0],c.shape[0])
        amp = keep_amp[b_idx]
        c = keep_c[b_idx]
        this_fit,x,y = get_thresh(amp,c)
        bootstrap_th.append(this_fit[0])

    upper = np.sort(bootstrap_th)[bootstrap_n*0.975]
    lower = np.sort(bootstrap_th)[bootstrap_n*0.025]

    #Make a figure, if required:
    if fig_name is not None: 
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        for idx,this_x in enumerate(keep_x):
            n = np.sum(keep_x==this_x) # How many trials, sets the
                                        # markersize
            ax.plot(this_x,keep_y[idx],'o',color = 'b',markersize = n)

        x_for_plot = np.linspace(np.min(keep_x)-0.05,np.max(keep_x)+0.05,100)
        ax.plot(x_for_plot,weibull(x_for_plot,keep_th,
                                   keep_slope,
                                   guess,
                                   flake),
                color = 'g')
        ax.set_title('Threshold=%1.2f +/- %1.2f ::Slope=%1.2f'
                     %(keep_th,(upper-lower)/2,keep_slope))
        fig.savefig(fig_name)

    return keep_th,lower,upper
