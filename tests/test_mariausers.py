import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def mariauser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

def test_mariausers(mariauser_server):
    mariauser_server_id = mariauser_server['id']
    mariauser_server_hostname = mariauser_server['hostname']

    # -- Create mariausers --
    #
    # Create new mariausers.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_mariausers = opalapi.mariausers.create([
        { 'name': f'test-mariauser-{RANDID}',
          'server': mariauser_server_id,
          'external': False,
        },
    ])
    created_mariauser = created_mariausers[0]
    created_mariauser_id = created_mariauser['id']
    created_mariauser_name = created_mariauser['name']
    print(f'Created mariauser {created_mariauser_name} on server {mariauser_server_hostname}')

    assert created_mariauser['name'] == f'test-mariauser-{RANDID}'
    assert created_mariauser['server'] == mariauser_server_id

    # -- List mariausers --
    #
    # Retrieve all existing mariausers.
    #
    for mariauser in opalapi.mariausers.list_all():
        mariauser_id = mariauser['id']
        mariauser_name = mariauser['name']
        this_mariauser_server_id = mariauser['server']
        print(f'Listed mariauser {mariauser_id} (name: {mariauser_name})')

    # Use embed to include more information about the server.
    #   Without the embed, mariauser['server'] would contain a uuid.
    #   By adding embed=['server'], it contains a dict instead.
    for mariauser in opalapi.mariausers.list_all(embed=['server']):
        mariauser_id = mariauser['id']
        mariauser_name = mariauser['name']
        this_mariauser_server_id = mariauser['server']['id']
        this_mariauser_server_hostname = mariauser['server']['hostname']
        print(f'Listed mariauser {mariauser_name} on {this_mariauser_server_hostname}')

    # -- Read single mariauser --
    #
    # Retrieve one existing mariauser by id.
    #
    mariauser = opalapi.mariausers.read(mariauser_id)
    print(f'Read mariauser by id: {mariauser_id}')

    assert mariauser['id'] == mariauser_id

    # -- Update mariausers --
    #
    # Change the password of existing mariausers.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_mariausers = opalapi.mariausers.update([
        {'id': created_mariauser_id, 'password': ''.join(random.choices(string.ascii_lowercase, k=32))},
    ])
    updated_mariauser = updated_mariausers[0]
    print(f'Updated mariauser password')

    assert updated_mariauser['id'] == created_mariauser_id

    # -- Delete mariausers --
    #
    # Delete existing mariausers by id.
    # Takes a list of items to delete.
    #
    opalapi.mariausers.delete([
        {'id': created_mariauser_id},
    ])
    print(f'Deleted mariauser with id {created_mariauser_id}')

    assert not any(mariauser['id'] == created_mariauser_id for mariauser in opalapi.mariausers.list_all())
