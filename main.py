import argparse
import os
import urllib
from urllib.parse import  urlparse, urlunparse
from pathlib import Path
import urllib.request
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from adblockparser import AdblockRules
import requests
import shutil
from archivePage import PageArchiver

parser = argparse.ArgumentParser(description="App")
parser.add_argument("--site", default="", help="The site to parse")
parser.add_argument("--outdir", default=os.path.join(os.curdir,"site"), help="Directory to output files to")
parser.add_argument("--bexe",default="",help="path to the brave executable")
parser.add_argument("--nHeadless", action="store_false", help="Dont run in headless mode")
parser.add_argument("--pdf",action="store_true",help="make a pdf of the page")
parser.add_argument("--screenshot",action="store_true",help="Take a screenshot of the page")
parser.add_argument("--iAdblock",action="store_true",help="Uses a custom adblocker alongside the brave adblocker")
args  =  parser.parse_args()

url = args.site
outdir = args.outdir

if url.startswith("http") == False:
        print("Appeneded "+url+" to http://")
        args.site = "http://"+url

if args.iAdblock:
      if os.path.exists(os.path.join(outdir,"adblock.txt")):
            print("Adblock list already exits skipping!")
      else:
            adblockerURL = "https://easylist.to/easylist/easylist.txt"
            print("Downloading EasyList...")
            response = requests.get(url)
            rules_raw = response.text.splitlines()


#if brave browser arg is empty attenmpt to find it on the users system (windows only)
if args.bexe == "":
       brave_path = shutil.which("brave.exe")
       if brave_path == "":
              print("Unable to find it on the users system exiting")
              exit(-2)
       else:
            args.bexe == brave_path       



page = PageArchiver(args.site,"./page")

page.archivePage()

#parseUrl(url=url,outdir=outdir,args=args)