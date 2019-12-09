
import requests
import hashlib
import urllib.parse as urlparse

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


# def create_project():
#     headers = sbcloud_req_res()
#     session = requests.Session()
#     json = "{\"name\":\"azazazazazazaza\",\"folder\":\"string\",\"pool\":\"string\",\"cluster\":\"string\",\"datastore\":\"string\",\"drs_groups\":[\"string\"],\"configuration\":{\"cpu\":0,\"cores_per_socket\":0,\"memory\":0,\"disks\":[{\"profile_id\":0,\"size\":0,\"id\":0,\"cluster_disk_id\":0,\"iops_limit\":0}],\"bandwidth\":0,\"networks\":[{\"network_id\":\"string\",\"fixed_ips\":[{\"subnet_id\":\"string\",\"ip_address\":\"127.0.0.1\"}],\"mac_address\":\"\\\"01-23-45-67-89-ab\",\"auto_floating\":false,\"floating_ip_address\":\"127.0.0.1\",\"port_id\":0}]},\"flavor_id\":\"string\",\"instance_id\":0,\"snapshot_id\":0,\"datacenter_id\":0,\"os_id\":\"string\",\"software\":[\"string\"],\"license_id\":0,\"is_vmtemplate\":false,\"launch_index\":0,\"hostname\":\"example.com\",\"password\":\"string\",\"instance_fw_rules\":{\"name\":\"string\",\"description\":\"string\",\"shared\":true,\"rules\":[{\"name\":\"string\",\"description\":\"string\",\"direction\":\"ingress\",\"protocol\":\"tcp\",\"start_port\":0,\"end_port\":0,\"ip_version\":4,\"remote_cidr\":\"127.0.0.1\",\"shared\":true,\"action\":\"allow\"}],\"templates_ids\":[0]},\"metadata\":{},\"metadata_unique\":{},\"backup_options\":{},\"monitoring\":{},\"security_groups\":[0]}"
#     respons_auth = session.post('https://' + HOSTNAME + '/api/instance', json=json, verify=False, headers=headers)
# create_project()
