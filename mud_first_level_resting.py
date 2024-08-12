#!/bin/env python

# enter subjects you want to run
    # example: for the first subject 
        # subs = ['sub-001']
        # mnultiple subjects 
        # subs = ["sub-001", "sub-002"]
subs = ['sub-001']
# enter sessions you want to run
    # example: for session 1 and 2
        # sessions = ['01', '02']
sessions = ['03']


# packages used
    # for analysis and plotting
import pandas as pd # to create and manage data in dataframes
import numpy as np # manipulate data and do quick calculations 
import nilearn # neuroimaging package
import nilearn.image 
# from nilearn import (image, plotting) # nilearn functions 
# import matplotlib.pyplot as plt # plotting package

    # system and file management
import os # file management
import sys # extracting linux env vars
import bids # for bids file retrevial
import warnings # to suppress erroneous warnings (i've checked them)
warnings.filterwarnings("ignore") # to get rid of the annoying depreciation warning that has nothing to do with this analysis. 
import time # to keep time
from datetime import timedelta # to accurately make calculations with dates and times. 
start_overall = time.monotonic() # here we are starting overall time to keep time of how long the script takes to complete. 

# bids layout
bids_prep= "/home/wintersd/mud_bids/derivatives/fmriprep/"
layout_prep = bids.BIDSLayout(bids_prep, validate=False)

bids_layout= "/home/wintersd/mud_bids/"
layout_bids = bids.BIDSLayout(bids_layout, validate=False)


# options
tr = 2
high_pass = 0.008
low_pass = 0.08

print(
    "\nSetup ", 
    "duration (min) = ", 
    timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
    "\n"
)

from joblib import parallel_backend
with parallel_backend('threading', n_jobs=-1):
    for i in subs:
        subj = os.path.split(i)[1].split('-')[1]
        start_loading = time.monotonic()
        print("Loading: ", i)
        ## obtaining files list
            ## mask
        mask = nilearn.image.load_img(
            os.path.join(
                '/home/wintersd/mud_bids/derivatives/fmriprep', i, 'ses-01/anat', 
                i + '_ses-01' + '_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz'
                )
        )
                #- note we only use ses-01 because of the say we prprocessed each session individually made anat go into ses-01
                #- if we did more than one session at once then we would have anat in subject file independent of session
                #- the mask file is for all sessions even thought in this case it is under ses-01 tab
        
            # functional resting state
        rest_files = layout_prep.get(
            subject = subj,
            datatype = 'func', 
            task='rest',
            session=sessions,
            extension='nii.gz', 
            desc = 'preproc', # desc-preproc refers to preprocessed input images
            space = 'MNI152NLin6Asym',
            return_type='file'
        )
            # confound files
        confound_files = layout_prep.get(
            subject=subj, 
            datatype='func',  
            task='rest',
            session=sessions, 
            desc='confounds',
            extension="tsv", 
            return_type='file'
        )
        
        # loading images and confounds for cleaning
            # cleaning strategy to extract
                # 12 motion parameters (6 motion and derivatives [no quadratics])
        clean_name = ["trans_x",
                        "trans_x_derivative1",
                        "trans_y","trans_y_derivative1",
                        "trans_z",
                        "trans_z_derivative1",
                        "rot_x",
                        "rot_x_derivative1",
                        "rot_y",
                        "rot_y_derivative1",
                        "rot_z",
                        "rot_z_derivative1"
        ]
            # function for 
                # loading restimage files
                # flipping image into neurological view
                # loading confounds
                # selecting only confounds we want for cleaning
                # appending items to list: restimages to imgs and confounds to confounds
        imgs = []
        confounds = []
        for j in range(len(rest_files)):
            #printing subject, session, and task collected
            print(
                " rest loading ", 
                rest_files[j].split(os.sep)[6], 
                rest_files[j].split(os.sep)[7], 
                rest_files[j].split(os.sep)[9].split('_')[2]
            )
            dl_img = nilearn.image.load_img(
                rest_files[j]
            )
            # here we are flipping the image on the 0 axis
                # This is becasue the brain was recored in radiological view and need to flip it for our plots
                # In brains the 0 axis is the x axis from left to right
                # so we use the flipud() function in numpy to flip our image on the 0 axis
            fl_img = nilearn.image.math_img(
                'np.flipud(img)', 
                img=dl_img
            )
            imgs.append(fl_img)
            confounds.append(
                pd.read_csv(confound_files[j], 
                sep='\t')[clean_name]
            )
        
        for m in confounds:
            m.fillna(
                0, 
                inplace=True
            )

        print(
                " loading complete", i, ": ", timedelta(seconds = time.monotonic() - start_loading).seconds/60, 
                "\n  cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
                "\n"
        )
        ## Cleaning images ##
        print("Cleaning:", i)
        start_cleaning = time.monotonic()
            # here we are cleaning images at the first level with confound strategy decided earlier. 
        cleaned_imgs = []
        for ii in range(len(imgs)):
            print(" cleaning image: ", rest_files[ii].split(os.sep)[7], rest_files[ii].split(os.sep)[9].split('_')[2])
            cleaned_imgs.append(
                nilearn.image.clean_img(
                    imgs[ii],
                    confounds = confounds[ii],
                    detrend = True,
                    t_r= tr,
                    high_pass = high_pass,
                    low_pass = low_pass,
                    mask_img= mask
                )
            )

            # saving clean images
                # setting up file name strucure for entire script (not all of these are used here and may be used later)
        base = '/home/wintersd/mud_bids/derivatives/clean_imgs'
        mode = "func"
        subj_sf = 'sub-' + str(subj)
        session1 = 'ses-01'
        session2 = 'ses-02'
        session3 = 'ses-03'
        session4 = 'ses-04'
        ses_lev = [session1, session2, session3, session4]
        if os.path.exists(base) == False:
                os.mkdir(base)
        if os.path.exists(os.path.join(base, subj_sf)) == False:
            os.mkdir(os.path.join(base, subj_sf))
        for items in ses_lev:
            path = os.path.join(base, subj_sf ,items)
            if os.path.exists(path) == False:
                os.mkdir(path)
                os.mkdir(os.path.join(path,mode))
        img_ind = 0
        for c_img in cleaned_imgs:
            print(
                " saving clean image: ", rest_files[img_ind].split(os.sep)[7], rest_files[img_ind].split(os.sep)[9].split('_')[2],
                "\n  to file: ", os.path.join(base, subj_sf, 'ses-' + sessions[img_ind], mode, rest_files[img_ind].split(os.sep)[9])
            )
            c_img.to_filename(os.path.join(base, subj_sf, 'ses-' + sessions[img_ind], mode, rest_files[img_ind].split(os.sep)[9]))
            img_ind += 1
        print(
            " cleaning complete", i, ": ", timedelta(seconds = time.monotonic() - start_cleaning).seconds/60, 
            "\n  cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
            "\n"
        )
        
        # ## Connectivity estimate ##
        # print("Estimating Connectivity first level: ", i)
        # corr_est = ConnectivityMeasure(kind='correlation')
        # corr_mat = corr_est.fit_transform([c_img])[0]


       
        # print(
        #     "Connectivity complete ", subj_sf, ": ", timedelta(seconds = time.monotonic() - start_contrasts).seconds/60, 
        #     "\n cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
        #     "\n"
        # )
    print(
        "All complete ", 
        "\n cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60
    )


