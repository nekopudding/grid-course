'''
UBC Public Course Schedule Web Scrapler

Using Python 3.9.9
Libraries: requests, bs4
'''

import json
import requests
from bs4 import BeautifulSoup
import time

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7', 'Cache-Control': 'max-age=0', 'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"', 'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': '"macOS"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'}

session_year = '2022'
session_cd = 'S'

#print(requests.get('https://legendword.com/files/print-headers.php', headers=headers).text)

def make_request(params):
    r = requests.get('https://courses.students.ubc.ca/cs/courseschedule', headers=headers, params=params)
    return r.text

def fetch_subjects():
    txt = make_request({'pname': 'subjarea', 'tname': 'subj-all-departments', 'sessyr': session_year, 'sesscd': session_cd})
    soup = BeautifulSoup(txt, 'html.parser')

    table_links = soup.select('#mainTable tr a')
    return [ i.string for i in table_links ]

def fetch_courses(subject):
    txt = make_request({'pname': 'subjarea', 'tname': 'subj-department', 'dept': subject, 'sessyr': session_year, 'sesscd': session_cd})
    soup = BeautifulSoup(txt, 'html.parser')

    table_links = soup.select('#mainTable tr a')
    return [ i.string.split(" ")[1] for i in table_links ]

def fetch_sections(subject, course):
    txt = make_request({'pname': 'subjarea', 'tname': 'subj-course', 'dept': subject, 'course': course, 'sessyr': session_year, 'sesscd': session_cd})
    soup = BeautifulSoup(txt, 'html.parser')

    r = []
    table_rows = soup.select('.table.table-striped.section-summary tr')
    del table_rows[0]
    for row in table_rows:
        s = {}
        cols = row.contents
        s['section'] = cols[1].select_one('a').string.split(' ')[2]
        s['id'] = subject + ' ' + course + ' ' + s['section']
        s['type'] = cols[2].string
        if s['type'] == 'Waiting List':
            continue
        s['term'] = cols[3].string
        s['delivery'] = cols[4].string
        # s['interval'] = cols[5].string
        if (not cols[6].string) or len(cols[6].string.strip()) == 0:
            continue
        s['days'] = cols[6].string
        if (not cols[7].string) or len(cols[7].string.strip()) == 0 or (not cols[8].string) or len(cols[8].string.strip()) == 0:
            continue
        s['start_time'] = cols[7].string
        s['end_time'] = cols[8].string
        if s['days']:
            s['days'] = s['days'].split(' ')
            for i in ['type', 'term', 'delivery', 'start_time', 'end_time']:
                if s[i]:
                    s[i] = s[i].strip()
        r.append(s)
    if len(r) == 0:
        return None
    return r


if __name__ == '__main__':
    res = []
    skipped = []
    subjects = fetch_subjects()
    time.sleep(2)
    for s in subjects:
        courses = fetch_courses(s)
        time.sleep(2)
        for c in courses:
            print(s, c)
            sections = None
            try:
                sections = fetch_sections(s, c)
            except:
                print('[skipped due to error]')
                skipped.append({'subject': s, 'course': c})
                continue

            if sections == None:
                print('[all sections skipped]')
            else:
                res.append({'id': s + ' ' + c, 'subject': s, 'course': c, 'sections': sections})
            
            time.sleep(2)
    # print('[skipped courses]')
    # print(skipped)
    print('[writing to file]')
    with open('ubc-' + session_year + session_cd + '.json', 'w') as f:
        f.write(json.dumps(res))
    print('[program finished]')
