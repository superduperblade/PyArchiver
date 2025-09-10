import argparse
from playwright.sync_api import sync_playwright, Route, Request, Response
import sqlite3
class Reader:
    def __init__(self,args):
                self.args = args
                self.setUpDatabaseConnections()
                pass
    

    def setUpDatabaseConnections(self):
         self.connection = sqlite3.connect(self.args.db)
         self.cursor = self.connection.cursor()

    def searchForUrlinDB(self,url):
        request = "SELECT * from WEBSITE WHERE url = ?"
        self.cursor.execute(request,(url,))
        row = self.cursor.fetchone()
        return row

    def handle_route(self,route: Route) -> None:
      
       responce = route.fetch()
       url = responce.url
       row = self.searchForUrlinDB(url)

       print("recived url +"+url)


       if row == None:
            route.continue_()
            return

       headers = row[1]
      
       body = row[2]
       status = row[3]
       
        
      
       print("allowed "+ body)

       #self.writeFile(os.path.join(str(self.routeDir),str(self.indicator)+extention),body)      





       route.fulfill(
         headers=headers,
         body=body,
         status=status
       )
       
    def run_browser(self):
        args = self.args
        with sync_playwright() as play:
            browser = play.chromium.launch(
            headless = False,
            executable_path= args.bexe,
            args=["--no-sandbox","--disable-dev-shm-usage"])

        # waits until the page has loaded
            page = browser.new_page()
            print("Sending request to: "+args.path)
        
            page.route("**/*",self.handle_route)
            page.goto(args.path,wait_until="networkidle",timeout=60000)

parser = argparse.ArgumentParser(description="App")
parser.add_argument("--path", default="", help="path contiaining the htlm to read from") 
parser.add_argument("--db",default="",help="The database to read from")
parser.add_argument("--bexe",default="",help="path to the brave executable")


args = parser.parse_args()



reader = Reader(args=args)

reader.run_browser()