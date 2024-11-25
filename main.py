# main.py
from pymongo import MongoClient
from crawler import Crawler
from parser import Parser


def connectDataBase():
    # Create a database connection object using pymongo
    client = MongoClient('mongodb://localhost:27017/')
    db = client['FinalProject']
    return db


# FOR TESTING
def view_parsed_data():
    db = connectDataBase()
    col = db['pages']

    # Find all documents that have been processed
    processed_pages = col.find({"processed": True})

    for page in processed_pages:
        print("\n" + "=" * 80)
        print(f"URL: {page['url']}")
        print("=" * 80)

        if 'parsed_data' in page:
            faculty_info = page['parsed_data']

            # Print basic information
            print("\nBasic Information:")
            print(f"Name: {faculty_info.get('name', 'N/A')}")
            print(f"Title: {faculty_info.get('title', 'N/A')}")
            print(f"Department: {faculty_info.get('department', 'N/A')}")
            print(f"College: {faculty_info.get('college', 'N/A')}")
            print(f"Email: {faculty_info.get('email', 'N/A')}")
            print(f"Phone: {faculty_info.get('phone', 'N/A')}")
            print(f"Office: {faculty_info.get('office', 'N/A')}")
            print(f"Timing: {faculty_info.get('timing', 'N/A')}")

            # Print sections
            if 'sections' in faculty_info:
                print("\nSections:")
                for section_title, content in faculty_info['sections'].items():
                    print(f"\n{section_title}:")
                    for item in content:
                        print(f"  - {item}")

            print(f"Content: {faculty_info.get('content', 'N/A')}")
        else:
            print("No parsed data available for this page")


def main():
    db = connectDataBase()
    col = db['pages']

    seed = 'https://www.cpp.edu/engineering/ce/index.shtml'
    num_targets = 25

    print(f"Starting to crawl {seed} for {num_targets} targets")
    crawler = Crawler(col, seed, num_targets)
    targets_found = crawler.crawlerThread()
    print(f"Finished crawling. Found {targets_found}")

    print(f"Starting to parse pages flagged by crawler")
    parser = Parser(col)
    parser.parse_all_faculty_pages()
    print(f"Done parsing")

if __name__ == '__main__':
    main()
    view_parsed_data()
