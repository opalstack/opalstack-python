import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

@pytest.fixture
def osuser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def site_ip(osuser_server):
    server_ip = [
        ip
        for ip in opalapi.ips.list_all()
        if ip['server'] == osuser_server['id']
        and ip['primary']
    ][0]
    yield server_ip

@pytest.fixture
def site_domain():
    created_domains = opalapi.domains.create([
        {'name': f'test-domain-{RANDID}.xyz'},
    ])
    domain = created_domains[0]
    yield domain
    opalapi.domains.delete([
        {'id': domain['id']},
    ])

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

@pytest.fixture
def site_app(app_osuser):
    created_apps = opalapi.apps.create([
        {'name': f'test-app-{RANDID}', 'osuser': app_osuser['id'], 'type': 'STA'},
    ])
    app = created_apps[0]
    yield app
    opalapi.apps.delete([
        {'id': app['id']},
    ])

def test_sites(site_ip, site_domain, site_app):
    site_ip_id = site_ip['id']
    site_domain_id = site_domain['id']
    site_domain_name = site_domain['name']
    site_app_id = site_app['id']
    site_app_name = site_app['name']

    # -- Create sites --
    #
    # Create new sites.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_sites = opalapi.sites.create([
        { 'name': f'test-site-{RANDID}',
          'ip4': site_ip_id,
          'domains': [site_domain_id],
          'routes': [
              {'app': site_app_id, 'uri': '/'},
          ]
        },
    ])
    created_site = created_sites[0]
    created_site_id = created_site['id']
    created_site_name = created_site['name']
    print(f'Created site {created_site_name} mounting app {site_app_name} on domain {site_domain_name}')

    assert created_site['name'] == f'test-site-{RANDID}'
    assert created_site['domains'] == [site_domain_id]
    assert created_site['routes'][0]['app'] == site_app_id
    assert created_site['routes'][0]['uri'] == '/'

    # -- List sites --
    #
    # Retrieve all existing sites.
    #
    for site in opalapi.sites.list_all():
        site_id = site['id']
        site_name = site['name']
        print(f'Listed site {site_id} (name: {site_name})')

    # Use embed to include more information about the apps.
    #   Without the embed, site['routes']['app'] would contain a uuid.
    #   By adding embed=['app'], it contains a dict instead.
    # This also applies to ips, domains, and certs.
    for site in opalapi.sites.list_all(embed=['app']):
        site_id = site['id']
        site_name = site['name']
        if site['routes']:
            this_site_app_id = site['routes'][0]['app']['id']
            this_site_app_name = site['routes'][0]['app']['name']
            print(f'Listed site {site_name} mounting app {this_site_app_name}')

    # -- Read single site --
    #
    # Retrieve one existing site by id.
    #
    site = opalapi.sites.read(site_id)
    print(f'Read site by id: {site_id}')

    assert site['id'] == site_id

    # -- Update sites --
    #
    # Change the configuration of existing sites.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_sites = opalapi.sites.update([
        {'id': created_site_id, 'name': f'test-updated-site-{RANDID}'},
    ])
    updated_site = updated_sites[0]
    print(f'Updated site name')

    assert updated_site['id'] == created_site_id
    assert updated_site['name'] == f'test-updated-site-{RANDID}'

    # -- Delete sites --
    #
    # Delete existing sites by id.
    # Takes a list of items to delete.
    #
    opalapi.sites.delete([
        {'id': created_site_id},
    ])
    print(f'Deleted site with id {created_site_id}')

    assert not any(site['id'] == created_site_id for site in opalapi.sites.list_all())
