import exceptions
import requests
import html5lib
import sys
import time
import datetime
import threading
import getpass
import random
import os
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
        print "Logining in...\n"

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
        if (urls.term_url != self.term_page.url):
            print "Login failed. Incorrect login credentials"
            return False
        print 'Login successful\n'
        ## get url of subj selection page
        urls.subj_url = urls.base_url
        term_page_soup = BeautifulSoup(self.term_page.text, 'html.parser')
        for tag in term_page_soup.findAll('form'):
            r = tag.get('onsubmit')
            if r != None:
                urls.subj_url += tag.get('action')
        return True

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
            #if hasattr(urls, course_url) is False:
            #    soup = BeautifulSoup(self.subj_page)
            #    urls.course_url = urls.base_url
            #    for tag in soup.find_all('form'):
            #        if tag.has_attr('onsubmit'):
            #            urls.course_url += tag.__getattribute__('action')
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
        self.section_page = session.post(urls.course_url, headers={'Referer':urls.subj_url}, data=cf)

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
        

class CourseRegister(object):
    register_url = 'https://compass-ssb.tamu.edu/pls/PROD/bwykfreg.P_AltPin1?deviceType=C'
    
    __errormsg = None

    @classmethod
    def register(cls, course):
        '''
        @course: Course

        returns True if successfully registered course
        False otherwise

        use get_error_message() for detailed error report
        '''
        
        register_form = course.get_register_form()
        register_page = session.post(cls.register_url, data=register_form)
        register_page_soup = BeautifulSoup(register_page.text, 'html5lib')
        error_span = register_page_soup.find('span', class_='errortext')
        if error_span is not None:
            print "** Registration Failed **"
            print "The following is the failed reason\n"
            cls.__errormsg = register_page_soup.find(
                'table', {'class':'datadisplaytable', 'summary':'This layout table is used to present Registration Errors.'})
            print cls.__errormsg
            return False
        return True

    @classmethod
    def get_error_message(cls):
        if cls.__errormsg is not None:
            print cls.__errormsg

            
class StatusCode(Enum):
    open = 0
    unavailable = 1
    registration_error = 2
    registered = 3   

class CourseWatchStatus:

    def __init__(self, course, status=None):
        self.courseName = str(course)
        if status is None:
            self.status = StatusCode.unavailable
        else:
            self.status = status

    def __repr__(self):
        return "CourseWatchStatus('{}', {})".format(self.courseName, self.status)

    def __str__(self):
        return '{} - status: {}'.format(self.courseName, self.status.name)

class CourseWatcher:

    def __init__(self):
        self.courseList = dict()

    def printStatuslist(self):
        pass
    
    def printStatus(self, course):
        _, status = self.courseList[course]
        print status

    def placeWatchOn(self, courses):
        '''
        @courses: [Course]
            list of Course
        '''
        for course in courses:
            if (self.courseList.has_key(course)): continue
            section_page = howdy_connector.direct_section_page(course)
            self.courseList[course] = [section_page, CourseWatchStatus(course)]
            
    @staticmethod
    def notify(course_name):
        '''
        notify user that there is an open section
        @course_name: str
        '''
        print '%s is available' % (course_name)

    @staticmethod
    def ask_for_registration():
        pass

    def startWatch(self, time_interval=10, auto_register=False):
        '''
        @time_interval: int
            time in minutes to wait in between each refresh
        @auto_register: bool
            automatically register if course is open when value is True.
            Default to False 
        '''
        for course in self.courseList:
            page, _ = self.courseList[course]
            soup = BeautifulSoup(page.text, 'html5lib')
            table = soup.find('table', class_='datadisplaytable')
            for tr in table.find_all('tr'):
                if tr.has_attr('style'):
                    select_tdtag = tr.find_all('td')[0]
                    checkbox = soup.find('input', {'type':'checkbox'})
                    if checkbox is not None:
                        self.courseList[course][1].status = StatusCode.open
                        self.notify(str(course))   
                        if auto_register is True:   # attempt to register automatically
                            if CourseRegister.register(course) is False:    # registration failed
                                CourseRegister.get_error_message()
                                self.courseList[course][1].status = StatusCode.registration_error
                            else:   # registration successful
                                self.courseList[course][1].status = StatusCode.registered
                        else:   # ask user whether they want the course to be registered
                            pass
                        
def is_number(s):
    try:
        num = int(s)
        return True
    except ValueError:
        return False

def displayInfo():
    print "**************************************"
    print "* Welcome to course registerer v0.1! *"
    print "*                 - Made by Yuan Yao *"
    print "**************************************\n"
    print "Please input your howdy login info\n"


def main():
    displayInfo()

    # obtain user info to login
    username = raw_input("Username: ")
    password = getpass.getpass()
    is_success = howdy_connector.login(username, password)
    chances = 2
    while (is_success is False and chances != 0):
        print chances, "chances left\n"
        username = raw_input("Username: ")
        password = getpass.getpass()
        is_success = howdy_connector.login(username, password)
        chances -= 1

    #course_register = CourseRegister()

    # obtain course info 
    term = '201711'
    print "Please provide with correct info of the course. (Term is default to Spring 2017)"
    is_correct = False
    while (is_correct is False):
        c_name = raw_input('Course Name (i.e. CSCE): ')
        c_num = raw_input('Course Number (i.e 489): ')
        c_sec = raw_input('Course Section (i.e 501): ')
        crn = raw_input('Course CRN (i.e. 12452): ')

        print "\n%s %s-%s\nCRN: %s" % (c_name, c_num, c_sec, crn)
        
        c = raw_input('Please confirm if the above information are correct? (y/n) ')
        while (c != 'y' and c != 'n'):
            c = raw_input('Please confirm if the above information are correct? (y/n) ')

        is_correct = c == 'y'
    
    # obtain wait time info
    time_lower = 0
    time_upper = 0
    is_valid = False
    print "Please provide wait time in between 2 registration trials\nby providing in minutes a " + \
        "a lower bound time and an upper bound time. \nA random wait time will be generate between the range"
    print "In order to obey to crawler rule set by Howdy, the crawler has to wait at least 10 minutes before another request"
    while (True):
        time_lower = raw_input('Enter lower bound time: ')
        time_upper = raw_input('Enter upper bound time: ')
        if (is_number(time_lower) is False or is_number(time_upper) is False):
            print "Must be a number!\n"
            continue
        time_lower = float(time_lower)
        time_upper = float(time_upper)
        if (time_lower >= time_upper):
            print "Lower bound must not be greater than or equal to upper bound!\n"
            continue
        if (time_lower < 10):
            print "Lower bound must be greater than or equal to 10 minutes!\n"
            continue
        break
        
    #course = Course('CSCE', '481', '900', '201711', '17851')
    sec_lower = int(time_lower * 60)
    sec_upper = int(time_upper * 60)


    course = Course(c_name, c_num, c_sec, term, crn)

    # registering the course
    is_registered = False
    while (is_registered is False):
        is_registered = CourseRegister.register(course)
        wait_time = random.randint(sec_lower, sec_upper)
        if (is_registered == False):
            print "Retry in %d seconds" % (wait_time)
            time.sleep(wait_time)

    print "\n\n******** Registration successful! *********"

    os.system('pause')



if __name__ == "__main__":
    main()