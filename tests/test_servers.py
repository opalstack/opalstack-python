from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

def test_servers():
    # -- List servers --
    #
    # Retrieve all existing servers on the account.
    # Returns three lists: web_servers, imap_servers, and smtp_servers
    #
    servers = opalapi.servers.list_all()

    web_servers = servers['web_servers']
    imap_servers = servers['imap_servers']
    smtp_servers = servers['smtp_servers']

    for web_server in web_servers:
        server_id = web_server['id']
        server_hostname = web_server['hostname']
        print(f'Listed web_server {server_hostname}')

    for imap_server in imap_servers:
        server_id = imap_server['id']
        server_hostname = imap_server['hostname']
        print(f'Listed imap_server {server_hostname}')

    for smtp_server in smtp_servers:
        server_id = smtp_server['id']
        server_hostname = smtp_server['hostname']
        print(f'Listed smtp_server {server_hostname}')

    # -- Read single server --
    #
    # Retrieve one existing server by id.
    #
    server = opalapi.servers.read(server_id)
    print(f'Read server by id: {server_id}')

    assert server['id'] == server_id
