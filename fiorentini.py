import numpy as np

from psychopy import visual, core, event
import psychopy.monitors.calibTools as calib
from tools import *

p = Params()
app = wx.App()
app.MainLoop()
p.set_by_gui()

#This is for the case of demonstrating the stimulus/task to the subjects:  
if p.demo:
    #I mean it: 
    for remove_this in ['target_dur','response_dur','iti','trial_duration']:
        #For some reason they appear twice in there:
        p._dont_touch.remove(remove_this)
        p._dont_touch.remove(remove_this)

    #Stretch everything in time: 
    p.target_dur = 1
    p.response_dur = 1
    p.iti = 0.5
    p.trial_duration = (p.target_dur*2 +
                       p.isi * 2 + 
                       p.response_dur +
                       p.feedback_dur)
    #and make the tasks super easy:
    start_per_staircase = 1
    start_fix_staircase = 1
    
f = start_data_file(p.subject)

#Save the params:
p.save(f)

#Add a column, if you are monitoring eye-movements:
if p.eye_motion:
    f = save_data(f,'task','trial', 'contrast','correct','eye-motion')
else:
    f = save_data(f,'task','trial', 'contrast','correct')
    
rgb = np.array([1.,1.,1.])
pi = np.pi
two_pi = 2*pi
calib.monitorFolder = './calibration/'# over-ride the usual setting of where
                                      # monitors are stored

mon = calib.Monitor(p.monitor) #Get the monitor object and pass that as an
                                    #argument to win:
                                    
win = visual.Window(monitor=mon,units='deg',screen=p.screen_number,
                    fullscr=p.full_screen)
#Shorthand:
fs = p.fixation_size

fixation_color = p.fixation_color * rgb
    
square_fixation = visual.PatchStim(win, tex=None,color=fixation_color,
                                size=p.fixation_size,interpolate=False)

square_fixation_surround = visual.PatchStim(win, tex=None, 
                                     color=1*rgb,
                                     size=p.fixation_size*1.5,
                                            interpolate=False)

if p.target_loc == 'Right':
    #Triangle fixation: 
    arrow_fixation = visual.ShapeStim(win, fillColor=fixation_color,
                            lineColor=fixation_color,
                            vertices=((fs/2, 0),(-fs/2, fs/2),(-fs/2,-fs/2)))
    #With a white penumbra:
    arrow_fixation_surround = visual.ShapeStim(win, fillColor=1*rgb,
                                               lineColor=1*rgb,
                    vertices=((fs/1.5, 0),(-fs/1.5, fs/1.5),(-fs/1.5,-fs/1.5)))
    

elif p.target_loc == 'Left':
    #Triangle fixation: 
    arrow_fixation = visual.ShapeStim(win, fillColor=fixation_color,
                                      lineColor=fixation_color,
                                vertices=((-fs/2, 0),(fs/2, fs/2),(fs/2, -fs/2)))
    #With a black penumbra:
    arrow_fixation_surround = visual.ShapeStim(win, fillColor=1*rgb,
                                               lineColor=1*rgb,
                vertices=((-fs/1.5, 0),(fs/1.5, fs/1.5),(fs/1.5, -fs/1.5)))    

#Peripheral target locations
target_x = p.target_x
target_y = p.target_y

if p.target_loc == "Left":
    target_x *=-1

nontarget_y = target_y
nontarget_x = -1 * target_x

#Initialize separate staircases for each task:
per_staircase = Staircase(p.start_per_staircase,p.per_staircase_step,lb=0.01,ub=1)
fix_staircase = Staircase(p.start_fix_staircase,p.fix_staircase_step,lb=0.01,ub=1)

#These variables are later used in order to generate the sin-wave stimuli:
X, Y = np.mgrid[0:2*pi:2*pi/p.res, 0:2*pi:2*pi/p.res]

#Pythagoras to the rescue: 
Z = np.sqrt((Y - np.pi)**2 + (X-np.pi)**2)

masker = np.zeros_like(Z)
masker[np.where(Z<np.pi)] = 1
raised_cos_idx = np.where([np.logical_and(Z<=np.pi,Z>=np.pi*(1-p.fringe_proportion))])[1:]

hamming_len = 1000
# Make a raised_cos (half a hamming window):
raised_cos = np.hamming(hamming_len)[:hamming_len/2]
raised_cos -= np.min(raised_cos)
raised_cos /= np.max(raised_cos)

# Measure the distance from the edge - this is your index into the hamming window: 
d_from_edge = np.abs(pi*(1-p.fringe_proportion)- Z[raised_cos_idx])
d_from_edge /= np.max(d_from_edge)
d_from_edge *= np.round(hamming_len/2)

# This is the indices into the hamming (larger for small distances from the edge!):
portion_idx = (-1 * d_from_edge).astype(int)

