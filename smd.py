#!/usr/bin/python3

from time import sleep
from tqdm import tqdm
import argparse
import json
import requests
import os

# Initialize parser
parser = argparse.ArgumentParser(description='Snapchat Memories Downloader')
parser.add_argument('-i', action='store', dest='input_file', help='Input JSON file')
parser.add_argument('-o', action='store', dest='output_dir', help='Output directory')
argresults = parser.parse_args()

if not argresults.input_file:
	print('No input file specified. Run with -h for help\nEXITING!')
	quit()
	
else:
	inputfile = argresults.input_file
	
if not argresults.output_dir:
	print('No output directory specified. Run with -h for help\nEXITING!')
	quit()
	
else:
	outputdir = argresults.output_dir
	
# ASCII art
# https://patorjk.com/software/taag/#p=display&f=Ivrit&t=Snapchat%0AMemory%0ADownloader%0Av%200.1

print("""\
  ____                         _           _              
 / ___| _ __   __ _ _ __   ___| |__   __ _| |_            
 \___ \| '_ \ / _` | '_ \ / __| '_ \ / _` | __|           
  ___) | | | | (_| | |_) | (__| | | | (_| | |_            
 |____/|_| |_|\__,_| .__/ \___|_| |_|\__,_|\__|           
  __  __           |_|                                    
 |  \/  | ___ _ __ ___   ___  _ __ _   _                  
 | |\/| |/ _ \ '_ ` _ \ / _ \| '__| | | |                 
 | |  | |  __/ | | | | | (_) | |  | |_| |                 
 |_|  |_|\___|_| |_| |_|\___/|_|   \__, |                 
  ____                      _      |___/      _           
 |  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __ 
 | | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 | |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
 |____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   
           ___   _                                        
 __   __  / _ \ / |                                       
 \ \ / / | | | || |                                       
  \ V /  | |_| || |                                       
   \_/    \___(_)_|                                       
                                                   """)

snapurls = {} # Make a dictionary for snapchat memory dates and urls
duplicateswitch = False # Switch for duplicate filenames
part = 1 # Value for duplicate filename suffix
f = open(inputfile) # Open specified JSON file
data = json.load(f) # Return JSON object as a dictionary

# Iterate through the JSON list: 
# TODO: Maybe clean this up. json.load already loads the file as a dictionary
for i in data["Saved Media"]:
	datetimeraw = i["Date"].split() # Get the memory date
	datetime = datetimeraw[0] + '-' + datetimeraw[1].replace(':', '') # Make the date key in format YYYY-MM-DD-HHMMSS
	if datetime in snapurls: # If already in dictionary (memory saved at the exact same time)
		if duplicateswitch: part += 1 # Add value if already been through this
		datetime = datetime + "-" + str(part) # Add suffix to filename
		snapurls[datetime] = i["Download Link"] # Add the snap url to dictionary with date(+suffix) as the key
		duplicateswitch = True
	else:
		snapurls[datetime] = i["Download Link"] # Add the snap url to dictionary with date as the key
		duplicateswitch = False
		part = 1

print("You have", len(snapurls), "memories to download.")

for key in tqdm(snapurls):
	awslink = requests.post(snapurls[key]) # POST request to Snap URL and receive a link pointing to AWS bucket with your memory
	filename = key + "." + awslink.text.split("/")[-1].split("?")[0].split(".")[1] # Make the filename from the memory date and the AWS link extension
	fullpath = os.path.join(outputdir, filename) # Get output full path
	downloadmemory = requests.get(awslink.text) # Download the memory from AWS bucket
	with open(fullpath, 'wb') as f: 
		f.write(downloadmemory.content) # Save to the specified path on disk
