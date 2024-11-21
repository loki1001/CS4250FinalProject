import os
from parser import parse_faculty_page


def parse_all(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.html'):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # page data from crawler
            page_data = {
                'html': html_content,
                'url': filename,
                'department': 'Civil Engineering'
            }

            parsed_data = parse_faculty_page(page_data)

            if parsed_data:
                print(f"Parsed data for {filename}:")
                print(f"Name: {parsed_data['name']}")
                print(f"Title: {parsed_data['title']}")
                print(f"Department: {parsed_data['department']}")
                print(f"College: {parsed_data['college']}")
                print(f"Email: {parsed_data['email']}")
                print(f"Phone: {parsed_data['phone']}")
                print(f"Office: {parsed_data['office']}")
                print(f"Timing: {parsed_data['timing']}")
                print(f"Sections: {parsed_data['sections']}")
                print(f"Content: {parsed_data['content']}")
                print('----------------------------------------------------------------------------------------------')
            else:
                print(f"Failed to parse {filename}")
                print('----------------------------------------------------------------------------------------------')

if __name__ == '__main__':
    folder_path = 'downloaded_faculty_pages'
    parse_all(folder_path)
