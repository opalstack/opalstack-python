#!/usr/bin/env python3

import sys, os
import logging.config
import argparse

import opalstack
opalapi = opalstack.Api(token='0000000000000000000000000000000000000000')

from opalstack.util import filt_one, filt_one_or_none

MAILUSER_PREFIX = 'myservice'  # All created mailusers will be prefixed by this string
                               # (typically your user, service, or website name)
                               # This is to prevent name conflicts.

IMAP_SERVER_HOSTNAME = 'imap1.us.opalstack.com'  # The IMAP server on which to create the mailuser.

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

def get_or_create_mailuser(imap_server, mailuser_name):
    mailuser = filt_one_or_none(
        opalapi.mailusers.list_all(), {
            'name': mailuser_name,
            'imap_server': imap_server['id'],
        },
    )
    if not mailuser:
        log.info(f'creating mailuser {mailuser_name}')
        mailuser = opalapi.mailusers.create_one({
            'name': mailuser_name,
            'imap_server': imap_server['id'],
        })
        assert mailuser
    return mailuser

def get_args():
    parser = argparse.ArgumentParser(description='Mailbox Generator')
    parser.add_argument('address', help='Email address to create')
    return parser.parse_args(sys.argv[1:])

def main(args):
    email_address = args.address
    if email_address.count('@') != 1:
        raise ValueError(f'provided email address invalid: {email_address}')
    user_part, domain_name = email_address.split('@')
    mailuser_name = f'{MAILUSER_PREFIX}_{user_part}'

    log.info(f'Retrieving imap server information for {IMAP_SERVER_HOSTNAME}')
    imap_server = filt_one(
        opalapi.servers.list_all()['imap_servers'], {'hostname': IMAP_SERVER_HOSTNAME},
    )

    # Create the address if it doesn't exist.
    # If it does exist, then ensure it delivers mail to our required mailuser.
    domain = get_or_create_domain(domain_name)
    mailuser = get_or_create_mailuser(imap_server, mailuser_name)
    address = filt_one_or_none(
        opalapi.addresses.list_all(), {'source': email_address},
    )
    if address:
        if mailuser['id'] not in address['destinations']:
            log.info(f'Updating address {email_address}')
            opalapi.addresses.update_one({
                'id': address['id'],
                'destinations': address['destinations'] + [mailuser['id']],
            })
    else:
        log.info(f'Creating address {email_address}')
        opalapi.addresses.create_one({
            'source': email_address,
            'destinations': [mailuser['id']],
            'forwards': [],
        })

if __name__ == '__main__':
    args = get_args()
    main(args)
