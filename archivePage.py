from playwright.sync_api import sync_playwright, Route, Request, Response

import os
import time
from pathlib import Path
import string
from urllib.parse import urlparse
import sqlite3

class PageArchiver:
    def __init__(self,url,args):
        self.url = url
        self.args = args
        self.routeDir = os.path.join(self.args.outdir,"requests")
        Path(self.routeDir).mkdir(parents=True,exist_ok=True)
        self.indicator = 0

    def create_database(self,path):
     connection = sqlite3.connect(path)
     self.cursor = connection.cursor()

     sql_create_command = '''
     CREATE TABLE IF NOT EXISTS WEBSITE(ID interger primary key ,
     URL text,
     headers text,
     body text,
     status interger
     )'''
     self.cursor.execute(sql_create_command)

    def remove_punctuation_except_dot(text):
     punctuation_to_remove = string.punctuation.replace('.', '')
     return ''.join(char for char in text if char not in punctuation_to_remove)


    def writeFile(self,path,content):
       with open(path,"w",encoding="utf-8") as file:
          file.write(str(content))

   #handles inividual responces 
    # TEMPORARY WILL WRITE TO SQL DATABASE
    def writeResponceToDb(self,url,body,headers,code):
       with open(os.path.join(self.args.outdir,"db.db"),"w",encoding="utf-8") as file:
          file.write(url+":"+str(headers)+":"+str(body)+":"+str(code)+"\n")

    def handle_route(self,route: Route) -> None:
      

      
       self.indicator += 1

       responce = route.fetch()

       headers = responce.headers
       url = responce.url
       body = responce.body()
       status = responce.status
       
       extention = urlparse(url)

       extention = Path(extention.path).suffix

       #self.writeResponceToDb(url=url,headers=headers,body=body,code=status)
       #self.writeFile(os.path.join(str(self.routeDir),str(self.indicator)+extention),body)      



       print("url: ",url,"header: ",str(headers)," body: ",str(body),"\n")

       route.fulfill(
          status=status,
          headers=headers,
          body=body
       )

    def archivePage(self):
      args = self.args

      #todo auto populate
      filename = "example"

      self.create_database(os.path.join(args.outdir,"db_"+filename+".db"))


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



