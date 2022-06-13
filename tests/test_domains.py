from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

def test_domains():
    # -- Create domains --
    #
    # Create new domains.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_domains = opalapi.domains.create([
        {'name': f'test-domain-{RANDID}.xyz'},
    ])
    created_domain = created_domains[0]
    created_domain_id = created_domain['id']
    created_domain_name = created_domain['name']
    print(f'Created domain {created_domain_name}')

    assert created_domain['name'] == f'test-domain-{RANDID}.xyz'

    # -- List domains --
    #
    # Retrieve all existing domains.
    #
    for domain in opalapi.domains.list_all():
        domain_id = domain['id']
        domain_name = domain['name']
        print(f'Listed domain {domain_name}')

    # -- Read single domain --
    #
    # Retrieve one existing domain by id.
    #
    domain = opalapi.domains.read(domain_id)
    print(f'Read domain by id: {domain_id}')

    assert domain['id'] == domain_id

    # -- Delete domains --
    #
    # Delete existing domains by id.
    # Takes a list of items to delete.
    #
    opalapi.domains.delete([
        {'id': created_domain_id},
    ])
    print(f'Deleted domain with id {created_domain_id}')

    assert not any(domain['id'] == created_domain_id for domain in opalapi.domains.list_all())
