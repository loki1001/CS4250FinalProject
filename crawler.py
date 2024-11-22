# crawler.py
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
import urllib.request

from bs4 import BeautifulSoup
from pymongo import MongoClient

# Define frontier stack
frontier = ['https://www.cpp.edu/engineering/ce/index.shtml']

# Define MongoDB connection
client = MongoClient("localhost", 27017)
db = client['local']
col = db['pages']

# Define helper functions for storing page data
def storePage(url, html):
    col.update_one({"url": url}, { "$set": {
        "url": url,
        "html": html.decode('utf-8')
    }}, upsert=True)

def flagTargetPage(url):
    col.update_one({"url": url}, { "$set": {
        "target": True
    }})

def checkExists(url):
    results = col.find({"url": url})
    return len(list(results)) > 0

# Define crawler function
def crawlerThread(frontier, num_targets):
    targets_found = 0
    while len(frontier) > 0:
        # Fetch URL from top of frontier
        url = frontier[0]
        try:
            # Fetch HTML content
            with urllib.request.urlopen(url) as response:
                html = response.read()
            # Initialize BeautifulSoup
            bs = BeautifulSoup(html, 'html.parser')
            # Store page
            storePage(url, html)
            # Check target 
            if len(bs.find_all(class_="fac-staff")) == 1:
                targets_found += 1
                flagTargetPage(url)
            # Check if all targets found
            if targets_found == num_targets:
                # Clear frontier and break loop if targets reached
                frontier.clear()
                break
            else:
                # Add unvisted links to frontier if target count not reached
                for link in bs.find_all('a', href=True):
                    href = urljoin(url, link.get('href'))
                    if not checkExists(href):
                        frontier.append(href)
        # Handle potential BS4 errors
        except HTTPError as e:
            print(f"HTTP Error: {e}")
        except URLError as e:
            print(f"URL Error: {e}")
        except Exception:
            print("Unknown exception")
        # Remove current URL from frontier
        del frontier[0]

# Initialize crawler thread
crawlerThread(frontier, 25)