# Apply the raised cos to this portion:
masker[raised_cos_idx]=raised_cos[portion_idx]

# Scale it into the interval -1:1: 
masker = masker - 0.5
masker = masker / np.max(masker)

#Sometimes there are some remaining artifacts from this process, get rid of them:
artifact_idx = np.where(np.logical_and(masker == -1, Z<np.pi))
masker[artifact_idx] = 1

#Put up message, wait for subject to press a key:
message = """ Press a key """
Text(win,text=message,height=0.5)() 

if p.scanner:
    if p.do_fixation:
        fixation = square_fixation
        fixation_surround = square_fixation_surround
    elif p.do_peripheral:
        fixation = arrow_fixation
        fixation_surround = arrow_fixation_surround
    #Get the fixation up:
    fixation_surround.draw()
    fixation.draw()
    win.flip()
    #Wait 1 sec, to avoid running off:
    core.wait(1)
    ttl = 0
    #After that, wait for the ttl pulse:
    while ttl<1:
        for key in event.getKeys():
            if key:
                ttl = 1
                # Start a clock to tally the time since scan started:
                scan_clock=core.Clock()

    print scan_clock.getTime()
    
    # The scan is 5:12 minutes (156 TR) long, and the stimulus presentation is only 288
    # seconds, so we add 12 seconds in the beginning and 12 seconds in the end:
    core.wait(9)
    Text(win,text='3',height=0.5)(10-scan_clock.getTime(),key_press=False) 
    Text(win,text='2',height=0.5)(11-scan_clock.getTime(),key_press=False)
    Text(win,text='1',height=0.5)(12-scan_clock.getTime(),key_press=False) 
else:
    # Just keep time from this time onwards
    scan_clock=core.Clock()


