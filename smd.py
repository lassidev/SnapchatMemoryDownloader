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

snapurls = [] # Make an array for snapchat memory urls
f = open(inputfile) # Open specified JSON file
data = json.load(f) # Return JSON object as a dictionary

# Iterate through the JSON list:
for i in data["Saved Media"]:
	snapurls.append(i["Download Link"]) # Add to array

print("You have", len(snapurls), "memories to download.")

for snapurl in tqdm(snapurls):
	awslink = requests.post(snapurl) # POST request to Snap URL and receive a link pointing to AWS bucket with your memory
	filename = awslink.text.split("/")[-1].split("?")[0] # Get filename from AWS bucket link. Doesn't provide headers for some reason?
	fullpath = os.path.join(outputdir, filename) # Get output full path
	downloadmemory = requests.get(awslink.text) # Download the memory from AWS bucket
	with open(fullpath, 'wb') as f: # Save to the specified path on disk
		f.write(downloadmemory.content)
