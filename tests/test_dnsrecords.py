import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def dnsrecord_domain():
    created_domains = opalapi.domains.create([
        {'name': f'test-dnsrecord-{RANDID}.xyz'},
    ])
    created_domain = created_domains[0]
    yield created_domain
    opalapi.domains.delete([
        {'id': created_domain['id']},
    ])

def test_dnsrecords(dnsrecord_domain):
    dnsrecord_domain_id = dnsrecord_domain['id']
    dnsrecord_domain_name = dnsrecord_domain['name']

    # -- Create dnsrecords --
    #
    # Create new dnsrecords.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_dnsrecords = opalapi.dnsrecords.create([
        {'domain': dnsrecord_domain_id, 'type': 'A', 'content': '10.111.222.33'},
    ])
    created_dnsrecord = created_dnsrecords[0]
    created_dnsrecord_id = created_dnsrecord['id']
    created_dnsrecord_type = created_dnsrecord['type']
    created_dnsrecord_content = created_dnsrecord['content']
    print(f'Created a dnsrecord on {dnsrecord_domain_name} with type {created_dnsrecord_type} and content {created_dnsrecord_content}')

    assert created_dnsrecord['type'] == 'A'
    assert created_dnsrecord['content'] == '10.111.222.33'
    assert created_dnsrecord['domain'] == dnsrecord_domain_id

    # -- List dnsrecords --
    #
    # Retrieve all existing dnsrecords.
    #
    for dnsrecord in opalapi.dnsrecords.list_all():
        dnsrecord_id = dnsrecord['id']
        dnsrecord_type = dnsrecord['type']
        dnsrecord_content = dnsrecord['content']
        dnsrecord_priority = dnsrecord['priority']
        dnsrecord_ttl = dnsrecord['ttl']
        dnsrecord_domain_id = dnsrecord['domain']
        print(f'Listed dnsrecord (type {dnsrecord_type}, priority: {dnsrecord_priority}, ttl: {dnsrecord_ttl}): {dnsrecord_content}')

    # Use embed to include more information about the domain.
    #   Without the embed, dnsrecord['domain'] would contain a uuid.
    #   By adding embed=['domain'], it contains a dict instead.
    for dnsrecord in opalapi.dnsrecords.list_all(embed=['domain']):
        dnsrecord_id = dnsrecord['id']
        dnsrecord_type = dnsrecord['type']
        dnsrecord_content = dnsrecord['content']
        dnsrecord_priority = dnsrecord['priority']
        dnsrecord_ttl = dnsrecord['ttl']
        dnsrecord_domain_id = dnsrecord['domain']['id']
        dnsrecord_domain_name = dnsrecord['domain']['name']
        print(f'Listed dnsrecord: DNS {dnsrecord_type} record on {dnsrecord_domain_name} with content {dnsrecord_content}')

    # -- Read single dnsrecord --
    #
    # Retrieve one existing dnsrecord by id.
    #
    dnsrecord = opalapi.dnsrecords.read(dnsrecord_id)
    print(f'Read dnsrecord by id: {dnsrecord_id}')

    assert dnsrecord['id'] == dnsrecord_id

    # -- Update dnsrecords --
    #
    # Change the name of existing dnsrecords.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_dnsrecords = opalapi.dnsrecords.update([
        {'id': created_dnsrecord_id, 'content': '10.111.222.44'},
    ])
    updated_dnsrecord = updated_dnsrecords[0]
    updated_dnsrecord_content = updated_dnsrecord['content']
    print(f'Updated dnsrecord content from "10.111.222.33" to "{updated_dnsrecord_content}"')

    assert updated_dnsrecord['content'] == '10.111.222.44'
    assert updated_dnsrecord['id'] == created_dnsrecord_id

    # -- Delete dnsrecords --
    #
    # Delete existing dnsrecords by id.
    # Takes a list of items to delete.
    #
    opalapi.dnsrecords.delete([
        {'id': created_dnsrecord_id},
    ])
    print(f'Deleted dnsrecord with id {created_dnsrecord_id}')

    assert not any(dnsrecord['id'] == created_dnsrecord_id for dnsrecord in opalapi.dnsrecords.list_all())
