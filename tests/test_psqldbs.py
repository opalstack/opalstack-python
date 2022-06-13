import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def psqluser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def psqldb_psqluser(psqluser_server):
    created_psqlusers = opalapi.psqlusers.create([
        {'server': psqluser_server['id'], 'name': f'test-psqluser-{RANDID}', 'external': False},
    ])
    psqluser = created_psqlusers[0]
    yield psqluser
    opalapi.psqlusers.delete([
        {'id': psqluser['id']},
    ])

def test_psqldbs(psqldb_psqluser):
    psqldb_psqluser_id = psqldb_psqluser['id']
    psqldb_psqluser_name = psqldb_psqluser['name']
    psqldb_psqluser_server_id = psqldb_psqluser['server']

    # -- Create psqldbs --
    #
    # Create new psqldbs.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_psqldbs = opalapi.psqldbs.create([
        { 'name': f'test-psqldb-{RANDID}',
          'server': psqldb_psqluser_server_id,
          'dbusers_readwrite': [psqldb_psqluser_id],
        },
    ])
    created_psqldb = created_psqldbs[0]
    created_psqldb_id = created_psqldb['id']
    created_psqldb_name = created_psqldb['name']
    print(f'Created psqldb {created_psqldb_name} with access from {psqldb_psqluser_name}')

    assert created_psqldb['name'] == f'test-psqldb-{RANDID}'
    assert created_psqldb['server'] == psqldb_psqluser_server_id
    assert created_psqldb['dbusers_readwrite'] == [psqldb_psqluser_id]

    # -- List psqldbs --
    #
    # Retrieve all existing psqldbs.
    #
    for psqldb in opalapi.psqldbs.list_all():
        psqldb_id = psqldb['id']
        psqldb_name = psqldb['name']
        this_psqldb_psqluser_ids = psqldb['dbusers_readwrite']
        print(f'Listed psqldb {psqldb_id} (name: {psqldb_name})')

    # Use embed to include more information about the psqlusers.
    #   Without the embed, psqldb['dbusers_readwrite'] would contain a uuid list.
    #   By adding embed=['dbusers_readwrite'], it contains a dict list instead.
    for psqldb in opalapi.psqldbs.list_all(embed=['dbusers_readwrite']):
        psqldb_id = psqldb['id']
        psqldb_name = psqldb['name']
        this_psqldb_psqluser_ids = [psqluser['id'] for psqluser in psqldb['dbusers_readwrite']]
        this_psqldb_psqluser_names = [psqluser['name'] for psqluser in psqldb['dbusers_readwrite']]
        this_psqldb_psqluser_name = this_psqldb_psqluser_names[0]
        print(f'Listed psqldb {psqldb_name} with access from {this_psqldb_psqluser_name}')

    # -- Read single psqldb --
    #
    # Retrieve one existing psqldb by id.
    #
    psqldb = opalapi.psqldbs.read(psqldb_id)
    print(f'Read psqldb by id: {psqldb_id}')

    assert psqldb['id'] == psqldb_id

    # -- Update psqldbs --
    #
    # Change the access for existing psqldbs.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_psqldbs = opalapi.psqldbs.update([
        { 'id': created_psqldb_id,
          'dbusers_readwrite': [],
          'dbusers_readonly': [psqldb_psqluser_id],
        },
    ])
    updated_psqldb = updated_psqldbs[0]
    print(f'Updated psqldb access')

    assert updated_psqldb['id'] == created_psqldb_id
    assert updated_psqldb['dbusers_readwrite'] == []
    assert updated_psqldb['dbusers_readonly'] == [psqldb_psqluser_id]

    # -- Delete psqldbs --
    #
    # Delete existing psqldbs by id.
    # Takes a list of items to delete.
    #
    opalapi.psqldbs.delete([
        {'id': created_psqldb_id},
    ])
    print(f'Deleted psqldb with id {created_psqldb_id}')

    assert not any(psqldb['id'] == created_psqldb_id for psqldb in opalapi.psqldbs.list_all())
