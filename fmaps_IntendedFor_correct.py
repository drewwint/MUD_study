#!/bin/env python

import os
import glob
import json

# specifying subject
subj='sub-001' # coudl use 0* for all subjects
session='ses-03' # ses-0* for all sessions or you culd specify specific session. 
subjectsPath = os.path.join('/home', 'wintersd', 'mud_bids', subj)
	## for all participants 
	# subjectsPath = os.path.join('/home', 'wintersd', 'mud_bids', 'sub-*')
subjects = glob.glob(subjectsPath)
# print(subjects)
# print(subjectsPath)


for subject in subjects:
	fmapsPath1 = os.path.join(subject, session, 'fmap', '*.json')
	fmaps1 = glob.glob(fmapsPath1)
	funcsPath1 = os.path.join(subject, session, 'func', '*.nii.gz')
	funcs1 = glob.glob(funcsPath1)
# print(fmaps1)
# print(funcs1)
	# substring to be removed from absolute path of functional files
	pathToRemove = subject + '/'
	funcs1 = list(map(lambda x: x.replace(pathToRemove, ''), funcs1))
# print(pathToRemove)
# print(funcs1)
	for fmap in fmaps1:
		with open(fmap, 'r') as data_file:
			fmap_json = json.load(data_file)
		fmap_json['IntendedFor'] = funcs1
# print(fmap_json)
# print(data_file)
		with open(fmap, 'w') as data_file:
			fmap_json = json.dump(fmap_json, data_file)


