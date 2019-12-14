
import requests
import hashlib
import urllib.parse as urlparse
import json
import time

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

def get_vdpc_tenant_id(response):
    data = json.loads(response.text)['task']['objects'][0]
    return "".join(filter(str.isdigit, data))

def sbcloud_create_network(headers):
    session = requests.Session()
    json_network = json.loads(
        '{"name":"Сеть","subnets":[{"enable_dhcp":true,"ip_version":4,"cidr":"10.0.1.0/24","gateway_ip":"10.0.1.1","allocation_pools":[{"start":"10.0.1.2","end":"10.0.1.254"}],"dns_nameservers":["8.8.8.8"]}]}')
    response = session.post('https://' + HOSTNAME + '/api/network', json=json_network, verify=False, headers=headers)
    resp_code = response.status_code
    while (resp_code == 409):
        time.sleep(2)
        response = session.post('https://' + HOSTNAME + '/api/network', json=json_network, verify=False, headers=headers)
        resp_code = response.status_code
    return response

def get_network_id(response):
    data = json.loads(response.text)['task']['objects'][0]
    return int("".join(filter(str.isdigit, data)))


def sbcloud_response_tenant(tenant_id, headers):
    session = requests.Session()
    return session.get('https://' + HOSTNAME + '/api/auth/service?tenant_id=' + str(tenant_id), verify=False, headers=headers)

def sbcloud_create_router(network_id, headers):
    session = requests.Session()
    router_data = {
        "name": "Роутер",
        "shaping_policy":{
            "enabled": True,
            "bandwidth": 10
        },
        "interfaces": [{
            "network_id": network_id
        }],
        "external_gateway_info" : {
            "internet" : True,
            "enable_snat" : True
        }
    }
    res_exist_network = session.get('https://' + HOSTNAME + '/api/network?network_id=' + str(network_id), headers=headers, verify=False)
    status_network = get_status_create_network(res_exist_network)
    # проверяем что сеть создана
    while status_network != 'active':
        time.sleep(2)
        status_network = get_status_create_network(session.get('https://' + HOSTNAME + '/api/network?network_id=' + str(network_id), headers=headers, verify=False))

    # создаём роутер
    response = session.post('https://' + HOSTNAME + '/api/router', json=router_data, headers= headers, verify=False)
    resp_code = response.status_code
    while (resp_code == 409):
        response = session.post('https://' + HOSTNAME + '/api/router', json=router_data, headers= headers, verify=False)
        resp_code = response.status_code
    return response

def get_status_create_network(respons):
    return json.loads(respons.text)["networks"][0]['status']

def get_all_networks(headers):
    session = requests.Session()
    response = session.get('https://' + HOSTNAME + '/api/network', headers=headers, verify=False)
    return json.loads(response.text)

def get_all_routers(headers):
    session = requests.Session()
    response = session.get('https://' + HOSTNAME + '/api/router', headers=headers, verify=False)
    return json.loads(response.text)

def get_all_os(headers):
    session = requests.Session()
    response = session.get('https://' + HOSTNAME + '/api/products?sort=name', headers=headers, verify=False)
    return json.loads(response.text)

def get_all_disk(headers):
    session = requests.Session()
    response = session.get('https://' + HOSTNAME + '/api/storage_profile?enabled=true', headers=headers, verify=False)
    return json.loads(response.text)

def testCreateProject():
    session = requests.Session()
    headers = get_headers_by_auth_resp(sbcloud_req_res('ishunin97@gmail.com', '8921414go'))
    resp_create_prog = sbcloud_create_project("47", headers)
    data_VDPC = {
        'hypervisor_id': 'vsphere',
        'create_immediately': True,
        'name': 'vsphere VDC for project' + str(get_field_from_response_project(resp_create_prog, 'id')),
        'project_id': get_field_from_response_project(resp_create_prog, 'id'),
        'contract_id': get_contract_id(headers),
        'org_id': str(get_field_from_response_project(resp_create_prog, 'org_id')),
        'plan_id': get_plan_id(headers, get_contract_id(headers)),
        'rts_status': "pending",
        'rts_type': "vdc"
    }
    resp_create_VDPC = sbcloud_create_vdpc(data_VDPC,headers)
    tenant_id = get_vdpc_tenant_id(resp_create_VDPC)
    response_tenant = sbcloud_response_tenant(tenant_id, headers)
    response_network = sbcloud_create_network(headers)
    response_tenant = sbcloud_response_tenant(tenant_id, headers)
    resp_router = sbcloud_create_router(get_network_id(response_network), headers)

    return resp_create_VDPC

# testCreateProject()