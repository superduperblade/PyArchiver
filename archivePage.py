from playwright.sync_api import sync_playwright, Route, Request, Response

import os
import time
from pathlib import Path
class PageArchiver:
    def __init__(self,url,args):
        self.url = url
        self.args = args


    def on_request(request):
       
       print("outbound -> ",request.url)
    
    def on_responce(request):
       print("inbound -> "+request.url)


    def handle_route(self,route: Route) -> None:
       responce = route.fetch()

       body = responce.text()
       
       print(body)

       route.continue_()

    def archivePage(self):
      args = self.args

      #todo auto populate
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
        
        page.route("**/*",self.handle_route)
        page.goto(self.url,wait_until="networkidle",timeout=args.timeout)
    

        


        html = page.content()


        #make sure folder exists
        Path(args.outdir).mkdir(parents=True,exist_ok=True)
        with open(os.path.join(args.outdir,filename+".html"),"w",encoding="utf-8") as file:
           file.write(html)


        if args.screenshot == True:
           page.screenshot(path=os.path.join(args.outdir,filename+".png"),full_page=True)
        
        if args.pdf == True:
           page.pdf(path= os.path.join(args.outdir,filename+".pdf"))



