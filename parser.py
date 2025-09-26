import json
from bs4 import BeautifulSoup

def parse_html(file_path):
    with open(file_path, 'r', encoding='windows-1252', errors='ignore') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    sessions = []

    session_tables = soup.find_all('table', class_='trk')

    for table in session_tables:
        sHdr = table.find_all('tr', class_='sHdr')
        if not sHdr or len(sHdr) < 2:
            continue

        session_code = sHdr[0].find('a').text.strip()
        room = sHdr[0].find('td', class_='r').text.strip()
        session_title = sHdr[1].find('a').text.strip()
        session_type = sHdr[1].find('td', class_='r').text.strip()

        chairs = []
        for chair_row in table.find_all('tr'):
            if 'Chair:' in chair_row.text:
                chair_name = chair_row.find('a').text.strip()
                affiliation = chair_row.find('td', class_='r').text.strip()
                chairs.append({'name': chair_name, 'affiliation': affiliation, 'role': 'Chair'})
            if 'Co-Chair:' in chair_row.text:
                co_chair_name = chair_row.find('a').text.strip()
                co_chair_affiliation = chair_row.find('td', class_='r').text.strip()
                chairs.append({'name': co_chair_name, 'affiliation': co_chair_affiliation, 'role': 'Co-Chair'})

        papers = []
        paper_headers = table.find_all('tr', class_='pHdr')
        for header in paper_headers:
            time_paper_code = header.find('a').parent.text.strip()
            time, paper_code = time_paper_code.split(', Paper ')

            title_row = header.find_next_sibling('tr')
            title = title_row.find('span', class_='pTtl').text.strip()

            authors = []
            author_row = title_row.find_next_sibling('tr').find_next_sibling('tr')
            while author_row and not author_row.has_attr('class'):
                author_name_tag = author_row.find('a')
                affiliation_tag = author_row.find('td', class_='r')

                if author_name_tag and affiliation_tag:
                    author_name = author_name_tag.text.strip()
                    affiliation = affiliation_tag.text.strip()
                    authors.append({'name': author_name, 'affiliation': affiliation})

                author_row = author_row.find_next_sibling('tr')

            abstract_div = header.find_next('div', id=lambda x: x and x.startswith('Ab'))
            keywords = ''
            abstract = ''
            if abstract_div:
                keywords_span = abstract_div.find('span')
                if keywords_span:
                    keywords = [a.text.strip() for a in keywords_span.find_all('a')]
                abstract_p = abstract_div.find('strong', string='Abstract:')
                if abstract_p:
                    abstract = abstract_p.next_sibling.strip()

            papers.append({
                'time': time,
                'paper_code': paper_code,
                'title': title,
                'authors': authors,
                'keywords': keywords,
                'abstract': abstract
            })

        sessions.append({
            'session_code': session_code,
            'room': room,
            'session_title': session_title,
            'session_type': session_type,
            'chairs': chairs,
            'papers': papers
        })

    return sessions

def main():
    files = ['tuesday.html', 'wednesday.html', 'thursday.html']
    all_sessions = []
    for file in files:
        try:
            day = file.split('.')[0]
            sessions = parse_html(f'/Users/matto/Desktop/IROS/{file}')
            for session in sessions:
                session['day'] = day
            all_sessions.extend(sessions)
        except FileNotFoundError:
            print(f"Warning: {file} not found. Skipping.")

    with open('/Users/matto/Desktop/IROS/schedule.json', 'w') as f:
        json.dump(all_sessions, f, indent=2)

    print('Parsing complete. Data saved to schedule.json')

if __name__ == '__main__':
    main()
