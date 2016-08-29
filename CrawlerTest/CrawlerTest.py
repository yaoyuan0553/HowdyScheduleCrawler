import sys
import requests
from bs4 import BeautifulSoup

def howdy_spider():
    session = requests.Session()
    url = "https://howdy.tamu.edu"
    source_code = session.get(url)
    print source_code
    code_text = source_code.text
    bsoup = BeautifulSoup(code_text, 'html.parser')
    for tag_a in bsoup.findAll('a', {'class': 'btn-group btn btn-lg btn-aggie'}):
        href = tag_a.get('href')
        #print(href)     # href is the link
        cas_auth(session, href, source_code.cookies)
    session.close()

# function used for TAMU cas authentication
def cas_auth(session, url, cookies):
    payload = {'_eventId':'submit', 'username':'yaoyuan0553', 'password':'0F9(20)-Yg*14'}
    response = session.get(url, params=cookies)
    print 'Response from ' + url + ':', response
    page = BeautifulSoup(response.text, 'html.parser')
    tag = page.find('input', id='username')
    print tag
    post = session.post(url, data=payload, params=cookies)
    print post



def main():
    howdy_spider()


#main()