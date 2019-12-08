
import requests
import hashlib
import urllib.parse as urlparse


def sbcloud_req_res():
    session = requests.Session()
    username = 'ishunin97@gmail.com'
    password_hash = hashlib.sha512('8921414go'.encode('utf-8')).hexdigest()
    hostname = 'sbcloud.ru'
    respons_auth = session.post('https://' + hostname + '/api/auth/login',
                                {'login': username, 'password': password_hash}, verify=False)
    token_list = urlparse.parse_qs(urlparse.urlparse(respons_auth.text).query)['token']
    token_str = ''.join([str(elem) for elem in token_list])
    headers = {'X-Auth-Token': token_str}
    response = session.get('https://' + hostname + '/api/projects/', headers=headers)
    return response


