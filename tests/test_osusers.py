import string
import random

import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def osuser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

def test_osusers(osuser_server):
    osuser_server_id = osuser_server['id']
    osuser_server_hostname = osuser_server['hostname']

    # -- Create osusers --
    #
    # Create new osusers.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_osusers = opalapi.osusers.create([
        {'server': osuser_server_id, 'name': f'test-osuser-{RANDID}'},
    ])
    created_osuser = created_osusers[0]
    created_osuser_id = created_osuser['id']
    created_osuser_name = created_osuser['name']
    print(f'Created osuser {created_osuser_name} on server {osuser_server_hostname}')

    assert created_osuser['name'] == f'test-osuser-{RANDID}'
    assert created_osuser['server'] == osuser_server_id

    # -- List osusers --
    #
    # Retrieve all existing osusers.
    #
    for osuser in opalapi.osusers.list_all():
        osuser_id = osuser['id']
        osuser_name = osuser['name']
        osuser_server_id = osuser['server']
        print(f'Listed osuser {osuser_name}')

    # Use embed to include more information about the domain.
    #   Without the embed, osuser['server'] would contain a uuid.
    #   By adding embed=['server'], it contains a dict instead.
    for osuser in opalapi.osusers.list_all(embed=['server']):
        osuser_id = osuser['id']
        osuser_name = osuser['name']
        osuser_server_id = osuser['server']['id']
        osuser_server_hostname = osuser['server']['hostname']
        print(f'Listed osuser {osuser_name} on {osuser_server_hostname}')

    # -- Read single osuser --
    #
    # Retrieve one existing osuser by id.
    #
    osuser = opalapi.osusers.read(osuser_id)
    print(f'Read osuser by id: {osuser_id}')

    assert osuser['id'] == osuser_id

    # -- Update osusers --
    #
    # Change the password of existing osusers.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_osusers = opalapi.osusers.update([
        {'id': created_osuser_id, 'password': ''.join(random.choices(string.ascii_lowercase, k=32))},
    ])
    updated_osuser = updated_osusers[0]
    print(f'Updated osuser password')

    assert updated_osuser['id'] == created_osuser_id

    # -- Delete osusers --
    #
    # Delete existing osusers by id.
    # Takes a list of items to delete.
    #
    opalapi.osusers.delete([
        {'id': created_osuser_id},
    ])
    print(f'Deleted osuser with id {created_osuser_id}')

    assert not any(osuser['id'] == created_osuser_id for osuser in opalapi.osusers.list_all())
