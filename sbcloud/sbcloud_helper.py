
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

def sbcloud_create_server(server_conf, headers):
    session = requests.Session()
    return session.post('https://' + HOSTNAME + '/api/instance', json=server_conf, headers= headers, verify=False)

def get_pattern_disks(disks):
    disks = disks["storage_profiles"]
    result = '|'.join(map(lambda disk: str(disk['id']), disks))
    return result

def get_subnets_str(network):
    return "(" + ','.join(map(lambda subnet: subnet["cidr"], network["subnets"])) + ")"

def get_network_by_id(id, networks):
    for network in networks:
        if network['id'] == int(id):
            return network
    return []

def get_fixed_ips(network):
    result = []
    if len(network) != 0:
        for subnet in network["subnets"]:
            result.append({"subnet_id": subnet["id"]})
    return result


def test():
    data = json.loads('{"networks": [{"id": 433345, "name": "\u0421\u0435\u0442\u044c", "tenant_id": "433339", "status": "active", "has_internet": false, "is_default": false, "external": false, "shared": false, "ctime": "2019-12-14T18:41:07.680798+03:00", "atime": "2019-12-14T18:41:09.977734+03:00", "vlan_id": 1239, "subnets": [{"id": 433347, "name": "", "tenant_id": "433339", "cidr": "10.0.1.0/24", "ip_version": 4, "enable_dhcp": true, "gateway_ip": "10.0.1.1", "allocation_pools": [{"end": "10.0.1.254", "start": "10.0.1.2"}], "has_internet": false, "ips": [{"ip_address": "10.0.1.1", "port_id": 433351}], "ctime": "2019-12-14T18:41:09.900402+03:00", "atime": "2019-12-14T18:41:10.351668+03:00"}], "task_percent": 100.0, "task_state": null, "task_action": null}, {"id": 20006, "name": "external", "tenant_id": "admin", "status": "active", "has_internet": true, "is_default": false, "external": true, "shared": true, "ctime": "2019-03-03T18:59:25.893975+03:00", "atime": "2019-05-16T14:44:37.950295+03:00", "vlan_id": null, "subnets": [{"id": 20007, "name": "", "tenant_id": "admin", "cidr": "185.17.141.0/24", "ip_version": 4, "enable_dhcp": false, "gateway_ip": "185.17.141.1", "allocation_pools": [{"end": "185.17.141.254", "start": "185.17.141.2"}], "has_internet": false, "ips": [{"ip_address": "185.17.141.14", "port_id": 212126}, {"ip_address": "185.17.141.19", "port_id": 298318}, {"ip_address": "185.17.141.7", "port_id": 358494}, {"ip_address": "185.17.141.6", "port_id": 238119}, {"ip_address": "185.17.141.57", "port_id": 390855}, {"ip_address": "185.17.141.33", "port_id": 357731}, {"ip_address": "185.17.141.105", "port_id": 257538}, {"ip_address": "185.17.141.82", "port_id": 212806}, {"ip_address": "185.17.141.83", "port_id": 212825}, {"ip_address": "185.17.141.3", "port_id": 225208}, {"ip_address": "185.17.141.116", "port_id": 289132}, {"ip_address": "185.17.141.106", "port_id": 310150}, {"ip_address": "185.17.141.39", "port_id": 303125}, {"ip_address": "185.17.141.44", "port_id": 308211}, {"ip_address": "185.17.141.66", "port_id": 218907}, {"ip_address": "185.17.141.30", "port_id": 209051}, {"ip_address": "185.17.141.99", "port_id": 217285}, {"ip_address": "185.17.141.98", "port_id": 298629}, {"ip_address": "185.17.141.91", "port_id": 290358}, {"ip_address": "185.17.141.37", "port_id": 254248}, {"ip_address": "185.17.141.109", "port_id": 257724}, {"ip_address": "185.17.141.124", "port_id": 298974}, {"ip_address": "185.17.141.4", "port_id": 237138}, {"ip_address": "185.17.141.43", "port_id": 308556}, {"ip_address": "185.17.141.62", "port_id": 306530}, {"ip_address": "185.17.141.74", "port_id": 252547}, {"ip_address": "185.17.141.108", "port_id": 304289}, {"ip_address": "185.17.141.133", "port_id": 424061}, {"ip_address": "185.17.141.122", "port_id": 261772}, {"ip_address": "185.17.141.46", "port_id": 238951}, {"ip_address": "185.17.141.76", "port_id": 253573}, {"ip_address": "185.17.141.114", "port_id": 308752}, {"ip_address": "185.17.141.72", "port_id": 308707}, {"ip_address": "185.17.141.134", "port_id": 424139}, {"ip_address": "185.17.141.84", "port_id": 256568}, {"ip_address": "185.17.141.135", "port_id": 424170}, {"ip_address": "185.17.141.20", "port_id": 306744}, {"ip_address": "185.17.141.45", "port_id": 306763}, {"ip_address": "185.17.141.22", "port_id": 299754}, {"ip_address": "185.17.141.52", "port_id": 309172}, {"ip_address": "185.17.141.32", "port_id": 279920}, {"ip_address": "185.17.141.68", "port_id": 280149}, {"ip_address": "185.17.141.136", "port_id": 424199}, {"ip_address": "185.17.141.90", "port_id": 286718}, {"ip_address": "185.17.141.86", "port_id": 309495}, {"ip_address": "185.17.141.113", "port_id": 286984}, {"ip_address": "185.17.141.110", "port_id": 221252}, {"ip_address": "185.17.141.12", "port_id": 307186}, {"ip_address": "185.17.141.102", "port_id": 304003}, {"ip_address": "185.17.141.89", "port_id": 295132}, {"ip_address": "185.17.141.13", "port_id": 307330}, {"ip_address": "185.17.141.27", "port_id": 407316}, {"ip_address": "185.17.141.96", "port_id": 341017}, {"ip_address": "185.17.141.93", "port_id": 341472}, {"ip_address": "185.17.141.132", "port_id": 423949}, {"ip_address": "185.17.141.54", "port_id": 407771}], "ctime": "2019-03-03T18:59:26.303144+03:00", "atime": "2019-12-12T16:03:31.233916+03:00"}], "task_percent": 100.0, "task_state": null, "task_action": null}], "total": 2}')

    res = get_fixed_ips(data['networks'])

# test()

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

    all_networks = get_all_networks(headers)
    all_routers = get_all_routers(headers)
    all_os = get_all_os(headers)
    all_disk = get_all_disk(headers)
    buttons = [[]]
    text = 'Выберите тип диска'
    for disk in all_disk["storage_profiles"]:
        buttons[0].append(str(disk['name'])  +str(disk['id']))
    pattern = get_pattern_disks(all_disk)
    return resp_create_VDPC

# testCreateProject()