from pymongo import MongoClient
from crawler import Crawler
from indexer import Indexer
from parser import Parser
from search_engine import SearchEngine


def connectDataBase():
    # Create a database connection object using pymongo
    client = MongoClient('mongodb://localhost:27017/')
    db = client['FinalProject']
    return db

def crawl():
    db = connectDataBase()
    col = db['pages']

    seed = 'https://www.cpp.edu/engineering/ce/index.shtml'
    num_targets = 25

    print(f"Starting to crawl {seed} for {num_targets} targets")
    crawler = Crawler(col, seed, num_targets)
    targets_found = crawler.crawlerThread()
    print(f"Finished crawling. Found {targets_found}")


def parse():
    db = connectDataBase()
    col = db['pages']

    print(f"Starting to parse pages flagged by crawler")
    parser = Parser(col)
    parser.parse_all_faculty_pages()
    print(f"Done parsing")


def index():
    db = connectDataBase()

    print()
    print("Starting to index")
    indexer = Indexer(db)
    indexer.create_index()
    print("Indexing complete")


def search():
    db = connectDataBase()

    print()
    print("Starting search engine")
    search_engine = SearchEngine(db)

    while True:
        print()
        query = input("Enter search query (or 'q' to quit): ")
        if query.lower() == 'q':
            break

        results, search_time = search_engine.search(query)

        if not results:
            print()
            print("No results")
            continue

        search_engine.display_results(results, query, search_time)


def all():
    crawl()
    parse()
    index()
    search()


def main():
    while True:
        print()
        print("Final Project")
        print("1. Run crawler")
        print("2. Run parser")
        print("3. Build index")
        print("4. Start search")
        print("5. Run all")
        print("6. Exit")
        print()

        choice = input("Enter your selection (1-6): ")

        if choice == '1':
            crawl()
        elif choice == '2':
            parse()
        elif choice == '3':
            index()
        elif choice == '4':
            search()
        elif choice == '5':
            all()
        elif choice == '6':
            print()
            print("Exiting")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()