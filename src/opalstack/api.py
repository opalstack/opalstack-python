import os
import logging
import time
import json
import requests
import socket

from .util import filt_one_or_none

from .servers import ServersManager
from .domains import DomainsManager
from .dnsrecords import DnsrecordsManager
from .osusers import OSUsersManager
from .apps import AppsManager
from .mariadbs import MariadbsManager
from .mariausers import MariausersManager
from .psqldbs import PsqldbsManager
from .psqlusers import PsqlusersManager
from .sites import SitesManager
from .addresses import AddressesManager
from .mailusers import MailusersManager

API_URL = 'https://my.opalstack.com/api/v1'

class Api():
    def __init__(self, token):
        self.token = token
        self.api_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.token}',
        }
        self.servers = ServersManager(self)
        self.domains = DomainsManager(self)
        self.dnsrecords = DnsrecordsManager(self)
        self.osusers = OSUsersManager(self)
        self.apps = AppsManager(self)
        self.mariadbs = MariadbsManager(self)
        self.mariausers = MariausersManager(self)
        self.psqldbs = PsqldbsManager(self)
        self.psqlusers = PsqlusersManager(self)
        self.sites = SitesManager(self)
        self.addresses = AddressesManager(self)
        self.mailusers= MailusersManager(self)

    def request(self, urlpath, dataObj, method, ensure_status=[200]):
        if method not in ('GET', 'POST'): raise ValueError(f'Invalid request method {method}')
        if method == 'GET':
            if dataObj is not None: raise ValueError(f'GET request method must not have dataObj')
            logging.debug(f'Performing GET {urlpath}')
            resp = requests.get(API_URL + urlpath, headers=self.api_headers)
        if method == 'POST':
            if type(dataObj) is None: raise ValueError(f'POST request method must have dataObj')
            logging.debug(f'Performing POST {urlpath} with {repr(dataObj)}')
            resp = requests.post(API_URL + urlpath, headers=self.api_headers, json=dataObj)
        logging.debug(resp.content.decode())
        try:
            result = json.loads(resp.content.decode())
        except json.decoder.JSONDecodeError:
            result = None
        logging.debug(f'Got resp: {repr(resp)} and result {repr(result)}')
        if ensure_status and resp.status_code not in ensure_status:
            if resp.status_code in [200, 400]:
                raise RuntimeError(f'Unexpected status_code: {resp.status_code}, result: {result}')
            else:
                raise RuntimeError(f'Unexpected status_code: {resp.status_code}')
        return resp, result

    def request_result(self, urlpath, dataObj, method, ensure_status=[200]):
        resp, result = self.request(urlpath, dataObj, method, ensure_status=ensure_status)
        return result

    def http_get_result(self, urlpath, ensure_status=[200]):
        return self.request_result(urlpath, None, 'GET', ensure_status=ensure_status)

    def http_post_result(self, urlpath, dataObj, ensure_status=[200]):
        return self.request_result(urlpath, dataObj, 'POST', ensure_status=ensure_status)

    #
    # -- Wait methods --
    #

    def wait_ready(self, model_name, uuids, delay=5.0, tries=0):
        """
        Block until all given `uuids` are ready, pausing `delay` before each check.
        If `tries` > 0, raise a RuntimeError after that many attempts.
        """
        if not uuids: return
        pending_uuids = list(uuids)
        i = 0
        while True:
            time.sleep(delay)
            i += 1
            logging.debug(f"Checking ready ({i}/{tries}) for {model_name} uuids: {repr(pending_uuids)}")
            for uuid in pending_uuids:
                result = self.http_get_result(f'/{model_name}/read/{uuid}', ensure_status=[200])
                assert type(result["ready"]) == bool
                if result["ready"]:
                    pending_uuids.remove(uuid)
            if not pending_uuids:
                logging.debug(f"Done waiting for ready")
                return
            if i == tries: break
        raise RuntimeError(f"{model_name} {repr(pending_uuids)} never became ready")

    def wait_deleted(self, model_name, uuids, delay=5.0, tries=0):
        """
        Block until all given `uuids` are deleted, pausing `delay` before each check.
        If `tries` > 0, raise a RuntimeError after that many attempts.
        """
        if not uuids: return
        pending_uuids = list(uuids)
        i = 0
        while True:
            time.sleep(delay)
            i += 1
            logging.debug(f"Checking deleted ({i}/{tries}) for {model_name} uuids: {repr(pending_uuids)}")
            for uuid in pending_uuids:
                resp, result = self.request(f'{model_name}/read/{uuid}', None, "GET", ensure_status=[200, 404])
                if resp.status_code == 404:
                    pending_uuids.remove(uuid)
            if not pending_uuids:
                logging.debug(f"Done waiting for deletion")
                return
            if i == tries: break
        raise RuntimeError(f"{model_name} {repr(pending_uuids)} never became deleted")

    #
    # -- Convenience methods --
    #

    def get_current_server(self, embed=[]):
        """
        Get the current server from which this is being executed.
        Returns None if not being run from an Opalstack webserver.
        """
        return filt_one_or_none(self.servers.list_all(embed)['web_servers'], {
            'hostname': socket.gethostname(),
        })

    def get_current_osuser(self, embed=['server']):
        """
        Get the current osuser from which this is being executed.
        Returns None if not being run from an Opalstack webserver.
        """
        if 'server' in embed:
            return filt_one_or_none(self.osusers.list_all(embed=embed), {
                'name': os.environ.get('USER'),
                'server.hostname': socket.gethostname(),
            })
        else:
            server = self.get_current_web_server(embed)
            if not server: return None
            return filt_one_or_none(self.osusers.list_all(embed=embed), {
                'name': os.environ.get('USER'),
                'server': self.get_current_web_server(embed)['id'],
            })
