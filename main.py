import argparse
import os
import urllib
from urllib.parse import  urlparse, urlunparse
from pathlib import Path
import urllib.request
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import string

def remove_punctuation_except_dot(text):
    # Create a set of punctuation without the dot
    punctuation_to_remove = string.punctuation.replace('.', '')
    # Remove all unwanted punctuation
    return ''.join(char for char in text if char not in punctuation_to_remove)

def get_filename_from_url(url):
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(path)
        return filename or "index.html"

def is_html_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.scheme.startswith("http"):
        return parsed.path.endswith(".html") or parsed.path == "" or parsed.path.endswith("/")
    return False

def downloadAttribute(url,outpath):
       print ("sending request to: "+url)
       parsed = urlparse(url)
       stripped = parsed._replace(query="", fragment="")
      
       filename = remove_punctuation_except_dot( urlunparse(stripped))
       Path(outdir).mkdir(parents=True, exist_ok=True)

       headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }


       try:
             responce   = requests.get(url,headers)
             responce.raise_for_status()
             with open(os.path.join(outpath,filename),"wb") as file:
                   file.write(responce.content)
            
             print("Downloaded file : "+filename)
       except Exception as e:
             print("Failed to download file "+filename)
             
    
       return filename
def parseUrl(url,outdir,args,filetype=".html"):
    Path(outdir).mkdir(parents=True, exist_ok=True)
   
    braveExe = args.bexe
    shouldPDF = args.pdf
    shouldScreenshot = args.screenshot

    with sync_playwright() as play:
        browser = play.chromium.launch(
            headless = args.nHeadless,
            executable_path= braveExe,
            args=["--no-sandbox","--disable-dev-shm-usage"]
        )

        # waits until the page has loaded
        page = browser.new_page()
        print("Sending request to: "+url)
        page.goto(url,wait_until="networkidle",timeout=60000)
        
        fileName = get_filename_from_url(url) 
        if fileName.endswith(filetype) == False:
               fileName = fileName+filetype


        # Dowloads and relinks any files attached to it
        html =  page.content()
        soup = BeautifulSoup(html,"html.parser")

        Path(os.path.join(outdir,"assets")).mkdir(parents=True, exist_ok=True)
        assetDir ="assets"
        for tag in soup.find_all(["link","script","img"]):
               attr = "src" if tag.name in ["script","img"] else "href"
               link = tag.get(attr) or tag.get("data-src")

               if link and not link.startswith("data:"):
                     if is_html_link(link) == False:
                           test = downloadAttribute(url=link,outpath=os.path.join(outdir,assetDir))
                           tag[attr] = os.path.join(assetDir,test)



        with open(os.path.join(outdir,fileName),"w",encoding="utf-8") as file:
                file.write(str(soup))
        
        if shouldPDF:
                page.pdf(path=os.path.join(outdir,fileName+".pdf"))
        
        if shouldScreenshot:
                page.screenshot(path=os.path.join(outdir,fileName+"screenshot.png"),  full_page=True)


        # Stops the browser from exiting immidetly
        print("Press enter to end program!")
       # input()
        
parser = argparse.ArgumentParser(description="App")
parser.add_argument("--site", default="", help="The site to parse")
parser.add_argument("--outdir", default=os.path.join(os.curdir,"site"), help="Directory to output files to")
parser.add_argument("--bexe",default="",help="path to the brave executable")
parser.add_argument("--nHeadless", action="store_false", help="Dont run in headless mode")
parser.add_argument("--pdf",action="store_true",help="make a pdf of the page")
parser.add_argument("--screenshot",action="store_true",help="Take a screenshot of the page")
args  =  parser.parse_args()

url = args.site
outdir = args.outdir

if url.startswith("http") == False:
        print("Appeneded "+url+" to http://")
        url = "http://"+url


parseUrl(url=url,outdir=outdir,args=args)
