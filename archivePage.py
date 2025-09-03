from playwright.sync_api import sync_playwright
import os
import time
class PageArchiver:
    def __init__(self,url,args):
        self.url = url
        self.args = args


    def archivePage(self):
      args = self.args

      #auto populate
      filename = "example"


      with sync_playwright() as play:
        browser = play.chromium.launch(
            headless = args.nHeadless,
            executable_path= args.bexe,
            args=["--no-sandbox","--disable-dev-shm-usage"]
        )

        # waits until the page has loaded
        page = browser.new_page()
        print("Sending request to: "+self.url)
        page.goto(self.url,wait_until="networkidle",timeout=args.timeout)
        


        if args.screenshot == True:
           page.screenshot(path=os.path.join(args.outdir,filename+".png"),full_page=True)
        
        if args.pdf == True:
           page.pdf(path= os.path.join(args.outdir,filename+".pdf"))



