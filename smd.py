from tqdm import tqdm
import argparse
import json
import requests
import os

# Initialize parser
parser = argparse.ArgumentParser(description='Snapchat Memories Downloader version 0.2')
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
# https://patorjk.com/software/taag/#p=display&f=Ivrit&t=Snapchat%0AMemory%0ADownloader%0Av%200.2

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
           ___   ____                                     
 __   __  / _ \ |___ \                                    
 \ \ / / | | | |  __) |                                   
  \ V /  | |_| | / __/                                    
   \_/    \___(_)_____|                                   
                                                                                               
                                                   """)

snapurls = {} # Make a dictionary for snapchat memory dates and urls
errors = {} # Dictionary for memories that fail downloading for some reason
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

print("You have {} memories to download.\n".format(len(snapurls)))

# TODO: Look into threading the downloads, it's way too slow this way
def downloader(values):
	for key in tqdm(list(values)):
		awslink = requests.post(values[key]) # POST request to Snap URL and receive a link pointing to AWS bucket with your memory
		if not awslink.ok: # If HTTP status not 2xx
			print("HTTP error {err} occured for memory from {mem}.".format(err=awslink.status_code, mem=key))
			errors[key] = values[key] # add to error dictionary
			continue
		try: # Make the filename from the memory date and the AWS link extension
			filename = key + "." + awslink.text.split("/")[-1].split("?")[0].split(".")[1] 
		except KeyboardInterrupt:
			print("\nBye!")
			quit()
		except Exception as e: #sometimes fails with this, let's see whats up
			print(e)
			print("An error occured getting the filename or extension! The Snap link returned: " + awslink.text)
			errors[key] = values[key] # add to error dictionary
			continue
			
		try: # Get output full path on system
			fullpath = os.path.join(outputdir, filename)
		except KeyboardInterrupt:
			print("\nBye!")
			quit()
		except Exception as e: #sometimes fails with this, let's see whats up
			print(e)
			print("An error occured! The filename was supposed to be:" + filename)
			errors[key] = values[key] # add to error dictionary
			continue
		try: # Downloading the file and writing to disk
			downloadmemory = requests.get(awslink.text) # Download the memory from AWS bucket
			with open(fullpath, 'wb') as f: 
				f.write(downloadmemory.content) # Save to the specified path on disk
			del values[key] # Delete from dictionary
		except KeyboardInterrupt:
			print("\nBye!")
			quit()
		except Exception as e: #sometimes fails with this, let's see whats up
			print(e)
			print("An error occured writing the file to disk! The path was:" + fullpath)
			errors[key] = values[key] # add to error dictionary
			continue
			
downloader(snapurls) # Start the download function

if errors:
	print("...\n...\n...\nThere were some errors during download. Trying once more...\n")
	downloader(errors)
	if errors:
		print("...\n...\n...\nSorry, still couldn't download everything! There could be a problem with Snapchat's servers.")
		print("Very old memories also sometimes return HTTP 500 error. Contact Snapchat support?")
		print("If you want to query the links individually, you can do so with e.g. curl with a command like this:")
		print("curl \'SNAPLINK\' -X POST")
		print("Here are all of the memories that failed to return the AWS download links:\n")
		print(errors)
else:
	print("All memories downloaded. Bye!")
