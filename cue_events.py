#!/bin/env python

import numpy as np
import pandas as pd
import os


# to save the events file
subn = '001'
subj = 'sub-' + str(subn)
sesn = '03'
session = 'ses-' + str(sesn)

# duration times

a=np.repeat(24,18)
b=np.repeat(6,18)

duration = np.empty((a.size + b.size,), dtype=a.dtype)
duration[0::2] = a
duration[1::2] = b

# onset
g = duration.copy()
g2 = np.append(0,g)
onset = np.cumsum(g2[:-1])

# trial type
trial_type=["Neutral",
            "Fix",
            "Meth",
            "Fix",
            "Neutral",
            "Fix",
            "Meth",
            "Fix",
            "Neutral",
            "Fix",
            "Meth",
            "Fix",
            "Meth",
            "Fix",
            "Neutral",
            'Fix',
            "Neutral",
            "Fix",
            "Meth",
            "Fix",
            "Neutral",
            "Fix",
            "Neutral",
            "Fix",
            "Meth",
            "Fix",
            "Meth",
            "Fix",
            "Neutral",
            "Fix",
            "Meth",
            "Fix",
            "Meth",
            "Fix",
            "Neutral",
            "Fix"
            ]


# Combining 
cue_event = pd.DataFrame({"onset":onset, "duration":duration,"trial_type":trial_type})

# saving 
base = '/home/wintersd/mud_bids/'
out = 'task-cue_events.tsv'
cue_event.to_csv(os.path.join(base,subj,session,'func', subj + '_' + session + '_' + out), sep='\t')


