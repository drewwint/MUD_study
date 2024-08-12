#!/bin/env bash

# Creating conda environment (already done so no need to run this again)
#conda create --name bids2dcm_env python=3.10.9 dcm2niix dcm2bids 

# activating conda environment 
conda activate dcm2bids_env

# choices for structure here
 # this is relevant once we have more subjects and sessions
    # subject = to identify which subject
    # session = what session are we running here? 
subn=001
sess=03
subf=sub-$subn
sessf=ses-$sess

echo "running dcm2bids on: " $subf " for " $sessf


# to create configuration files 
    # first we extract files and run a series of searches to ensure we are tettign teh right files from dcm in the right folders
    # then put this in the config file for proper retrevial. 
    # cd /home/wintersd/mud_bids/ # file you wnt helper to place file 
    # dcm2bids_helper -d /home/wintersd/mud_raw/
    # then we extract info from the .json files to make our configuration files 
    # files I am intersted in 
        # *_t1_mprage_sag*.nii.gz and json # for t1
        # *fMRI_CUE* .nii.gz and json # for cue
        # *fMRI_REST* .nii.gz and json # for rest
        # *fMRI_BLIP* .nii.gz and json # for fieldmap

    # T1 - comparing to find correct file - example from mock
        # diff --side-by-side tmp_dcm2bids/helper/"008_raw_t1_mprage_sag_p2_20231205143432.json" tmp_dcm2bids/helper/"009_raw_t1_mprage_sag_p2_20231205143432.json"
        # diff --side-by-side tmp_dcm2bids/helper/"008_raw_t1_mprage_sag_p2_20231205143432.json" tmp_dcm2bids/helper/"010_raw_t1_mprage_sag_p2_20231205143432.json"
        # 008 is the right one - finding grep to identify it
            #  grep "t1_mprage_sag_p2" tmp_dcm2bids/helper/*.json
            #  grep "HEAD" tmp_dcm2bids/helper/*.json - this is under BodyPartExamined
        # essentialy we are lokoing for the file that has "head" body part being examined. 

# for mud raw
cd /home/wintersd/mud_raw

# # for selected subject and session 
dcm2bids -d /home/wintersd/mud_raw/$subf/$sessf \
        -p $subn \
        -s $sess \
        -c /home/wintersd/mud_code/dcm2bids_mud_config.json \
        -o /home/wintersd/mud_bids/ \
        --force 



# # for all subjects in folder
# for f in *
#     do sub="${f#*-}"
#     echo $sub 
#     echo $f 
#     dcm2bids -d /home/wintersd/mud_raw/$f \
#             -p $sub \
#             -s 01 \
#             -c /home/wintersd/mud_code/dcm2bids_mud_config.json \
#             -o /home/wintersd/mud_bids/ \
#             --force 
# done




# dcm2bids -d /home/wintersd/mud/mock/raw/sub-002/ -p 002 -c /home/wintersd/mud/code/dcm2bids_mud_confit_comb.json -o /home/wintersd/mud/mock/ --force

