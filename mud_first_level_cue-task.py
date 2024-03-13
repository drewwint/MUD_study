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
sessions = ['01', '02']


# packages used
    # for analysis and plotting
import pandas as pd # to create and manage data in dataframes
import numpy as np # manipulate data and do quick calculations 
import nilearn # neuroimaging package
from nilearn import (image, plotting) # nilearn functions 
import matplotlib.pyplot as plt # plotting package
from nilearn.glm.first_level import FirstLevelModel # to use nilearn first level model glm
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
        
            # functional cue task
        cue_files = layout_prep.get(
            subject = subj,
            datatype = 'func', 
            task='cue',
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
            task='cue',
            session=sessions, 
            desc='confounds',
            extension="tsv", 
            return_type='file'
        )
            # events files
        design_files = layout_bids.get(
            subject = subj, 
            task= 'cue', 
            session=sessions, 
            suffix = 'events',
            extension='tsv', 
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
                # loading cue image files
                # flipping image into neurological view
                # loading confounds
                # selecting only confounds we want for cleaning
                # appending items to list: cue images to imgs and confounds to confounds
        imgs = []
        confounds = []
        for j in range(len(cue_files)):
            #printing subject, session, and task collected
            print(
                " cue loading ", 
                cue_files[j].split(os.sep)[6], 
                cue_files[j].split(os.sep)[7], 
                cue_files[j].split(os.sep)[9].split('_')[2]
            )
            dl_img = nilearn.image.load_img(
                cue_files[j]
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

        print(
                " loading complete", i, ": ", timedelta(seconds = time.monotonic() - start_loading).seconds/60, 
                "\n  cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
                "\n"
        )
        ## Cleaning images ##
        print("Cleaning: ", i)
        start_cleaning = time.monotonic()
            # here we are cleaning images at the first level with confound strategy decided earlier. 
        cleaned_imgs = []
        for ii in range(len(imgs)):
            print(" cleaning image: ", cue_files[ii].split(os.sep)[7], cue_files[ii].split(os.sep)[9].split('_')[2])
            cleaned_imgs.append(
                nilearn.image.clean_img(
                    imgs[ii],
                    confounds = confounds[ii],
                    detrend = True,
                    t_r= tr,
                    high_pass = high_pass,
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
                " saving clean image: ", cue_files[img_ind].split(os.sep)[7], cue_files[img_ind].split(os.sep)[9].split('_')[2],
                "\n  to file: ", os.path.join(base, subj_sf, 'ses-' + sessions[img_ind], mode, cue_files[img_ind].split(os.sep)[9])
            )
            c_img.to_filename(os.path.join(base, subj_sf, 'ses-' + sessions[img_ind], mode, cue_files[img_ind].split(os.sep)[9]))
            img_ind += 1
        print(
            " cleaning complete", i, ": ", timedelta(seconds = time.monotonic() - start_cleaning).seconds/60, 
            "\n  cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
            "\n"
        )
        
        ## BOLD estimate ##
        print("Estimating BOLD first level: ", i)
        glms = []
        for c_glm in range(len(cleaned_imgs)):
            glms.append(FirstLevelModel(t_r=tr, 
                        hrf_model="spm", #  SPMs HRF consists of a linear combination of two Gamma functions
                        drift_model = None,
                        signal_scaling=False, 
                        standardize=True,
                        n_jobs=-1, 
                        smoothing_fwhm = 6,
                        mask_img = mask
                        ))

            # getting the design matricies
        design = []
        for j in range(len(design_files)):
            #printing subject, session, and task collected
            print(" design loading ", cue_files[j].split(os.sep)[6], cue_files[j].split(os.sep)[7], cue_files[j].split(os.sep)[9].split('_')[2])
            design.append(pd.read_csv(design_files[j], sep='\t', index_col = 0))
        
            # running GLM
        glm_cue = []
        for glm_i in range(len(glms)):
            print(" estimating bold - first level ", cue_files[glm_i].split(os.sep)[6], cue_files[glm_i].split(os.sep)[7], cue_files[glm_i].split(os.sep)[9].split('_')[2], "\n")
            glm_f = glms[glm_i].fit(cleaned_imgs[glm_i], design[glm_i])
            glm_cue.append(glm_f)
        

        ## Contrasts ##
        print('Computing contrasts', i)
        start_contrasts = time.monotonic()
        
        # creating and estimating contrast matricies
        glm_ind = 0 
        for cond_i in range(len(glm_cue)):
            contrast_mat = np.eye(glm_cue[cond_i].design_matrices_[0].shape[1])
            conditions=dict(
                [
                    (column,contrast_mat[i])
                    for i, column in enumerate(glm_cue[cond_i].design_matrices_[0].columns)
                ]
            )

            cont = {
                'neutral-meth': (
                    conditions['Neutral']
                    - conditions['Meth']
                ),
                'meth-neutral': (
                    conditions['Meth']
                    - conditions['Neutral']
                ),
                'meth-fix': (
                    conditions['Meth']
                    - conditions['Fix']
                ),
                'fix-meth': (
                    conditions['Fix']
                    - conditions['Meth']
                ),
                'neutal-fix': (
                    conditions['Neutral']
                    - conditions['Fix']
                ),
                'fix-neutral': (
                    conditions['Fix']
                    - conditions['Neutral']
                )
            }

            contrast_img = []
            print("\n contrast glm : ", subj_sf, 'ses-' + sessions[glm_ind])
            cont_l = []
            for ss in cont:
                cont_l.append(cont[ss])
            rp = None
            rp = glm_cue[cond_i].generate_report(cont_l, title = subj_sf + '_' + 'task-cue' + '_' + 'ses-' + sessions[glm_ind], cluster_threshold = 10, alpha = 0.05)
            rp.save_as_html(os.path.join(base, subj_sf, 'ses-' + sessions[glm_ind], mode, subj_sf + '_' +  'ses-' + sessions[glm_ind] + '_' + 'task-cue_desc-glm-report' + '.html'))
            rp.open_in_browser()
            temp = []
            cont_ind = 0
            for n in cont:
                gct = None
                gct = glm_cue[cond_i].compute_contrast(cont[n])
                gct.to_filename(os.path.join(base,
                                            subj_sf,
                                            'ses-' + sessions[glm_ind],
                                            'func',
                                            subj_sf + '_' + 'ses-' + sessions[glm_ind] + '_' + 'task-cue_desc-contrast-' + n + '.nii.gz')
                                            )
                temp.append(gct)
                cont_ind += 1
            contrast_img.append(temp)   
            glm_ind += 1
       
        print(
            "Contrasts complete ", subj_sf, ": ", timedelta(seconds = time.monotonic() - start_contrasts).seconds/60, 
            "\n cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60, 
            "\n"
        )
    print(
        "All complete ", 
        "\n cumulative (min) = ", timedelta(seconds = time.monotonic() - start_overall).seconds/60
    )


