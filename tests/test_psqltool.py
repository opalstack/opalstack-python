import time
import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

from opalstack.util import SshRunner, PsqlTool

@pytest.fixture
def psqluser_server():
    server = opalapi.servers.list_all()['web_servers'][0]
    yield server

@pytest.fixture
def local_psqluser(psqluser_server):
    created_psqlusers = opalapi.psqlusers.create([
        {'server': psqluser_server['id'], 'name': f'localdbu-{RANDID}', 'external': False},
    ])
    psqluser = created_psqlusers[0]
    yield psqluser
    opalapi.psqlusers.delete([
        {'id': psqluser['id']},
    ])

@pytest.fixture
def local_psqldb(psqluser_server, local_psqluser):
    created_psqldbs = opalapi.psqldbs.create([
        { 'name': f'localdb-{RANDID}',
          'server': psqluser_server['id'],
          'dbusers_readwrite': [local_psqluser['id']],
        },
    ])
    psqldb = created_psqldbs[0]
    yield psqldb
    opalapi.psqldbs.delete([
        {'id': psqldb['id']},
    ])

@pytest.fixture
def remote_osuser(psqluser_server):
    created_osusers = opalapi.osusers.create([
        {'server': psqluser_server['id'], 'name': f'remoteosu-{RANDID}'},
    ])
    osuser = created_osusers[0]
    yield osuser
    opalapi.osusers.delete([
        {'id': osuser['id']},
    ])

@pytest.fixture
def remote_psqluser(psqluser_server):
    created_psqlusers = opalapi.psqlusers.create([
        {'server': psqluser_server['id'], 'name': f'remotedbu-{RANDID}', 'external': False},
    ])
    psqluser = created_psqlusers[0]
    yield psqluser
    opalapi.psqlusers.delete([
        {'id': psqluser['id']},
    ])

@pytest.fixture
def remote_psqldb(psqluser_server, remote_psqluser):
    created_psqldbs = opalapi.psqldbs.create([
        { 'name': f'remotedb-{RANDID}',
          'server': psqluser_server['id'],
          'dbusers_readwrite': [remote_psqluser['id']],
        },
    ])
    psqldb = created_psqldbs[0]
    yield psqldb
    opalapi.psqldbs.delete([
        {'id': psqldb['id']},
    ])

def test_psqltool(psqluser_server, local_psqluser, local_psqldb, remote_osuser, remote_psqluser, remote_psqldb):
    # Some time for pg_hba update
    time.sleep(60)

    this_psqltool = PsqlTool('localhost', 5432, local_psqluser['name'], local_psqluser['default_password'], local_psqldb['name'], 'this.sqlpasswd')
    this_psqltool.export_local_db('this.sql')
    this_psqltool.import_local_db('this.sql')
    os.remove('this.sql')

    osuser_name = remote_osuser['name']
    osuser_server = psqluser_server['hostname']
    sshrunner = SshRunner(f'{osuser_name}@{osuser_server}', remote_osuser['default_password'], 'that.sshpass')
    that_psqltool = PsqlTool('localhost', 5432, remote_psqluser['name'], remote_psqluser['default_password'], remote_psqldb['name'], 'that-local.sqlpasswd', 'that-remote.sqlpasswd')
    that_psqltool.export_remote_db(sshrunner, 'that.sql')
    that_psqltool.import_remote_db(sshrunner, 'that.sql')
    assert not os.path.exists('that.sshpass')
