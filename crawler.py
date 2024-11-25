# crawler.py
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
import urllib.request
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, col, seed, num_targets):
        self.col = col
        self.frontier = [seed]
        self.visited = []
        self.num_targets = num_targets

    # Define helper functions for storing page data
    def storePage(self, url, html):
        self.col.update_one({"url": url}, {"$set": {
            "url": url,
            "html": html.decode('utf-8')
        }}, upsert=True)

    def flagTargetPage(self, url):
        self.col.update_one({"url": url}, {"$set": {
            "target": True
        }})

    # Define crawler function
    def crawlerThread(self):
        targets_found = 0

        while len(self.frontier) > 0:
            # Fetch URL from top of frontier
            url = self.frontier.pop(0)

            try:
                # Fetch HTML content
                with urllib.request.urlopen(url) as response:
                    html = response.read()
                # Initialize BeautifulSoup
                bs = BeautifulSoup(html, 'html.parser')
                # Store page
                self.storePage(url, html)
                # Mark URL as visited
                self.visited.append(url)
                # Check target
                if len(bs.find_all(class_="fac-staff")) == 1:
                    targets_found += 1
                    self.flagTargetPage(url)
                # Check if all targets found
                if targets_found == self.num_targets:
                    # Clear frontier and break loop if targets reached
                    self.frontier.clear()
                    break
                else:
                    # Add unvisted links to frontier if target count not reached
                    for link in bs.find_all('a', href=True):
                        href = urljoin(url, link.get('href'))
                        if not href in self.visited:
                            self.frontier.append(href)
            # Handle potential BS4 errors
            except HTTPError as e:
                print(f"HTTP Error: {e}")
            except URLError as e:
                print(f"URL Error: {e}")
            except Exception as e:
                print(f"Unknown exception: {e}")

        return targets_found