# Snapchat Memory Downloader

Decided to delete your Snapchat account, but still wish to keep your saved memories?
Snapchat currently provides no easy way to mass-download all of your memories. 
This script is intended to fix that.

## Operation
1. Install Python 3 and pip
2. Clone the repository and cd to the directory
3. Install the requirements `pip install -r requirements.txt`
4. Download your Snapchat data: https://support.snapchat.com/en-US/a/download-my-data
5. Extract the zip file
6. Run the script: `python smd.py -i /path/to/snapzip/json/memories_history.json -o /path/to/output/directory`
