import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

from opalstack.util import SshRunner, MariaTool

@pytest.fixture
def mariauser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def local_mariauser(mariauser_server):
    created_mariausers = opalapi.mariausers.create([
        {'server': mariauser_server['id'], 'name': f'localdbu-{RANDID}', 'external': False},
    ])
    mariauser = created_mariausers[0]
    yield mariauser
    opalapi.mariausers.delete([
        {'id': mariauser['id']},
    ])

@pytest.fixture
def local_mariadb(mariauser_server, local_mariauser):
    created_mariadbs = opalapi.mariadbs.create([
        { 'name': f'localdb-{RANDID}',
          'server': mariauser_server['id'],
          'dbusers_readwrite': [local_mariauser['id']],
        },
    ])
    mariadb = created_mariadbs[0]
    yield mariadb
    opalapi.mariadbs.delete([
        {'id': mariadb['id']},
    ])

@pytest.fixture
def remote_osuser(mariauser_server):
    created_osusers = opalapi.osusers.create([
        {'server': mariauser_server['id'], 'name': f'remoteosu-{RANDID}'},
    ])
    osuser = created_osusers[0]
    yield osuser
    opalapi.osusers.delete([
        {'id': osuser['id']},
    ])

@pytest.fixture
def remote_mariauser(mariauser_server):
    created_mariausers = opalapi.mariausers.create([
        {'server': mariauser_server['id'], 'name': f'remotedbu-{RANDID}', 'external': False},
    ])
    mariauser = created_mariausers[0]
    yield mariauser
    opalapi.mariausers.delete([
        {'id': mariauser['id']},
    ])

@pytest.fixture
def remote_mariadb(mariauser_server, remote_mariauser):
    created_mariadbs = opalapi.mariadbs.create([
        { 'name': f'remotedb-{RANDID}',
          'server': mariauser_server['id'],
          'dbusers_readwrite': [remote_mariauser['id']],
        },
    ])
    mariadb = created_mariadbs[0]
    yield mariadb
    opalapi.mariadbs.delete([
        {'id': mariadb['id']},
    ])

def test_mariatool(mariauser_server, local_mariauser, local_mariadb, remote_osuser, remote_mariauser, remote_mariadb):
    this_mariatool = MariaTool('localhost', 5432, local_mariauser['name'], local_mariauser['default_password'], local_mariadb['name'], 'this.sqlpasswd')
    this_mariatool.export_local_db('this.sql')
    this_mariatool.import_local_db('this.sql')
    os.remove('this.sql')

    osuser_name = remote_osuser['name']
    osuser_server = mariauser_server['hostname']
    sshrunner = SshRunner(f'{osuser_name}@{osuser_server}', remote_osuser['default_password'], 'that.sshpass')
    that_mariatool = MariaTool('localhost', 5432, remote_mariauser['name'], remote_mariauser['default_password'], remote_mariadb['name'], 'that-local.sqlpasswd', 'that-remote.sqlpasswd')
    that_mariatool.export_remote_db(sshrunner, 'that.sql')
    that_mariatool.import_remote_db(sshrunner, 'that.sql')
    assert not os.path.exists('that.sshpass')
