import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def address_domain():
    created_domains = opalapi.domains.create([
        {'name': f'test-domain-{RANDID}.xyz'},
    ])
    domain = created_domains[0]
    yield domain
    opalapi.domains.delete([
        {'id': domain['id']},
    ])

@pytest.fixture
def mailuser_server():
    server = opalapi.servers.list_all()['imap_servers'][0]
    yield server

@pytest.fixture
def address_mailuser(mailuser_server):
    created_mailusers = opalapi.mailusers.create([
        {'imap_server': mailuser_server['id'], 'name': f'test-mailuser-{RANDID}'},
    ])
    mailuser = created_mailusers[0]
    yield mailuser
    opalapi.mailusers.delete([
        {'id': mailuser['id']},
    ])

def test_addresses(address_domain, address_mailuser):
    address_domain_name = address_domain['name']
    address_mailuser_id = address_mailuser['id']
    address_mailuser_name = address_mailuser['name']

    # -- Create addresses --
    #
    # Create new addresses.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_addresses = opalapi.addresses.create([
        { 'source': f'someone@{address_domain_name}',
          'destinations': [address_mailuser_id],
          'forwards': ['somebody@example.com'],
        }
    ])
    created_address = created_addresses[0]
    created_address_id = created_address['id']
    created_address_source = created_address['source']
    created_address_destinations = created_address['destinations']
    created_address_forwards = created_address['forwards']
    print(f'Created address {created_address_source} delivering to {address_mailuser_name} and forwarding to somebody@example.com')

    assert created_address['source'] == f'someone@{address_domain_name}'
    assert created_address['destinations'] == [address_mailuser_id]
    assert created_address['forwards'] == ['somebody@example.com']

    # -- List addresses --
    #
    # Retrieve all existing addresses.
    #
    for address in opalapi.addresses.list_all():
        address_id = address['id']
        address_source = address['source']
        address_destination_ids = address['destinations']
        print(f'Listed address {address_source}')

    # Use embed to include more information about the destination mailusers.
    #   Without the embed, address['destinations'] would contain a uuid list.
    #   By adding embed=['destinations'], it contains a dict list instead.
    for address in opalapi.addresses.list_all(embed=['destinations']):
        address_id = address['id']
        address_source = address['source']
        if address['destinations']:
            address_destination_ids = [destination['id'] for destination in address['destinations']]
            address_destination_names = [destination['name'] for destination in address['destinations']]
            address_forwards = address['forwards']
            address_destination_name = address_destination_names[0]
            print(f'Listed address {address_source} delivering to mailuser {address_destination_name}')

    # -- Read single address --
    #
    # Retrieve one existing address by id.
    #
    address = opalapi.addresses.read(address_id)
    print(f'Read address by id: {address_id}')

    assert address['id'] == address_id

    # -- Update addresses --
    #
    # Change the password of existing addresses.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_addresses = opalapi.addresses.update([
        {'id': created_address_id, 'forwards': ['somebody@example.com', 'somebody@example.net']},
    ])
    updated_address = updated_addresses[0]
    print(f'Updated address forwards')

    assert updated_address['id'] == created_address_id
    assert sorted(updated_address['forwards']) == sorted(['somebody@example.com', 'somebody@example.net'])

    # -- Delete addresses --
    #
    # Delete existing addresses by id.
    # Takes a list of items to delete.
    #
    opalapi.addresses.delete([
        {'id': created_address_id},
    ])
    print(f'Deleted address with id {created_address_id}')

    assert not any(address['id'] == created_address_id for address in opalapi.addresses.list_all())
