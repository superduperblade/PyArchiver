from playwright.sync_api import sync_playwright
import time
class PageArchiver:
    def __init__(self,url,args):
        self.url = url
        self.args = args


    def archivePage(self):
      args = self.args
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
        


        if self.args.screenshot == True:
           page.screenshot(path=args.outdir,full_page=True)
        
        if self.args.pdf == True:
           page.pdf(path=self.args.outdir)



