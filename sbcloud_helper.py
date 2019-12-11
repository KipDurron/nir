
import requests
import hashlib
import urllib.parse as urlparse
import json

HOSTNAME = 'sbcloud.ru'
USERNAME = 'ishunin97@gmail.com'

def sbcloud_req_res(login, password):
    session = requests.Session()
    password_hash = hashlib.sha512(str(password).encode('utf-8')).hexdigest()
    respons_auth = session.post('https://' + HOSTNAME + '/api/auth/login',
                                {'login': login, 'password': password_hash}, verify=False)
    return respons_auth

def get_headers_by_auth_resp(respons_auth):
    token_list = urlparse.parse_qs(urlparse.urlparse(respons_auth.text).query)['token']
    token_str = ''.join([str(elem) for elem in token_list])
    headers = {'X-Auth-Token': token_str}
    return headers

def sbcloud_create_project(name_project, headers):
    data = {"name": name_project}
    # json_data = json.dumps(data)
    session = requests.Session()
    response = session.post('https://' + HOSTNAME + '/api/projects', json=data, verify=False, headers=headers)
    return response
