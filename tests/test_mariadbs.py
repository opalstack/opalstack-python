import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def mariauser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def mariadb_mariauser(mariauser_server):
    created_mariausers = opalapi.mariausers.create([
        {'server': mariauser_server['id'], 'name': f'test-mariauser-{RANDID}', 'external': False},
    ])
    mariauser = created_mariausers[0]
    yield mariauser
    opalapi.mariausers.delete([
        {'id': mariauser['id']},
    ])

def test_mariadbs(mariadb_mariauser):
    mariadb_mariauser_id = mariadb_mariauser['id']
    mariadb_mariauser_name = mariadb_mariauser['name']
    mariadb_mariauser_server_id = mariadb_mariauser['server']

    # -- Create mariadbs --
    #
    # Create new mariadbs.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_mariadbs = opalapi.mariadbs.create([
        { 'name': f'test-mariadb-{RANDID}',
          'server': mariadb_mariauser_server_id,
          'dbusers_readwrite': [mariadb_mariauser_id],
        },
    ])
    created_mariadb = created_mariadbs[0]
    created_mariadb_id = created_mariadb['id']
    created_mariadb_name = created_mariadb['name']
    print(f'Created mariadb {created_mariadb_name} with access from {mariadb_mariauser_name}')

    assert created_mariadb['name'] == f'test-mariadb-{RANDID}'
    assert created_mariadb['server'] == mariadb_mariauser_server_id
    assert created_mariadb['dbusers_readwrite'] == [mariadb_mariauser_id]

    # -- List mariadbs --
    #
    # Retrieve all existing mariadbs.
    #
    for mariadb in opalapi.mariadbs.list_all():
        mariadb_id = mariadb['id']
        mariadb_name = mariadb['name']
        this_mariadb_mariauser_ids = mariadb['dbusers_readwrite']
        print(f'Listed mariadb {mariadb_id} (name: {mariadb_name})')

    # Use embed to include more information about the mariausers.
    #   Without the embed, mariadb['dbusers_readwrite'] would contain a uuid list.
    #   By adding embed=['dbusers_readwrite'], it contains a dict list instead.
    for mariadb in opalapi.mariadbs.list_all(embed=['dbusers_readwrite']):
        mariadb_id = mariadb['id']
        mariadb_name = mariadb['name']
        this_mariadb_mariauser_ids = [mariauser['id'] for mariauser in mariadb['dbusers_readwrite']]
        this_mariadb_mariauser_names = [mariauser['name'] for mariauser in mariadb['dbusers_readwrite']]
        this_mariadb_mariauser_name = this_mariadb_mariauser_names[0]
        print(f'Listed mariadb {mariadb_name} with access from {this_mariadb_mariauser_name}')

    # -- Read single mariadb --
    #
    # Retrieve one existing mariadb by id.
    #
    mariadb = opalapi.mariadbs.read(mariadb_id)
    print(f'Read mariadb by id: {mariadb_id}')

    assert mariadb['id'] == mariadb_id

    # -- Update mariadbs --
    #
    # Change the access for existing mariadbs.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_mariadbs = opalapi.mariadbs.update([
        { 'id': created_mariadb_id,
          'dbusers_readwrite': [],
          'dbusers_readonly': [mariadb_mariauser_id],
        },
    ])
    updated_mariadb = updated_mariadbs[0]
    print(f'Updated mariadb access')

    assert updated_mariadb['id'] == created_mariadb_id
    assert updated_mariadb['dbusers_readwrite'] == []
    assert updated_mariadb['dbusers_readonly'] == [mariadb_mariauser_id]

    # -- Delete mariadbs --
    #
    # Delete existing mariadbs by id.
    # Takes a list of items to delete.
    #
    opalapi.mariadbs.delete([
        {'id': created_mariadb_id},
    ])
    print(f'Deleted mariadb with id {created_mariadb_id}')

    assert not any(mariadb['id'] == created_mariadb_id for mariadb in opalapi.mariadbs.list_all())
