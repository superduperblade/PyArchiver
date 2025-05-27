import argparse
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description="App")
parser.add_argument("--site", default="", help="The site to parse")
parser.add_argument("--outdir", default=os.curdir, help="Directory to output files to")
parser.add_argument("--bexe",default="",help="path to the brave executable")
parser.add_argument("--nHeadless", action="store_false", help="Dont run in headless mode")
args  =  parser.parse_args()

url = args.site
outdir = args.outdir
braveExe = args.bexe




Path(outdir).mkdir(parents=True, exist_ok=True)

with sync_playwright() as play:
        browser = play.chromium.launch(
            headless = args.nHeadless,
            executable_path= braveExe,
            args=["--no-sandbox","--disable-dev-shm-usage"]
        )

        page = browser.new_page()
        page.goto(url,wait_until="networkidle")
        
        
        # Stops the browser from exiting immidetly
        print("Press enter to end program!")
        input()
