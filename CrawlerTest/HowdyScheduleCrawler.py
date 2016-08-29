import exceptions
import requests
import html5lib
import sys
import time
import datetime
from bs4 import BeautifulSoup
from enum import Enum

from ManagerHeader import *
from ManagerHeader import url_manager as urls

#class ConnectionError(Exception):
#    def __init__(self, message='', error_code=''):
#        err_msg = '%s \nstatus code: %d' % (message, error_code)
#        super(ConnectionError, self).__init__(err_msg)

#class ConnectionManager(requests.Session):
#    '''
#    Wrapper class of requests.Session with extra error checking
#    '''
#    def get(self, url, **kwargs):
#        response = super(ConnectionManager, self).get(url, **kwargs)
#        if response.status_code != 200:
#            raise ConnectionError('Get connection to %s failed' % (url), response.status_code)
#        return response

#    def post(self, url, data = None, json = None, **kwargs):
#        response = super(ConnectionManager, self).post(url, data, json, **kwargs)
#        if response.status_code != 200:
#            raise ConnectionError('Post connection to %s failed' %(url), response.status_code)
#        return response

#class UrlManager:
#    base_url = 'https://compass-ssb.tamu.edu'
#    login_url = 'https://compass-sso.tamu.edu:443/ssomanager/c/SSB?pkg=bwykfcls.p_sel_crse_search'
#    referer_url = 'https://cas.tamu.edu/cas/login?service=https%3A%2F%2Fcompass-sso.tamu.edu%3A443%2Fssomanager%2Fc%2FSSB%3Bjsessionid%3DrnCyUwU8GZI6Z4N_I-f6g5B6wx65qnJgrtMABFKdE-uyZdwN4E52%21-280416030%3Fpkg%3Dbwykfcls.p_sel_crse_search'
#    term_url = None

#urlManager = UrlManager()
#session = ConnectionManager()   # global session used by other classes

class HowdyCompassConnector:
    def __init__(self):
        self.term_page = None
        self.subj_page = None
        self.course_page = None
        self.section_page = None 
        self.username = None
        self.password = None

    def login(self, username, password):
        self.username = username
        self.password = password

        login_page = session.get(urls.login_url)
        
        self.csrftoken = login_page.cookies['csrftoken']
        soup = BeautifulSoup(login_page.text, 'html.parser')
        tag = soup.find('input', {'name':'lt'})
        lt_value = tag.attrs['value']
        payload = dict(csrfmiddlewaretoken=self.csrftoken, username=username, 
                       password=password, lt=lt_value, _eventId='submit')
        self.term_page = session.post(login_page.url, headers={'Referer': urls.referer_url}, data=payload)
        urls.term_url = self.term_page.url
        print 'Login successful'

        ## get url of subj selection page
        urls.subj_url = urls.base_url
        term_page_soup = BeautifulSoup(self.term_page.text, 'html.parser')
        for tag in term_page_soup.findAll('form'):
            r = tag.get('onsubmit')
            if r != None:
                urls.subj_url += tag.get('action')

    def direct_term_page(self):
        if term_page is None:
            raise Exception('Please login first!')
        return self.term_page

    def direct_subj_page(self, semester_id=None):
        if semester_id is None and self.subj_page is not None:
            return self.subj_page
        elif semester_id is not None:
            term_form = dict(p_calling_proc='P_CrseSearch', p_term=semester_id)
            self.subj_page = session.post(urls.subj_url, data=term_form)
            return self.subj_page
        else:
            raise ValueError('Semester not specified on first use!')

    def direct_course_page(self, subj_name=None):
        if subj_name is None and self.course_page is not None:
            return self.course_page
        elif subj_name is not None:
            pass
        else:
            raise ValueError('Subject name not specified on first use!')

    def direct_section_page(self, course):
        '''
        @course: Course
        '''
        cf = course.get_course_form()
        self.section_page = session.post(urls.subj_url, headers={'Referer':subj_url}, data=cf)

        return self.section_page

howdy_connector = HowdyCompassConnector()

class Course:
    def __init__(self, subj_name, course_id, section_id, semester_id, crn):
        self.semester_id = semester_id
        self.subj_name = subj_name
        self.course_id = course_id
        self.section_id = section_id
        self.crn = crn

    def __repr__(self):
        return "Course('{}', '{}', '{}', '{}', '{}')".format(
            self.subj_name, self.course_id, self.section_id, self.semester_id, self.crn)

    def __str__(self):
        return '{} {}-{} CRN: {}'.format(self.subj_name, self.course_id,
                                         self.section_id, self.crn)
    def get_course_form(self):
        return {
            'term_in':self.semester_id,
            'sel_subj': ['dummy', self.subj_name],
            'SEL_CRSE': self.course_id,
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
            'SEL_ATTR':['dummy', '%'],
            'SEL_LEVL':['dummy', '%'],
            'SEL_INSM':'dummy',
            'sel_dunt_code':'',
            'sel_dunt_unit':'',
            'call_value_in':'BASIC',
            'rsts':'dummy',
            'crn':'dummy',
            'path':'1',
            'SUB_BTN':'View Sections'
        }
    def get_register_form(self):
        return dict(TERM_IN=self.semester_id, sel_crn=['dummy', self.crn + ' ' + self.semester_id], 
                    assoc_term_in=['dummy', self.semester_id], ADD_BTN=['dummy', 'Register'])

class CourseInfoExtractor:
    course_url = 'https://compass-ssb.tamu.edu/pls/PROD/bwykgens.p_proc_term_date?deviceType=C'

    def download_course_info(self, course_per_request=-1, delay = 2):
        '''
        @course_per_reqeust: int
            defines number of courses in each request
        @delay: int
            time to wait in between each request (in seconds)
        '''
        

class CourseRegister:
    register_url = 'https://compass-ssb.tamu.edu/pls/PROD/bwykfreg.P_AltPin1?deviceType=C'

    def register(self, course):
        '''
        @course: Course
        '''
        course_form = course.get_course_form()
        #section_page = session.post(
        
        register_form = course.get_register_form()
        register_page = session.post(self.register_url, data=register_form)
            
    
class ClassWatchStatus:
    class StatusCode(Enum):
        open = 0
        unavailable = 1
        registered = 2

    def __init__(self, course):
        self.courseName = str(course)
        self.status = StatusCode.unavailable

    def __str__(self):
        return '{} - status: {}'.format(self.courseName, self.status.name)

class CourseWatcher:

    def __init__(self):
        self.courseList = dict()

    def printStatuslist(self):
        pass
    
    def printStatus(course):
        _, status = course 

    def placeWatchOn(self, courses):
        '''
        @courses: [Course]
            list of Course
        '''
        for course in courses:
            if (self.courseList.has_key(course)): continue
            section_page = howdy_connector.direct_section_page(course)
            self.courseList[course] = (section_page, 



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
        'SEL_ATTR':['dummy', '%'],
        'SEL_LEVL':['dummy', '%'],
        'SEL_INSM':'dummy',
        'sel_dunt_code':'',
        'sel_dunt_unit':'',
        'call_value_in':'BASIC',
        'rsts':'dummy',
        'crn':'dummy',
        'path':'1',
        'SUB_BTN':'View Sections'
    }



def main():
    howdy_connector.login('yaoyuan0553', '0F9(20)-Yg*14')

    course_register = CourseRegister()

    course = Course('CSCE', '221', '501', '201631', '10933')

    course_register.register(course)


main()