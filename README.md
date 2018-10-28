# Steven Universe Downloader #

#### Small script for downloading steven universe episodes. ####

This script downloads all the available episodes of Steven Universe from a local copy of https://stevenuniver.se  
Please note that stevenuniver.se runs a cryptocoin miner in the background, they make this no secret.  
  
Files are downloaded one at the time and stored in a seperate directory per season.  
Downloads are named like S01E01 Gem glow.mp4  
  

* * *
  
usage: downloadsu.py [-h] [-o] [-v] source  
  
A simple CLI for downloading Steven Universe episodes.  
  
positional arguments:  
  source&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Path to local copy of http://stevenuniver.se  
  
optional arguments:  
  -h, --help&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;how this help message and exit  
  -o, --overwrite&nbsp;&nbsp;&nbsp;overwrite existing files, default=False  
  -v, --verbose&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;increase output verbosity  



