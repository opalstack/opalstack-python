import string
import random

import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def mailuser_server():
    server = opalapi.servers.list_all()['imap_servers'][0]
    yield server

def test_mailusers(mailuser_server):
    mailuser_server_id = mailuser_server['id']
    mailuser_server_hostname = mailuser_server['hostname']

    # -- Create mailusers --
    #
    # Create new mailusers.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_mailusers = opalapi.mailusers.create([
        {'imap_server': mailuser_server_id, 'name': f'test-mailuser-{RANDID}'},
    ])
    created_mailuser = created_mailusers[0]
    created_mailuser_id = created_mailuser['id']
    created_mailuser_name = created_mailuser['name']
    print(f'Created mailuser {created_mailuser_name} on server {mailuser_server_hostname}')

    assert created_mailuser['name'] == f'test-mailuser-{RANDID}'
    assert created_mailuser['imap_server'] == mailuser_server_id

    # -- List mailusers --
    #
    # Retrieve all existing mailusers.
    #
    for mailuser in opalapi.mailusers.list_all():
        mailuser_id = mailuser['id']
        mailuser_name = mailuser['name']
        mailuser_server_id = mailuser['imap_server']
        print(f'Listed mailuser {mailuser_name}')

    # Use embed to include more information about the domain.
    #   Without the embed, mailuser['imap_server'] would contain a uuid.
    #   By adding embed=['imap_server'], it contains a dict instead.
    for mailuser in opalapi.mailusers.list_all(embed=['imap_server']):
        mailuser_id = mailuser['id']
        mailuser_name = mailuser['name']
        mailuser_server_id = mailuser['imap_server']['id']
        mailuser_server_hostname = mailuser['imap_server']['hostname']
        print(f'Listed mailuser {mailuser_name} on {mailuser_server_hostname}')

    # -- Read single mailuser --
    #
    # Retrieve one existing mailuser by id.
    #
    mailuser = opalapi.mailusers.read(mailuser_id)
    print(f'Read mailuser by id: {mailuser_id}')

    assert mailuser['id'] == mailuser_id

    # -- Update mailusers --
    #
    # Change the password of existing mailusers.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_mailusers = opalapi.mailusers.update([
        {'id': created_mailuser_id, 'password': ''.join(random.choices(string.ascii_lowercase, k=32))},
    ])
    updated_mailuser = updated_mailusers[0]
    print(f'Updated mailuser password')

    assert updated_mailuser['id'] == created_mailuser_id

    # -- Delete mailusers --
    #
    # Delete existing mailusers by id.
    # Takes a list of items to delete.
    #
    opalapi.mailusers.delete([
        {'id': created_mailuser_id},
    ])
    print(f'Deleted mailuser with id {created_mailuser_id}')

    assert not any(mailuser['id'] == created_mailuser_id for mailuser in opalapi.mailusers.list_all())
