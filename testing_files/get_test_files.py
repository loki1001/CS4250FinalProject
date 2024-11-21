import os
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_faculty_urls(directory_url):
    try:
        with urllib.request.urlopen(directory_url) as response:
            html_content = response.read().decode('utf-8')

        soup = BeautifulSoup(html_content, 'html.parser')

        faculty_urls = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')

            if href and '/faculty/' in href:
                full_url = urljoin(directory_url, href)
                faculty_urls.append(full_url)

        return faculty_urls

    except Exception as e:
        print(e)
        return []

def download_html_files(urls, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for url in urls:
        try:
            with urllib.request.urlopen(url) as response:
                html_content = response.read().decode('utf-8')

            filename = url.split('/')[-2] + '.html'
            filepath = os.path.join(download_folder, filename)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(html_content)

            print(f"Downloaded {url} to {filepath}")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    directory_url = 'https://www.cpp.edu/engineering/ce/faculty.shtml'
    faculty_urls = extract_faculty_urls(directory_url)
    download_html_files(faculty_urls, 'downloaded_faculty_pages')
