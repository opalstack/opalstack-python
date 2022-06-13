import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

from opalstack.util import SshRunner

TMP_DIRPATH = os.environ['XDG_RUNTIME_DIR'] + f'/tmp-{RANDID}'
TMP_SSH_PASSWORD_FILEPATH = f'{TMP_DIRPATH}/sshpass.txt'
TMP_SSH_PRIVKEY_PATH = f'{TMP_DIRPATH}/id_rsa'
TMP_SSH_PUBKEY_PATH = f'{TMP_DIRPATH}/id_rsa.pub'
TMP_TXTFILE_FPATH = f'{TMP_DIRPATH}/temp.txt'

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

@pytest.fixture(autouse=True)
def tmpfiles():
    os.mkdir(TMP_DIRPATH)
    yield
    if os.path.exists(TMP_SSH_PASSWORD_FILEPATH): os.remove(TMP_SSH_PASSWORD_FILEPATH)
    if os.path.exists(TMP_SSH_PRIVKEY_PATH): os.remove(TMP_SSH_PRIVKEY_PATH)
    if os.path.exists(TMP_SSH_PUBKEY_PATH): os.remove(TMP_SSH_PUBKEY_PATH)
    if os.path.exists(TMP_TXTFILE_FPATH): os.remove(TMP_TXTFILE_FPATH)
    os.rmdir(TMP_DIRPATH)

def test_ssh(osuser_server, app_osuser):
    osuser_name = app_osuser['name']
    osuser_pass = app_osuser['default_password']
    server_hostname = osuser_server['hostname']
    userhost = f'{osuser_name}@{server_hostname}'

    with open(TMP_TXTFILE_FPATH, 'w') as fp:
        fp.write('This is a tempfile')

    sshrunner = SshRunner(
        userhost,
        ssh_password=osuser_pass,
        ssh_password_filepath=TMP_SSH_PASSWORD_FILEPATH,
        ssh_privkey_path=TMP_SSH_PRIVKEY_PATH,
        ssh_pubkey_path=TMP_SSH_PUBKEY_PATH,
    )
    sshrunner.ensure_valid_ssh_password()

    sshrunner.run_passbased_rsync(TMP_TXTFILE_FPATH, f'{userhost}:')
    stdout, stderr, retcode = sshrunner.run_passbased_ssh('cat temp.txt')
    assert stdout == 'This is a tempfile'
    assert stderr == ''
    assert retcode == 0

    sshrunner.run_passbased_scp(TMP_TXTFILE_FPATH, f'{userhost}:newfile.txt')
    stdout, stderr, retcode = sshrunner.run_passbased_ssh('cat newfile.txt')
    assert stdout == 'This is a tempfile'
    assert stderr == ''
    assert retcode == 0

    with open(TMP_TXTFILE_FPATH, 'w') as fp:
        fp.write('This is an updated tempfile')

    sshrunner.set_ssh_key()
    sshrunner.force_ssh_key_permissions()
    sshrunner.ensure_valid_ssh_key()

    sshrunner.run_keybased_rsync(TMP_TXTFILE_FPATH, f'{userhost}:')
    stdout, stderr, retcode = sshrunner.run_keybased_ssh('cat temp.txt')
    assert stdout == 'This is an updated tempfile'
    assert stderr == ''
    assert retcode == 0

    sshrunner.run_keybased_scp(TMP_TXTFILE_FPATH, f'{userhost}:newfile.txt')
    stdout, stderr, retcode = sshrunner.run_keybased_ssh('cat newfile.txt')
    assert stdout == 'This is an updated tempfile'
    assert stderr == ''
    assert retcode == 0
