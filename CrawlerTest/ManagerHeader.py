import requests

class ConnectionError(Exception):
    def __init__(self, message='', error_code=''):
        err_msg = '%s \nstatus code: %d' % (message, error_code)
        super(ConnectionError, self).__init__(err_msg)

class ConnectionManager(requests.Session):
    '''
    Wrapper class of requests.Session with extra error checking
    '''
    def get(self, url, **kwargs):
        response = super(ConnectionManager, self).get(url, **kwargs)
        if response.status_code != 200:
            raise ConnectionError('Get connection to %s failed' % (url), response.status_code)
        return response

    def post(self, url, data = None, json = None, **kwargs):
        response = super(ConnectionManager, self).post(url, data, json, **kwargs)
        if response.status_code != 200:
            raise ConnectionError('Post connection to %s failed' %(url), response.status_code)
        return response

class UrlManager:
    base_url = 'https://compass-ssb.tamu.edu'
    login_url = 'https://compass-sso.tamu.edu:443/ssomanager/c/SSB?pkg=bwykfcls.p_sel_crse_search'
    referer_url = 'https://cas.tamu.edu/cas/login?service=https%3A%2F%2Fcompass-sso.tamu.edu%3A443%2Fssomanager%2Fc%2FSSB%3Bjsessionid%3DrnCyUwU8GZI6Z4N_I-f6g5B6wx65qnJgrtMABFKdE-uyZdwN4E52%21-280416030%3Fpkg%3Dbwykfcls.p_sel_crse_search'


url_manager = UrlManager()
session = ConnectionManager()   # global session used by other classes