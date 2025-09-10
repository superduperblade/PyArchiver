import argparse
import os
import string
import re
from urllib.parse import urlparse, urlunparse, unquote, urljoin
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from adblockparser import AdblockRules

# -------------------------------
# Helper functions
# -------------------------------
def remove_punctuation_except_dot(text):
    punctuation_to_remove = string.punctuation.replace('.', '')
    return ''.join(char for char in text if char not in punctuation_to_remove)

def get_filename_from_url(url):
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    return filename or "index.html"

def is_html_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.scheme.startswith("http"):
        return parsed.path.endswith(".html") or parsed.path == "" or parsed.path.endswith("/")
    return False

def downloadAttribute(url, outpath):
    print("Sending request to:", url)
    parsed = urlparse(url)
    stripped = parsed._replace(query="", fragment="")
    filename = remove_punctuation_except_dot(urlunparse(stripped))
    Path(outpath).mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        filepath = os.path.join(outpath, filename)
        with open(filepath, "wb") as file:
            file.write(response.content)
        print("Downloaded file:", filename)
        return filename
    except Exception as e:
        print("Failed to download file:", filename, "Error:", e)
        return None

def scan_asset_file(filepath, outdir, base_url):
    """Scan JS or CSS file for URLs and download them."""
    downloaded_files = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return downloaded_files

    # CSS urls: url(...)
    urls_css = re.findall(r'url\((?:\'|")?(.*?)(?:\'|")?\)', content)
    # JS urls: "http(s)://..." or 'http(s)://...'
    urls_js = re.findall(r'["\'](https?://[^"\']+)["\']', content)

    all_urls = set(urls_css + urls_js)

    for url in all_urls:
        if not url.startswith("data:"):
            full_url = urljoin(base_url, url)  # ✅ resolve relative
            filename = downloadAttribute(full_url, outdir)
            if filename:
                downloaded_files.append(filename)
    return downloaded_files

# -------------------------------
# Main parsing function
# -------------------------------
def parseUrl(url, outdir, args, filetype=".html"):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    braveExe = args.bexe
    shouldPDF = args.pdf
    shouldScreenshot = args.screenshot

    with sync_playwright() as play:
        browser = play.chromium.launch(
            headless=args.nHeadless,
            executable_path=braveExe,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()
        print("Loading page:", url)
        page.goto(url, wait_until="networkidle", timeout=60000)

        fileName = get_filename_from_url(url)
        if not fileName.endswith(filetype):
            fileName += filetype

        # Parse HTML
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Prepare assets folder
        assetDir = "assets"
        Path(os.path.join(outdir, assetDir)).mkdir(parents=True, exist_ok=True)

        # Download assets from HTML
        for tag in soup.find_all(["link", "script", "img"]):
            attr = "src" if tag.name in ["script", "img"] else "href"
            link = tag.get(attr) or tag.get("data-src")

            if link and not link.startswith("data:") and not is_html_link(link):
                # ✅ FIX: resolve relative paths
                full_url = urljoin(url, link)

                downloaded_filename = downloadAttribute(full_url, os.path.join(outdir, assetDir))
                if downloaded_filename:
                    tag[attr] = os.path.join(assetDir, downloaded_filename)
                    # If JS or CSS, scan it for additional URLs
                    if full_url.endswith(".js") or full_url.endswith(".css"):
                        scan_asset_file(os.path.join(outdir, assetDir, downloaded_filename),
                                        os.path.join(outdir, assetDir),
                                        url)

        # Save final HTML
        with open(os.path.join(outdir, fileName), "w", encoding="utf-8") as file:
            file.write(str(soup))

        # Optional PDF or screenshot
        if shouldPDF:
            page.pdf(path=os.path.join(outdir, fileName + ".pdf"))
        if shouldScreenshot:
            page.screenshot(path=os.path.join(outdir, fileName + "_screenshot.png"), full_page=True)

        print("Archiving complete:", os.path.join(outdir, fileName))
        browser.close()

# -------------------------------
# Argument parser
# -------------------------------
parser = argparse.ArgumentParser(description="Site Archiver")
parser.add_argument("--site", default="", help="The site to parse")
parser.add_argument("--outdir", default=os.path.join(os.curdir, "site"), help="Directory to output files to")
parser.add_argument("--bexe", default="", help="Path to the Brave executable")
parser.add_argument("--nHeadless", action="store_false", help="Don't run in headless mode")
parser.add_argument("--pdf", action="store_true", help="Make a PDF of the page")
parser.add_argument("--screenshot", action="store_true", help="Take a screenshot of the page")
parser.add_argument("--iAdblock", action="store_true", help="Use a custom adblock list")
args = parser.parse_args()

url = args.site
outdir = args.outdir

if not url.startswith("http"):
    print("Prepended http:// to URL")
    url = "http://" + url

# Optional: download adblock list
if args.iAdblock:
    adblock_path = os.path.join(outdir, "adblock.txt")
    if not os.path.exists(adblock_path):
        print("Downloading EasyList...")
        response = requests.get("https://easylist.to/easylist/easylist.txt")
        with open(adblock_path, "w", encoding="utf-8") as f:
            f.write(response.text)

# Run the archiver
parseUrl(url=url, outdir=outdir, args=args)
