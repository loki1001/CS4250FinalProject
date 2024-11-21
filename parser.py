# parser.py
from bs4 import BeautifulSoup


# Information from the header
def extract_header(soup):
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
def extract_main(soup):
    main = {}

    for blurb in soup.find_all('div', {'class': 'blurb'}):
        section_text = blurb.find('div', {'class': 'section-text'})
        if section_text:
            title = section_text.get_text().strip()

            content = []
            section = blurb.find('div', {'class': 'section-menu'})
            if section:
                for item in section.find_all('li'):
                    content.append(item.get_text().strip())

            main[title] = content

    return main


# Information from the side part / accolades (green headers)
def extract_accolades(soup):
    accolades = {}

    for accolade in soup.find_all('div', {'class': 'accolades'}):
        section_text = accolade.find('h2')
        if section_text:
            title = section_text.get_text().strip()

            content = []
            for item in accolade.find_all('li'):
                content.append(item.get_text().strip())

            accolades[title] = content

    return accolades


def parse_faculty_page(page_data):
    try:
        soup = BeautifulSoup(page_data['html'], 'html.parser')

        header = extract_header(soup)
        blurbs = extract_main(soup)
        accolades = extract_accolades(soup)

        faculty_info = {
            "url": page_data['url'],
            "department": page_data['department']
        }

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
