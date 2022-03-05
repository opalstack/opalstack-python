import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def osuser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def app_osuser(osuser_server):
    created_osusers = opalapi.osusers.create([
        {'server': osuser_server['id'], 'name': f'test-osuser-{RANDID}'},
    ])
    osuser = created_osusers[0]
    yield osuser
    opalapi.osusers.delete([
        {'id': osuser['id']},
    ])

def test_apps(app_osuser):
    app_osuser_id = app_osuser['id']
    app_osuser_name = app_osuser['name']

    # -- Create apps --
    #
    # Create new apps.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_apps = opalapi.apps.create([
        { 'name': f'test-app-{RANDID}',
          'osuser': app_osuser_id,
          'type': 'STA',
        },
    ])
    created_app = created_apps[0]
    created_app_id = created_app['id']
    created_app_name = created_app['name']
    print(f'Created app {created_app_name} under osuser {app_osuser_name}')

    assert created_app['name'] == f'test-app-{RANDID}'
    assert created_app['osuser'] == app_osuser_id
    assert created_app['type'] == 'STA'

    # -- List apps --
    #
    # Retrieve all existing apps.
    #
    for app in opalapi.apps.list_all():
        app_id = app['id']
        app_name = app['name']
        this_app_osuser_id = app['osuser']
        print(f'Listed app {app_id} (name: {app_name})')

    # Use embed to include more information about the osuser.
    #   Without the embed, app['osuser'] would contain a uuid.
    #   By adding embed=['osuser'], it contains a dict instead.
    for app in opalapi.apps.list_all(embed=['osuser']):
        app_id = app['id']
        app_name = app['name']
        this_app_osuser_id = app['osuser']['id']
        this_app_osuser_name = app['osuser']['name']
        print(f'Listed app {app_name} under {this_app_osuser_name}')

    # -- Read single app --
    #
    # Retrieve one existing app by id.
    #
    app = opalapi.apps.read(app_id)
    print(f'Read app by id: {app_id}')

    assert app['id'] == app_id

    # -- Update apps --
    #
    # Change the configuration of existing apps.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_apps = opalapi.apps.update([
        {'id': created_app_id, 'json': {'php_version': 74}},
    ])
    updated_app = updated_apps[0]
    print(f'Updated app json')

    assert updated_app['id'] == created_app_id
    assert updated_app['json']['php_version'] == 74

    # -- Delete apps --
    #
    # Delete existing apps by id.
    # Takes a list of items to delete.
    #
    opalapi.apps.delete([
        {'id': created_app_id},
    ])
    print(f'Deleted app with id {created_app_id}')

    assert not any(app['id'] == created_app_id for app in opalapi.apps.list_all())