#time_arr = [0] #dbg
trial_counter = 0
for block in xrange(p.n_blocks):
    if p.do_fixation:
        block_clock = core.Clock()
        #During the fixation blocks, the fixation is the square fixation:
        fixation = square_fixation
        fixation_surround = square_fixation_surround
        #Fixation task block: 
        for trial in xrange(p.n_trials):
            trial_clock = core.Clock()
            correct = None #per default, no response 
            get_response = True 
            target_first = np.sign(np.random.randn(1))>0
            t = 0

            #Set the feedback color to default to gray:
            fixation_feedback_color = [0,0,0]

            while t<p.trial_duration:
                t = trial_clock.getTime()

                #For the first isi of the trial, do nothing: 
                if t<p.isi:
                    fixation.setColor(p.fixation_color)

                #For the following segment, show the first stimulus:
                elif t<p.target_dur+p.isi:
                    if target_first:
                        fixation.setColor(rgb*fix_staircase.value)
                    else:
                        fixation.setColor(rgb*p.fix_base_color)

                #Then, during the isi, switch the color back to the original: 
                elif t<p.target_dur+2*p.isi:
                    fixation.setColor(rgb*p.fixation_color)

                #During the second stimulus interval, show the second stimulus:
                elif t<p.target_dur*2+2*p.isi:
                    if target_first:
                        fixation.setColor(rgb*p.fix_base_color)
                    else:
                        fixation.setColor(rgb*fix_staircase.value)

                #During the response duration, turn the stimulus off again:
                elif t<p.target_dur*2+2*p.isi+p.response_dur:
                    fixation.setColor(rgb*p.fixation_color)

                elif t<p.target_dur*2+2*p.isi+p.response_dur+p.feedback_dur:
                    fixation.setColor(fixation_feedback_color)

                fixation_surround.draw()
                fixation.draw()
                win.flip()

                if get_response:
                    for key in event.getKeys(keyList=['1','2','end','down']):
                        if ( (target_first and key=='1') or
                             (target_first and key=='end') or
                             (target_first==False and key=='2') or
                             (target_first==False and key=='down') ):
                            correct = True
                            p.correct_sound.play()
                            fixation_feedback_color = [0,1,0]
                        else:
                            correct = False
                            p.incorrect_sound.play()
                            fixation_feedback_color = [1,0,0]
                        get_response = False

                for key in event.getKeys():
                    if key in ['escape','q']:
                        win.close()
                        core.quit()

            #Trial done, play the no-response feedback, if you haven't gathered a
            #response: 
            if correct is None:
                p.no_response_sound.play()

            #Convert from bool to int for saving into data file:
            if correct is None:
                correct_int = -1
            elif correct: #True
                correct_int = 1
            else: #False
                correct_int = 0  

            trial_counter += 1

            eyes_moved = 0
            if p.eye_motion == True:
                no_key = True
                while no_key:
                    for key in event.getKeys(keyList=['space','f']):
                        if key == 'f':
                            #Feedback for eye movement: 
                            p.eye_motion_sound.play()
                            no_key = False
                            eyes_moved = 1
                        else:
                            #Otherwise, just move on to the next trial:
                            no_key = False
                f = save_data(f,'fixation',trial_counter,fix_staircase.value,
                          correct_int,eyes_moved)
            #If no eye-motion monitoring, save without that info and wait for
            #the alloted time
            else:
                f = save_data(f,'fixation',trial_counter,fix_staircase.value,
                          correct_int)

            #Update the staircase, before moving on (assuming no eye-motion
            #happened): 
            if eyes_moved==0:
                fix_staircase.update(correct)                

            #Clear the event cue, so that previous responses made after the end
            #of the trial don't get registered in the next trial: 
            event.clearEvents()

            iti = p.iti
            #In the transition between blocks, turn the fixation around: 
            if p.do_peripheral and trial == p.n_trials-1:
                    fixation = arrow_fixation
                    fixation_surround = arrow_fixation_surround
                    fixation_surround.draw()
                    fixation.setFillColor(fixation_feedback_color)
                    fixation.setLineColor(fixation_feedback_color)
                    fixation.draw()
                    win.flip()
                    #And wait for a longer period between blocks:
                    #print p.block_duration-block_clock.getTime() #dbg
                    core.wait(p.block_duration - block_clock.getTime())
            else:
                core.wait(p.trial_duration+p.iti-trial_clock.getTime())

            #time_arr.append(scan_clock.getTime()) #dbg
            
    #In training, you don't want to do the peripheral task at all:
    if p.do_peripheral:
        block_clock = core.Clock()
        fixation = arrow_fixation
        fixation_surround = arrow_fixation_surround
        #Peripheral task block:
        for trial in xrange(p.n_trials):
            trial_clock = core.Clock()
            correct = None #per default, no response 
            get_response = True 
            target_first = np.sign(np.random.randn(1))>0
            
            #The non-target is determined independently from the target: 
            nontarget_first = np.sign(np.random.randn(1))>0
            if nontarget_first:
                nontarget_intensity1 = (np.sin(Y-pi/2) +
                                     per_staircase.value*np.sin(3*Y-pi/2))
                nontarget_intensity2 = (np.sin(Y-pi/2))
            else:
                nontarget_intensity1 = (np.sin(Y-pi/2))
                nontarget_intensity2 = (np.sin(Y-pi/2) +
                                     per_staircase.value*np.sin(3*Y-pi/2))

            nontarget_intensity1 /= np.max(nontarget_intensity1)
            nontarget_intensity2 /= np.max(nontarget_intensity2)
            
            t = 0

            #Set the feedback color to default to gray:
            fixation_feedback_color = [0,0,0]
            
            while t<p.trial_duration:
                t = trial_clock.getTime()
                #First interval, draw only the fixation:
                if t<p.isi:
                    fixation.setFillColor(rgb*p.fixation_color)
                    fixation.setLineColor(rgb*p.fixation_color)

                elif t<p.target_dur + p.isi:
                    fixation.setLineColor(rgb*p.fixation_color)
                    fixation.setFillColor(rgb*p.fixation_color)
                    if target_first:
                        color_target = [1, 0.8, 0.8]
                        intensity = (np.sin(Y-pi/2) +
                                     per_staircase.value*np.sin(3*Y-pi/2))   
                    else:
                        color_target = [1,1,1]
                        intensity = (np.sin(Y-pi/2))

                    intensity /= np.max(intensity)
                    
                    grating1 = visual.PatchStim(win,ori=p.orientation,
                                                pos=[target_x,target_y],
                                                phase=0,tex=intensity,
                                                sf=p.sf_base,mask=masker,
                                                size=p.target_size,
                                                interpolate=False)
                    if p.color_target:
                        grating1 = visual.PatchStim(win,
                                                color=color_target,
                                                colorSpace='rgb',
                                                pos=[target_x,target_y],
                                                tex=np.ones(intensity.shape),
                                                mask=masker,
                                                size=p.target_size,
                                                interpolate=False)
 
                    grating1.draw()

                elif t<p.target_dur+2*p.isi:
                    #Don't draw the gratings during the isi:
                    fixation.setFillColor(rgb*p.fixation_color)
                    fixation.setLineColor(rgb*p.fixation_color)

                #Second interval:
                elif t<p.target_dur*2+2*p.isi:
                    fixation.setFillColor(rgb*p.fixation_color)
                    fixation.setLineColor(rgb*p.fixation_color)

                    if target_first:
                        color_target = [1,1,1]
                        intensity = np.sin(Y-pi/2)
                    else:
                        intensity = (np.sin(Y-pi/2) +
                                     per_staircase.value*np.sin(3*Y-pi/2))
                        color_target = [1, 0.8, 0.8]
                        
                    intensity /= np.max(intensity)
                    grating1 = visual.PatchStim(win,ori=p.orientation,
                                                pos=[target_x,target_y],
                                                phase=0,tex=intensity,
                                                sf=p.sf_base,mask=masker,
                                                size=p.target_size,
                                                interpolate=False)
                    if p.color_target:
                        grating1 = visual.PatchStim(win,
                                                color=color_target,
                                                colorSpace='rgb',
                                                pos=[target_x,target_y],
                                                tex=np.ones(intensity.shape),
                                                mask=masker,
                                                size=p.target_size,
                                                interpolate=False)
                    grating1.draw()

                #During the response duration, turn the stimulus off again:
                elif t<p.target_dur*2+2*p.isi+p.response_dur:
                    fixation.setFillColor(rgb*p.fixation_color)
                    fixation.setLineColor(rgb*p.fixation_color)

                elif t<p.target_dur*2+2*p.isi+p.response_dur+p.feedback_dur:
                    fixation.setFillColor(fixation_feedback_color)
                    fixation.setLineColor(fixation_feedback_color)

                fixation_surround.draw()
                fixation.draw()
                win.flip()

                if get_response:
                    for key in event.getKeys(keyList=['1','2','end','down']):
                        if ( (target_first and key=='1') or
                             (target_first and key=='end') or
                             (target_first==False and key=='2') or
                             (target_first==False and key=='down') ):
                            correct = True
                            p.correct_sound.play()
                            fixation_feedback_color = [0,1,0]
                        else:
                            correct = False
                            p.incorrect_sound.play()
                            fixation_feedback_color = [1,0,0]
                        get_response = False

                for key in event.getKeys():
                    if key in ['escape','q']:
                        win.close()
                        core.quit()

            if correct is None:
                p.no_response_sound.play()

            #Convert from bool to int for saving into data file:
            if correct is None:
                correct_int = -1
            elif correct: #True
                correct_int = 1
            else: #False
                correct_int = 0
                                
            trial_counter += 1

            eyes_moved = 0
            if p.eye_motion == True:
                no_key = True
                while no_key:
                    for key in event.getKeys(keyList=['space','f']):
                        if key == 'f':
                            #Feedback for eye movement: 
                            p.eye_motion_sound.play()
                            no_key = False
                            eyes_moved = 1
                        else:
                            #Otherwise, just move on to the next trial:
                            no_key = False
                
                f = save_data(f,'periphery',trial_counter,
                          per_staircase.value,correct_int,eyes_moved)

            #If no eye-motion monitoring, save without that info and wait for
            #the alloted time
            else:
                f = save_data(f,'periphery',trial_counter,
                          per_staircase.value,correct_int)

            #Update the staircase, before moving on (assuming no eye-motion
            #happened): 
            if eyes_moved==0:
                per_staircase.update(correct)                
            #Clear the event cue, so that previous responses made after the end
            #of the trial don't get registered in the next trial: 
            event.clearEvents()


            iti = p.iti
            #In the transition, turn the fixation around:
            if p.do_fixation and trial == p.n_trials-1:
                fixation = square_fixation
                fixation_surround = square_fixation_surround
                fixation_surround.draw()
                fixation.setColor(fixation_feedback_color)
                fixation.draw()
                win.flip()
                # Wait exactly for the remainder of the block:
                #print p.block_duration-block_clock.getTime() #dbg
                core.wait(p.block_duration-block_clock.getTime())
            else:
                # Wait for the ITI, before moving on the next trial:
                core.wait(p.trial_duration+p.iti-trial_clock.getTime())

    # How long did this block take?
    print scan_clock.getTime()

            #time_arr.append(scan_clock.getTime()) #dbg

#Take the fig name from the data file name:
fig_stem = f.name.split('/')[-1].split('.')[0]

#Print out the values of the staircases, for the next run:
if p.do_fixation:
    print 'Fixation staircase ended at: %1.4f'%fix_staircase.record[-1]
    if p.save_fig:
        fname = 'data/%s_fix.png'%fig_stem
        th,lower,upper=fix_staircase.analyze(fig_name=fname)
    else:
        th,lower,upper = fix_staircase.analyze()
    print 'Fixation threshold: %s +/- %s'%(th,(upper-lower)/2)    
if p.do_peripheral:
    print 'Periphery staircase ended at: %1.4f'%per_staircase.record[-1]
    if p.save_fig:
        fname = 'data/%s_per.png'%fig_stem
        th,lower,upper=per_staircase.analyze(fig_name=fname)
    else:
        th,lower,upper = per_staircase.analyze()
    print 'Periphery threshold: %s +/- %s'%(th,(upper-lower)/2)    

print scan_clock.getTime()

if p.scanner:
    # Wait until the scan is over, unless the analysis has already filled this time:
    core.wait(312-scan_clock.getTime())

print scan_clock.getTime()
f.close()
win.close()
core.quit()



