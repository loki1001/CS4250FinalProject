# parser.py
from bs4 import BeautifulSoup

class Parser:
    def __init__(self, col):
        self.col = col

    # Information from the header
    def extract_header(self, soup):
        info = {}

        name_header = soup.find('h1')
        if name_header:
            info['name'] = name_header.get_text().strip()
        else:
            info['name'] = ""

        title_dept = soup.find('span', {'class': 'title-dept'})
        if title_dept:
            parts = title_dept.get_text().strip().split(', ')
            if len(parts) > 0:
                info['title'] = parts[0]
            else:
                info['title'] = ""

            if len(parts) > 1:
                info['department'] = parts[1]
            else:
                info['department'] = ""

            if len(parts) > 2:
                info['college'] = parts[2]
            else:
                info['college'] = ""
        else:
            info['title'] = ""
            info['department'] = ""
            info['college'] = ""

        left_header_menu = soup.find('div', {'class': 'menu-left'})
        if left_header_menu:
            email = left_header_menu.find('a')
            if email:
                info['email'] = email.get_text().strip()
            else:
                info['email'] = ""

            phone = left_header_menu.find('p', {'class': 'phoneicon'})
            if phone:
                info['phone'] = phone.get_text().strip()
            else:
                info['phone'] = ""

        right_header_menu = soup.find('div', {'class': 'menu-right'})
        if right_header_menu:
            office = right_header_menu.find('a')
            if office:
                info['office'] = office.get_text().strip()
            else:
                info['office'] = ""

            timing = right_header_menu.find('span', {'class': 'odd'})
            if timing:
                info['timing'] = timing.get_text().strip()
            else:
                info['timing'] = ""

        return info


    # Information from the main part (sections with yellow highlight on the top)
    def extract_main(self, soup):
        main = {}

        for blurb in soup.find_all('div', {'class': 'blurb'}):
            section_text = blurb.find('div', {'class': 'section-text'})
            if section_text:
                title = section_text.get_text().strip()

                section = blurb.find('div', {'class': 'section-menu'})
                if section:
                    for br in section.find_all('br'):
                        br.replace_with('\n')

                    full_text = section.get_text().strip()

                    content = []
                    for line in full_text.split('\n'):
                        line = line.strip()
                        if line:
                            content.append(line)

                    main[title] = content
                    '''
                    content = []
                    para = section.find_all('p')
                    for p in para:
                        text = p.get_text().strip()
                        if text:
                            content.append(text)

                    for item in section.find_all('li'):
                        content.append(item.get_text().strip())

                    col_div = section.find('div', {'class': 'col'})
                    if col_div and not para and not section.find_all('li'):
                        for br in col_div.find_all('br'):
                            br.replace_with('\n')

                        lines = col_div.get_text().strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                content.append(line)

                main[title] = content
                '''

        return main


    # Information from the side part / accolades (green headers)
    def extract_accolades(self, soup):
        accolades = {}

        for accolade in soup.find_all('div', {'class': 'accolades'}):
            section_text = accolade.find('h2')
            if section_text:
                title = section_text.get_text().strip()

                for br in accolade.find_all('br'):
                    br.replace_with('\n')

                full_text = accolade.get_text().strip()
                content = []
                for line in full_text.split('\n'):
                    line = line.strip()
                    if line and line != title:
                        content.append(line)

                accolades[title] = content

                '''
                title = section_text.get_text().strip()
                content = []

                for paragraph in accolade.find_all('p'):
                    links = paragraph.find_all('a')
                    paragraph_text = paragraph.get_text().strip()

                    for link in links:
                        paragraph_text = paragraph_text.replace(link.get_text().strip(), '').strip()

                    if paragraph_text:
                        content.append(paragraph.get_text().strip())

                    for link in links:
                        href = link.get('href')
                        if href:
                            link_text = f"{link.get_text().strip()}: {href}"
                            content.append(link_text)

                for item in accolade.find_all('li'):
                    content.append(item.get_text().strip())

                if not content:
                    for br in accolade.find_all('br'):
                        br.replace_with('\n')

                    h2_tag = accolade.find('h2')
                    if h2_tag:
                        text_after_h2 = ''
                        for content_node in h2_tag.next_siblings:
                            if hasattr(content_node, 'get_text'):
                                text_after_h2 += content_node.get_text()
                            elif hasattr(content_node, 'strip'):
                                text_after_h2 += content_node.strip()

                        lines = text_after_h2.strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                content.append(line)

                accolades[title] = content
        '''

        return accolades


    def parse_faculty_page(self, page_data):
        try:
            soup = BeautifulSoup(page_data['html'], 'html.parser')

            header = self.extract_header(soup)
            blurbs = self.extract_main(soup)
            accolades = self.extract_accolades(soup)

            faculty_info = {}

            faculty_info.update(header)

            faculty_info['sections'] = {}
            faculty_info['sections'].update(blurbs)
            faculty_info['sections'].update(accolades)

            # Dump for indexing purposes
            all_content = [
                header['name'],
                header['title'],
                header['department'],
                header['college'],
                header['email'],
                header['phone'],
                header['office'],
                header['timing']
            ]

            for title, items in faculty_info['sections'].items():
                all_content.append(title)
                all_content.extend(items)

            faculty_info['content'] = ' '.join(all_content)

            return faculty_info
        except Exception as e:
            print(e)

    def parse_all_faculty_pages(self):
        target_pages = self.col.find({"target": True})
        parsed_count = 0

        for page in target_pages:
            try:
                parsed_data = self.parse_faculty_page(page)
                if parsed_data:
                    self.col.update_one(
                        {"_id": page["_id"]},
                        {"$set": {
                            "parsed_data": parsed_data,
                            "processed": True
                        }}
                    )
                    parsed_count += 1
                    print(f"Successfully parsed page {parsed_count}: {page['url']}")
            except Exception as e:
                print(f"Error parsing {page['url']}: {e}")

        print(f"Finished parsing {parsed_count} faculty pages")