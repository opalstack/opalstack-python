import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def osuser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def osvar_osuser(osuser_server):
    created_osusers = opalapi.osusers.create([
        {'server': osuser_server['id'], 'name': f'test-osuser-{RANDID}'},
    ])
    osuser = created_osusers[0]
    yield osuser
    opalapi.osusers.delete([
        {'id': osuser['id']},
    ])

def test_osvars(osvar_osuser):
    osvar_osuser_id = osvar_osuser['id']
    osvar_osuser_name = osvar_osuser['name']

    # -- Create osvars --
    #
    # Create new osvars.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_osvars = opalapi.osvars.create([
        { 'name': f'test-osvar-{RANDID}',
          'content': 'This is a test osvar value',
          'osusers': [osvar_osuser_id],
          'global': False,
        },
    ])
    created_osvar = created_osvars[0]
    created_osvar_id = created_osvar['id']
    created_osvar_name = created_osvar['name']
    created_osvar_content = created_osvar['content']
    print(f'Created osvar {created_osvar_name} under osuser {osvar_osuser_name} with content "{created_osvar_content}"')

    assert created_osvar['name'] == f'test-osvar-{RANDID}'
    assert created_osvar['content'] == 'This is a test osvar value'
    assert created_osvar['osusers'] == [osvar_osuser_id]

    # -- List osvars --
    #
    # Retrieve all existing osvars.
    #
    for osvar in opalapi.osvars.list_all():
        osvar_id = osvar['id']
        osvar_name = osvar['name']
        osvar_osuser_ids = osvar['osusers']
        print(f'Listed osvar {osvar_id} (osusers: {osvar_osuser_ids})')

    # Use embed to include more information about the osusers.
    #   Without the embed, osvar['osusers'] would contain a uuid list.
    #   By adding embed=['osusers'], it contains a dict list instead.
    for osvar in opalapi.osvars.list_all(embed=['osusers']):
        osvar_id = osvar['id']
        osvar_name = osvar['name']
        osvar_osuser_ids = [osuser['id'] for osuser in osvar['osusers']]
        osvar_osuser_names = [osuser['name'] for osuser in osvar['osusers']]
        osvar_osuser_name = osvar_osuser_names[0]
        print(f'Listed osvar {osvar_name} under {osvar_osuser_name}')

    # -- Read single osvar --
    #
    # Retrieve one existing osvar by id.
    #
    osvar = opalapi.osvars.read(osvar_id)
    print(f'Read osvar by id: {osvar_id}')

    assert osvar['id'] == osvar_id

    # -- Update osvars --
    #
    # Change the osusers or content of existing osvars.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_osvars = opalapi.osvars.update([
        {'id': created_osvar_id, 'content': 'This is another test osvar value'},
    ])
    updated_osvar = updated_osvars[0]
    print(f'Updated osvar content')

    assert updated_osvar['id'] == created_osvar_id
    assert updated_osvar['content'] == 'This is another test osvar value'

    # -- Delete osvars --
    #
    # Delete existing osvars by id.
    # Takes a list of items to delete.
    #
    opalapi.osvars.delete([
        {'id': created_osvar_id},
    ])
    print(f'Deleted osvar with id {created_osvar_id}')

    assert not any(osvar['id'] == created_osvar_id for osvar in opalapi.osvars.list_all())
