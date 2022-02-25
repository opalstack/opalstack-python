import logging
import subprocess

def run(cmd, stdin=None, strip=True, ensure_status=[0]):
    logging.debug(f'Running cmd: {cmd}')
    p = subprocess.run(cmd, shell=True, executable='/bin/bash', stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
