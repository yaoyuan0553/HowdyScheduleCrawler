import requests
import html5lib
import sys
import time
import datetime
from bs4 import BeautifulSoup

session = requests.Session()


USERNAME = 'yaoyuan0553'
PASSWORD = '0F9(20)-Yg*14'
base_url = 'https://compass-ssb.tamu.edu'
login_url = 'https://compass-sso.tamu.edu:443/ssomanager/c/SSB?pkg=bwykfcls.p_sel_crse_search'
referer_url = 'https://cas.tamu.edu/cas/login?service=https%3A%2F%2Fcompass-sso.tamu.edu%3A443%2Fssomanager%2Fc%2FSSB%3Bjsessionid%3DrnCyUwU8GZI6Z4N_I-f6g5B6wx65qnJgrtMABFKdE-uyZdwN4E52%21-280416030%3Fpkg%3Dbwykfcls.p_sel_crse_search'

# get page to get csrf and lt
rget = session.get(login_url)
print rget.url, rget
csrftoken = rget.cookies['csrftoken']
page = BeautifulSoup(rget.text, 'html.parser')
tag = page.find('input', {'name': 'lt'})
lt_value = tag.attrs['value']
header = {'Referer':referer_url}
payload = dict(csrfmiddlewaretoken=csrftoken, username=USERNAME, password=PASSWORD,
                lt=lt_value, _eventId='submit')

# post form to log in
main_page = session.post(rget.url, headers=header, data=payload)
if main_page.status_code != 200:    # if 200 then successfully logged in
    print 'Login failed! Exiting...\n'
    sys.exit(-1)    ##### could potentially use a class/function to replace this

# now have access to the main page which is the term seleciton page 
main_page_soup = BeautifulSoup(main_page.text, 'html.parser')
major_selection_url = base_url
for tag in main_page_soup.findAll('form'):
    r = tag.get('onsubmit')
    if r != None:
        major_selection_url += tag.get('action')

term_form = dict(p_calling_proc='P_CrseSearch', p_term='201631')
major_page = session.post(major_selection_url, data=term_form)
if major_page.status_code != 200:
    print 'Login failed! Exiting...\n'
    sys.exit(-1)

subj_list = []
# get abbr.'s for all majors while on the major's page
major_page_soup = BeautifulSoup(major_page.text, 'html.parser')
sel_subj_tag = major_page_soup.find('select', {'name':'sel_subj'})
for option_tag in sel_subj_tag.find_all('option'):
    subj_list.append(option_tag.attrs['value'])


def generate_major_form(major, term_in):
    return {
        'rsts':'dummy',
        'crn':'dummy',
        'term_in':term_in,
        'sel_subj': ['dummy'] + major,
        'sel_day':'dummy',
        'sel_schd':'dummy',
        'sel_insm':'dummy',
        'sel_camp':'dummy',
        'sel_levl':'dummy',
        'sel_sess':'dummy',
        'sel_instr':'dummy',
        'sel_ptrm':['dummy','%'],
        'sel_attr':'dummy',
        'sel_crse':'',
        'sel_title':'',
        #'sel_ptrm':'%',
        'sel_from_cred':'',
        'sel_to_cred':'',
        'begin_hh':'0',
        'begin_mi':'0',
        'begin_ap':'x',
        'end_hh':'0',
        'end_mi':'0',
        'end_ap':'x',
        'path':'1',
        'SUB_BTN':'Course Search '
    }

major_form = generate_major_form(['ACCT', 'CSCE'], '201631')

course_url = base_url
for tag in major_page_soup.findAll('form'):
    if tag.has_attr('onsubmit'):
        course_url += tag.get('action')

course_page = session.post(course_url, headers={'Referer': course_url}, data=major_form)

def is_number(s):
    try:
        num = int(s)
        return (True, num)
    except ValueError:
        return (False, None)

def construct_course_form(sel_subj, sel_crse):
    return {
        'term_in':'201631',
        'sel_subj': ['dummy', sel_subj],
        'SEL_CRSE': sel_crse,
        'SEL_TITLE':'',
        'BEGIN_HH':'0',
        'BEGIN_MI':'0',
        'BEGIN_AP':'a',
        'SEL_DAY':'dummy',
        'SEL_PTRM':'dummy',
        'END_HH':'0',
        'END_MI':'0',
        'END_AP':'a',
        'SEL_CAMP':'dummy',
        'SEL_SCHD':'dummy',
        'SEL_SESS':'dummy',
        'SEL_INSTR':['dummy', '%'],
        #'SEL_INSTR':'%',
        'SEL_ATTR':['dummy', '%'],
        #'SEL_ATTR':'%',
        'SEL_LEVL':['dummy', '%'],
        #'SEL_LEVL':'%',
        'SEL_INSM':'dummy',
        'sel_dunt_code':'',
        'sel_dunt_unit':'',
        'call_value_in':'BASIC',
        'rsts':'dummy',
        'crn':'dummy',
        'path':'1',
        'SUB_BTN':'View Sections'
    }

course_dict = dict()
course_page_soup = BeautifulSoup(course_page.text, 'html.parser')
for i, table in enumerate(course_page_soup.find_all('table', class_='datadisplaytable')):
    table_title = table.find('tr').text.strip('\n')
    course_dict[table_title] = []
    for tr in table.find_all('tr'):
        for td in tr.find_all('td'):
            isNumber, courseNumber = is_number(td.text)
            if isNumber is True:
                course_dict[table_title].append(courseNumber)


cf = construct_course_form('CSCE', '411')
section_page = session.post(course_url, headers={'Referer':course_url}, data=cf)

section_page_soup = BeautifulSoup(section_page.text, 'html5lib')
table = section_page_soup.find('table', class_='datadisplaytable')


class TimeRangeFinder:
    min_time = datetime.time(hour=23, minute=59)
    max_time = datetime.time(hour=0, minute=0)

    def time_constructor(self, time_period_string):
        start, end = time_period_string.split('-')
        start_time = datetime.datetime.strptime(start, '%I:%M %p').time()
        end_time = datetime.datetime.strptime(end, '%I:%M %p').time()

        return (start_time, end_time)

    def time_filter(self, t1, t2):
        self.min_time = min(t1, self.min_time)
        self.max_time = max(t2, self.max_time)



#class CourseInfoScraper:
#    trf = TimeRangeFinder()
    
#    def __init__(self, course


trf = TimeRangeFinder()


def record_minmax(table):
    count = 0
    for tr in table.find_all('tr'):
        if tr.has_attr('style'):
            time_tag = tr.find_all('td')[9]
            count += 1
            try:
                start, end = trf.time_constructor(time_tag.text)
            except ValueError:
                continue
            trf.time_filter(start, end)
    print count


def parse_section_data():
    for subject_name in course_dict:
        for course_id in course_dict[subject_name]:
            cf = construct_course_form(subject_name, course_id)
            section_page = session.post(course_url, headers={'Referer':course_url}, data=cf)
            section_page_soup = BeautifulSoup(section_page.text, 'html5lib')
            table = section_page_soup.find('table', class_='datadisplaytable')
            record_minmax(table)
            time.sleep(2)


register_url = base_url + '/pls/PROD/bwykfreg.P_AltPin1?deviceType=C'
register_form = dict(TERM_IN='201631', sel_crn=['dummy', '28851 201631'], 
                     assoc_term_in=['dummy', '201631'], ADD_BTN=['dummy', 'Register'])

register_page = session.post(register_url, headers={'Referer':section_page.url}, data=register_form)

