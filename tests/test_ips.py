from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

def test_ips():
    # -- List ips --
    #
    # Retrieve all webserver ips on the account.
    #
    for ip in opalapi.ips.list_all():
        ip_id = ip['id']
        ip_address = ip['ip']
        ip_type = ip['type']
        is_primary = ip['primary']
        server_id = ip['server']
        print(f'Listed ip (type IPv{ip_type}, primary={is_primary}, server_id={server_id}): {ip_address}')

    # Use embed to include more information about server.
    #   Without the embed, ip['server'] would contain a uuid.
    #   By adding embed=['server'], it contains a dict instead.
    for ip in opalapi.ips.list_all(embed=['server']):
        ip_id = ip['id']
        ip_address = ip['ip']
        ip_type = ip['type']
        is_primary = ip['primary']
        server_id = ip['server']['id']
        server_hostname = ip['server']['hostname']
        print(f'Listed ip (type IPv{ip_type}, primary={is_primary}): {ip_address} on server {server_hostname}')

    # -- Read single ip --
    #
    # Retrieve one existing ip by id.
    #
    ip = opalapi.ips.read(ip_id)
    print(f'Read ip by id: {ip_id}')

    assert ip['id'] == ip_id
