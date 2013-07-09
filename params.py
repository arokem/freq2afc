from tools import sound_freq_sweep,compound_sound

from psychopy.sound import Sound 

p = dict(
    color_target=True,
    monitor='SportsMedicineLab',
    screen_number = 0,
    scanner = False,
    eye_motion = True,
    full_screen = False,
    save_fig=True,
    #Feedback sounds
    incorrect_sound = Sound(sound_freq_sweep(8000, 200, .1)),
    correct_sound = Sound(sound_freq_sweep(2000,2000,.1)),
    no_response_sound = Sound(sound_freq_sweep(500, 700, .1)),
    eye_motion_sound = Sound(compound_sound([200,400,800], .2)),
    fixation_size = 3.0,
    target_dur = 0.1,
    response_dur = 1.5,
    feedback_dur = 0.3,
    iti = 0.24,
    isi = 0.3,
    interblock_interval=0.54,
    # block_duration = 12, Enforce this!
    n_trials = 5,
    n_blocks = 12,
    target_size = 4,
    target_x = 4,
    target_y = 4,
    sf_base = 1,
    res = 128,
    fix_base_color = 0, #The comparison color for the brightness judgment
    fixation_color = -1,
    fix_staircase_step = 0.05,
    per_staircase_step = 0.05,
    fringe_proportion = 0.2, # The part of the stimulus that is a raised cosine
                            # at the fringe
    )

p['trial_duration'] = (p['target_dur']*2 +
                       p['isi'] * 2 + 
                       p['response_dur'] +
                       p['feedback_dur'])


#2*(5*p.trial_duration+4*p.iti + p.interblock_interval)

p['block_duration'] = (p['trial_duration']*5 + p['iti'] * 4 + p['interblock_interval'])
