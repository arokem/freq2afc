#test usb key-pad:

from psychopy import visual, core, event

win = visual.Window()
trial_clock = core.Clock()

t=0 
while t<60:
    t = trial_clock.getTime()

    for key in event.getKeys():
        print key
