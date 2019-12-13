
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

def get_field_from_response_project(respons, field_name):
    return json.loads(respons.text)['project'][field_name]

def get_contract_id(headers):
    session = requests.Session()
    return json.loads(session
        .get('https://' + HOSTNAME + '/api/cloud/organization', verify=False, headers=headers).text)['organizations'][0]['contracts'][0]['id']

def get_plan_id(headers, contract_id):
    session = requests.Session()
    plan_id = json.loads(session.get('https://' + HOSTNAME + '/api/billing/plans?contract_id=' + str(contract_id), headers=headers,
                           verify=False).text)['plans'][0]['id']
    return plan_id

def sbcloud_create_vdpc(vdpc, headers):
    session = requests.Session()
    data = vdpc
    response = session.post('https://' + HOSTNAME + '/api/cloud/projects', json=data, verify=False, headers=headers)
    return response

def test():
    session = requests.Session()
    headers = get_headers_by_auth_resp(sbcloud_req_res('ishunin97@gmail.com', '8921414go'))
    data = {
        'hypervisor_id': 'vsphere',
        'create_immediately': True,
        'name': 'vsphere VDC for project 307928',
        'project_id': 307928
    }
    # response = session.post('https://' + HOSTNAME + '/api/cloud/projects', json=data, verify=False, headers=headers)
    # response = session.get('https://' + HOSTNAME + '/api/billing/plans?contract_id=307926', headers= headers, verify=False, )
    # contract_id = get_contract_id(headers)
    # response = get_plan_id(headers, contract_id)
    # return response

test()