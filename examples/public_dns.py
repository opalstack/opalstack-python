#!/usr/bin/env python3

import sys, os
import logging.config
import argparse
import requests

import opalstack
opalapi = opalstack.Api(token='0000000000000000000000000000000000000000')

from opalstack.util import filt_one_or_none

DOMAIN_NAME = 'ip.mydomain.com'  # The domain whose A record to update to our public IP.

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s : %(levelname)-5s : %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'standard',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'opalstack': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        '__main__': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
})
log = logging.getLogger(__name__)

def get_or_create_domain(domain_name):
    domain = filt_one_or_none(
        opalapi.domains.list_all(), {'name': domain_name},
    )
    if not domain:
        log.info(f'creating domain {domain_name}')
        domain = opalapi.domains.create_one({'name': domain_name})
        assert domain
    return domain

def dnsrecord_exists(domain, record_type, record_content):
    for dnsrecord in opalapi.dnsrecords.list_all():
        if ( dnsrecord['domain'] == domain['id'] and
             dnsrecord['type'] == record_type and
             dnsrecord['content'] == record_content ): return True
    return False

def get_args():
    parser = argparse.ArgumentParser(description='Public DNS Updater')
    return parser.parse_args(sys.argv[1:])

def main(args):
    domain = get_or_create_domain(DOMAIN_NAME)

    req = requests.get('http://ifconfig.me/')
    if req.status_code != 200:
        log.warn('failed to retrieve public ip address')
        return

    ip_address = req.content.decode()
    if dnsrecord_exists(domain, 'A', ip_address):
        log.debug('nothing to do')
        return

    log.info(f'updating {DOMAIN_NAME} A record to {ip_address}')
    opalapi.dnsrecords.create_one({
        'domain': domain['id'],
        'type': 'A',
        'content': ip_address,
    })

if __name__ == '__main__':
    args = get_args()
    main(args)
