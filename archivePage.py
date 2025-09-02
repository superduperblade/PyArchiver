from playwright.sync_api import sync_playwright
import time
class PageArchiver:
    def __init__(self,url,args):
        self.url = url
        self.args = args


    def archivePage(self):
      with sync_playwright() as play:
        browser = play.chromium.launch(
            headless = self.args.nHeadless,
            executable_path= self.args.bexe,
            args=["--no-sandbox","--disable-dev-shm-usage"]
        )

        # waits until the page has loaded
        page = browser.new_page()
        print("Sending request to: "+self.url)
        page.goto(self.url,wait_until="networkidle",timeout=60000)
        time.sleep(100)

