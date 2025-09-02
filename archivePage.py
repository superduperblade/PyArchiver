class PageArchiver:
    def __init__(self,url,outdir):
        self.url = url
        self.outdir = outdir


    def archivePage(self):
        print("Starting achive of url "+ self.url)

