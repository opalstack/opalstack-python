import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def psqluser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

def test_psqlusers(psqluser_server):
    psqluser_server_id = psqluser_server['id']
    psqluser_server_hostname = psqluser_server['hostname']

    # -- Create psqlusers --
    #
    # Create new psqlusers.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_psqlusers = opalapi.psqlusers.create([
        { 'name': f'test-psqluser-{RANDID}',
          'server': psqluser_server_id,
          'external': False,
        },
    ])
    created_psqluser = created_psqlusers[0]
    created_psqluser_id = created_psqluser['id']
    created_psqluser_name = created_psqluser['name']
    print(f'Created psqluser {created_psqluser_name} on server {psqluser_server_hostname}')

    assert created_psqluser['name'] == f'test-psqluser-{RANDID}'
    assert created_psqluser['server'] == psqluser_server_id

    # -- List psqlusers --
    #
    # Retrieve all existing psqlusers.
    #
    for psqluser in opalapi.psqlusers.list_all():
        psqluser_id = psqluser['id']
        psqluser_name = psqluser['name']
        this_psqluser_server_id = psqluser['server']
        print(f'Listed psqluser {psqluser_id} (name: {psqluser_name})')

    # Use embed to include more information about the server.
    #   Without the embed, psqluser['server'] would contain a uuid.
    #   By adding embed=['server'], it contains a dict instead.
    for psqluser in opalapi.psqlusers.list_all(embed=['server']):
        psqluser_id = psqluser['id']
        psqluser_name = psqluser['name']
        this_psqluser_server_id = psqluser['server']['id']
        this_psqluser_server_hostname = psqluser['server']['hostname']
        print(f'Listed psqluser {psqluser_name} on {this_psqluser_server_hostname}')

    # -- Read single psqluser --
    #
    # Retrieve one existing psqluser by id.
    #
    psqluser = opalapi.psqlusers.read(psqluser_id)
    print(f'Read psqluser by id: {psqluser_id}')

    assert psqluser['id'] == psqluser_id

    # -- Update psqlusers --
    #
    # Change the password of existing psqlusers.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_psqlusers = opalapi.psqlusers.update([
        {'id': created_psqluser_id, 'password': ''.join(random.choices(string.ascii_lowercase, k=32))},
    ])
    updated_psqluser = updated_psqlusers[0]
    print(f'Updated psqluser password')

    assert updated_psqluser['id'] == created_psqluser_id

    # -- Delete psqlusers --
    #
    # Delete existing psqlusers by id.
    # Takes a list of items to delete.
    #
    opalapi.psqlusers.delete([
        {'id': created_psqluser_id},
    ])
    print(f'Deleted psqluser with id {created_psqluser_id}')

    assert not any(psqluser['id'] == created_psqluser_id for psqluser in opalapi.psqlusers.list_all())
