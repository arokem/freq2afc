#!/usr/bin/env python

#bb_check.py
#written by SS 3/8/2012

from psychopy import event, visual,core

myWin = visual.Window((800,600), allowGUI=False, color=(-1,-1,-1), colorSpace='rgb', monitor='testMonitor', winType='pyglet')

textStim = visual.TextStim(myWin,text='press each button', font='Arial', height=.1,
                           color=(1,1,1), colorSpace='rgb', pos=(0.5,0))
textStim2 = visual.TextStim(myWin,text='button pressed = none yet', font='Arial', height=.1,
                           color=(1,1,1), colorSpace='rgb', pos=(-0.5,0)) 
textStim_quit = visual.TextStim(myWin,text='to quit, press q', font='Arial', height=.1,
                           color=(1,1,1), colorSpace='rgb', pos=(-0.5,0.5)) 

button_pressed = 0
end = 0

textStim.draw()
textStim2.draw()
textStim_quit.draw()
myWin.flip()

while end != 1:
    key = event.getKeys()
    if len(key) != 0:
        if key[-1] == 'q':
            end = 1
            core.quit()
        else:
            print key
            message = 'button pressed = ' +key[-1]
            textStim.draw()
            textStim2.setText(message)
            textStim2.draw()
            textStim_quit.draw()
            myWin.flip()
            core.wait(0.5)
            key = None
    