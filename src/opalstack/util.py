import os
import time
import logging
import subprocess

def ts():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

def run(cmd, stdin=None, strip=True, ensure_status=[0]):
    logging.debug(f'Running cmd: {cmd}')
    if isinstance(cmd, str):
        p = subprocess.run(cmd, shell=True, executable='/bin/bash', stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif isinstance(cmd, list) or isinstance(cmd, tuple):
        p = subprocess.run(cmd, shell=False, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        raise ValueError('cmd must be a string, list, or tuple')
    stdout = p.stdout.decode().strip() if strip else p.stdout.decode()
    stderr = p.stderr.decode().strip() if strip else p.stderr.decode()
    if ensure_status and p.returncode not in ensure_status:
        raise RuntimeError(f'Command "{cmd}" exited with status {p.returncode}. Stderr: {stderr}')
    return (stdout, stderr, p.returncode)

def filt(items, keymap, sep='.'):
    """
    Filters a list of dicts by given keymap.
    By default, periods represent nesting (configurable by passing `sep`).

    For example:
        items = [
            {'name': 'foo', 'server': {'id': 1234, 'hostname': 'host1'}, 'loc': 4},
            {'name': 'bar', 'server': {'id': 2345, 'hostname': 'host2'}, 'loc': 3},
            {'name': 'baz', 'server': {'id': 3456, 'hostname': 'host3'}, 'loc': 4},
        ]
        filt(items, {'loc': 4})                                   # Returns [foo, baz]
        filt(items, {'loc': 4, 'server.hostname': 'host1'})       # Returns [foo]
        filt(items, {'name': 'bar', 'server.hostname': 'host2'})  # Returns [bar]
        filt(items, {'name': 'bar', 'server.hostname': 'host3'})  # Returns []
    """
    filtered = []
    for item in items:
        for keypath in keymap:
            val = item.copy()
            for key in keypath.split(sep):
                val = val[key]
            if val != keymap[keypath]: break
        else:
            filtered.append(item)
    return filtered

def laxfilt(items, keymap, sep='.'):
    """
    Like filt(), except that KeyErrors are not raised.
    Instead, a missing key is considered to be a mismatch.

    For example:
        items = [
            {'name': 'foo', 'server': {'id': 1234, 'hostname': 'host1'}, 'loc': 4, 'yyy': 'zzz'},
            {'name': 'bar', 'server': {'id': 2345, 'hostname': 'host2'}, 'loc': 3},
            {'name': 'baz', 'server': {'id': 3456, 'hostname': 'host3'}, 'loc': 4},
        ]
        filt(items, {'yyy': 'zzz'})     # Raises KeyError
        laxfilt(items, {'yyy': 'zzz'})  # Returns [foo]
    """
    filtered = []
    for item in items:
        for keypath in keymap:
            ok = True
            val = item.copy()
            for key in keypath.split(sep):
                try:
                    val = val[key]
                except KeyError:
                    ok = False
                    break
            if not ok or val != keymap[keypath]: break
        else:
            filtered.append(item)
    return filtered

def one(items):
    assert len(items) == 1
    return items[0]

def one_or_none(items):
    if not items: return None
    assert len(items) < 2
    if items: return items[0]
    return None

def filt_one(items, keymap):
    return one(filt(items, keymap))

def filt_one_or_none(items, keymap):
    return one_or_none(filt(items, keymap))

def laxfilt_one(items, keymap):
    return one(laxfilt(items, keymap))

def laxfilt_one_or_none(items, keymap):
    return one_or_none(laxfilt(items, keymap))

class SshRunner():
    def __init__(self, userhost, ssh_password=None, ssh_password_filepath=None, ssh_privkey_path=None, ssh_pubkey_path=None):
        if (ssh_password and not ssh_password_filepath) or (ssh_password_filepath and not ssh_password):
            raise ValueError('ssh_password and ssh_password_filepath must be specified together')

        if (ssh_privkey_path and not ssh_pubkey_path) or (ssh_pubkey_path and not ssh_privkey_path):
            raise ValueError('ssh_privkey_path and ssh_pubkey_path must be specified together')

        if not ssh_password and not ssh_privkey_path:
            raise ValueError('must specify ssh_password and/or ssh_privkey_path')

        self.userhost = userhost
        self.ssh_password = ssh_password
        self.ssh_password_filepath = ssh_password_filepath
        self.ssh_privkey_path = ssh_privkey_path
        self.ssh_pubkey_path = ssh_pubkey_path

    #
    # Password-based SSH
    #

    def run_via_sshpass(self, cmd, *args, **kwargs):
        prelude = ['sshpass', '-f', self.ssh_password_filepath]
        with open(self.ssh_password_filepath, 'w') as fp: fp.write(self.ssh_password + '\n')
        try:
            return run(prelude + cmd, *args, **kwargs)
        finally:
            os.remove(self.ssh_password_filepath)

    def run_passbased_ssh(self, remote_cmd, *args, **kwargs):
        prelude = [ '/usr/bin/ssh', '-q',
                    '-o', 'PasswordAuthentication=yes',
                    '-o', 'PubkeyAuthentication=no',
                    '-o', 'StrictHostKeyChecking=no',
                    self.userhost,
        ]
        return self.run_via_sshpass(prelude + [remote_cmd], *args, **kwargs)

    def run_passbased_scp(self, src, dst, *args, **kwargs):
        prelude = [ '/usr/bin/scp', '-q',
                    '-o', 'PasswordAuthentication=yes',
                    '-o', 'PubkeyAuthentication=no',
                    '-o', 'StrictHostKeyChecking=no',
        ]
        return self.run_via_sshpass(prelude + [src, dst], *args, **kwargs)

    def run_passbased_rsync(self, src, dst, *args, **kwargs):
        prelude = [ 'rsync', '-a',
                    '-e', f'ssh -o PasswordAuthentication=yes'
                              ' -o PubkeyAuthentication=no'
                              ' -o StrictHostKeyChecking=no',
        ]
        return self.run_via_sshpass(prelude + [src, dst], *args, **kwargs)

    def check_ssh_password(self):
        stdout, stderr, retcode = self.run_passbased_ssh('/bin/true', ensure_status=[])
        if retcode != 0:
            logging.error(f'SSH credentials check failed with exit status {retcode} (stdout: "{stdout}", stderr: "{stderr}")')
        return retcode == 0

    def ensure_valid_ssh_password(self):
        if not self.check_ssh_password():
            raise RuntimeError('Invalid SSH Password')

    #
    # Key-based SSH
    #

    def run_keybased_ssh(self, remote_cmd, *args, **kwargs):
        prelude = [ '/usr/bin/ssh', '-q',
                    '-i', self.ssh_privkey_path,
                    '-o', 'PasswordAuthentication=no',
                    '-o', 'PubkeyAuthentication=yes',
                    '-o', 'StrictHostKeyChecking=no',
                    self.userhost,
        ]
        return run(prelude + [remote_cmd], *args, **kwargs)

    def run_keybased_scp(self, src, dst, *args, **kwargs):
        prelude = [ '/usr/bin/scp', '-q',
                    '-i', self.ssh_privkey_path,
                    '-o', 'PasswordAuthentication=no',
                    '-o', 'PubkeyAuthentication=yes',
                    '-o', 'StrictHostKeyChecking=no',
        ]
        return run(prelude + [src, dst], *args, **kwargs)

    def run_keybased_rsync(self, src, dst, *args, **kwargs):
        prelude = [ 'rsync', '-a',
                    '-e', f'ssh -i {self.ssh_privkey_path}'
                              ' -o PasswordAuthentication=no'
                              ' -o PubkeyAuthentication=yes'
                              ' -o StrictHostKeyChecking=no',
        ]
        return run(prelude + [src, dst], *args, **kwargs)

    def check_ssh_key(self):
        stdout, stderr, retcode = self.run_keybased_ssh('/bin/true', ensure_status=[])
        if retcode != 0:
            logging.error(f'SSH credentials check failed with exit status {retcode} (stdout: "{stdout}", stderr: "{stderr}")')
        return retcode == 0

    def ensure_valid_ssh_key(self):
        if not self.check_ssh_key():
            raise RuntimeError('Invalid SSH Key')

    def force_ssh_key_permissions(self, set_webserver_acls=True):
        self.run_passbased_ssh('setfacl -b $HOME')
        self.run_passbased_ssh('setfacl -b $HOME/.ssh')
        self.run_passbased_ssh('setfacl -b $HOME/.ssh/*')
        self.run_passbased_ssh('chmod 710 $HOME')
        self.run_passbased_ssh('chmod 700 $HOME/.ssh')
        self.run_passbased_ssh('chmod 600 $HOME/.ssh/*')
        if set_webserver_acls:
            self.run_passbased_ssh('setfacl -m u:apache:r-x $HOME')
            self.run_passbased_ssh('setfacl -m u:nginx:r-x $HOME')

    def create_ssh_key(self):
        cmd = [ 'ssh-keygen',
                '-t', 'rsa',
                '-b', '4096',
                '-N', '',
                '-f', self.ssh_privkey_path
        ]
        subprocess.run(cmd)

    def set_ssh_key(self):
        if ( not os.path.exists(self.ssh_privkey_path) or
             not os.path.exists(self.ssh_pubkey_path) ): self.create_ssh_key()

        if self.check_ssh_key():
            logging.debug('SSH key already set')
            return

        logging.debug('Setting SSH key...')
        cmd = [ 'ssh-copy-id',
                '-i', self.ssh_privkey_path,
                self.userhost
        ]
        self.ensure_valid_ssh_password()
        self.run_via_sshpass(cmd)
        logging.debug('SSH key set successfully')
