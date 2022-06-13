#!/usr/bin/env python3

import sys, os
import logging.config
import argparse

import opalstack
opalapi = opalstack.Api(token='0000000000000000000000000000000000000000')

from opalstack.util import run, filt_one

SRC_APP_NAME            = 'myapp'               # The application files to clone (~/apps/myapp).

DST_WEB_SERVER_HOSTNAME = 'vps1.opalstack.com'  # The webserver to clone to. May be the same as source webserver.
DST_DOMAIN_NAME         = 'www.mynewsite.com'   # The domain to create. Will host the cloned site.
DST_OSUSER_NAME         = 'mynewuser'           # The osuser (shell user) to which the source app will be cloned.
DST_OSUSER_PASS         = None                  # The osuser password if the user already exists. If None, the osuser will be created instead.
DST_APP_NAME            = 'mynewapp'            # The new app name cloned on the destination server (~/apps/mynewapp). May be the same as the source app name.
DST_SITE_NAME           = 'mynewsite'           # The new site name to create (visible in the dashboard). Often the same as DST_APP_NAME.
DST_SITE_HTTPS          = False                 # Whether or not to enable HTTPS and generate an SSL certificate. Can also be enabled on the site in the dashboard later.

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

def get_args():
    parser = argparse.ArgumentParser(description='Wordpress Site Cloner')
    return parser.parse_args(sys.argv[1:])

def main(args):
    # Set some derived variables
    userhost = f'{DST_OSUSER_NAME}@{DST_WEB_SERVER_HOSTNAME}'
    src_app_path = os.path.expanduser(f'~/apps/{SRC_APP_NAME}')
    dst_app_path = f'/home/{DST_OSUSER_NAME}/apps/{DST_APP_NAME}'

    proto = 'https' if DST_SITE_HTTPS else 'http'
    site_url = f'{proto}://{DST_DOMAIN_NAME}/'

    ssh_password_filepath = f'{DST_OSUSER_NAME}.sshpass'

    sqlpasswd_filepath_local = os.path.expanduser(f'~/{DST_APP_NAME}.sqlpasswd')
    sqlpasswd_filepath_remote = f'/home/{DST_OSUSER_NAME}/{DST_APP_NAME}.sqlpasswd'

    sql_filepath_local = os.path.expanduser(f'~/{DST_APP_NAME}.sql')
    sql_filepath_remote = f'/home/{DST_OSUSER_NAME}/{DST_APP_NAME}.sql'

    # Retrieve web_server and primary IP entries for later use
    log.info(f'Retrieving webserver information for {DST_WEB_SERVER_HOSTNAME}')
    web_server = filt_one(
        opalapi.servers.list_all()['web_servers'], {'hostname': DST_WEB_SERVER_HOSTNAME},
    )
    webserver_primary_ip = filt_one(
        opalapi.ips.list_all(embed=['server']), {'server.hostname': web_server['hostname'], 'primary': True},
    )

    # Either retrieve or create destination osuser, depending on whether or not a password was specified.
    if DST_OSUSER_PASS:
        log.info(f'Retrieving existing osuser {DST_OSUSER_NAME}')
        dst_osuser = filt_one(
            opalapi.osusers.list_all(), {'name': DST_OSUSER_NAME, 'server': web_server['id']},
        )
        ssh_password = DST_OSUSER_PASS

    else:
        log.info(f'Creating new osuser {DST_OSUSER_NAME}')
        dst_osuser = opalapi.osusers.create_one({
            'name':  DST_OSUSER_NAME,
            'server': web_server['id'],
        })
        ssh_password = dst_osuser['default_password']

    sshrunner = opalstack.util.SshRunner(userhost, ssh_password=ssh_password, ssh_password_filepath=ssh_password_filepath)
    sshrunner.run_passbased_ssh('/bin/true')

    # Create domain
    log.info(f'Creating domain {DST_DOMAIN_NAME}')
    created_domain = opalapi.domains.create_one({
        'name': DST_DOMAIN_NAME,
    })

    # Create app
    log.info(f'Creating application {DST_APP_NAME}')
    created_app = opalapi.apps.create_one({
        'name': DST_APP_NAME,
        'osuser': dst_osuser['id'],
        'type': 'APA',
        'installer_url': 'https://raw.githubusercontent.com/opalstack/installers/master/core/wordpress/install.sh'
    })

    # Create site
    log.info(f'Creating site {DST_SITE_NAME}')
    created_site = opalapi.sites.create_one({
        'name': DST_SITE_NAME,
        'ip4': webserver_primary_ip['id'],
        'domains': [created_domain['id']],
        'routes': [{'app': created_app['id'], 'uri': '/'}],
        'generate_le': DST_SITE_HTTPS,
        'redirect': DST_SITE_HTTPS,
    })

    # Clone data
    log.info(f'Retrieving database configurations')
    src_db_host, _, _ = run(f'~/bin/wp --path={src_app_path} config get DB_HOST')
    src_db_user, _, _ = run(f'~/bin/wp --path={src_app_path} config get DB_USER')
    src_db_pass, _, _ = run(f'~/bin/wp --path={src_app_path} config get DB_PASSWORD')
    src_db_name, _, _ = run(f'~/bin/wp --path={src_app_path} config get DB_NAME')
    assert src_db_host and src_db_user and src_db_pass and src_db_name

    dst_db_host, _, _ = sshrunner.run_passbased_ssh(f'/home/{DST_OSUSER_NAME}/bin/wp --path={dst_app_path} config get DB_HOST')
    dst_db_user, _, _ = sshrunner.run_passbased_ssh(f'/home/{DST_OSUSER_NAME}/bin/wp --path={dst_app_path} config get DB_USER')
    dst_db_pass, _, _ = sshrunner.run_passbased_ssh(f'/home/{DST_OSUSER_NAME}/bin/wp --path={dst_app_path} config get DB_PASSWORD')
    dst_db_name, _, _ = sshrunner.run_passbased_ssh(f'/home/{DST_OSUSER_NAME}/bin/wp --path={dst_app_path} config get DB_NAME')
    assert dst_db_host and dst_db_user and dst_db_pass and dst_db_name

    mariatool_local = opalstack.util.MariaTool(src_db_host, 3306, src_db_user, src_db_pass, src_db_name, sqlpasswd_filepath_local)
    mariatool_remote = opalstack.util.MariaTool(dst_db_host, 3306, dst_db_user, dst_db_pass, dst_db_name, sqlpasswd_filepath_local, sqlpasswd_filepath_remote)

    log.info(f'Exporting database')
    mariatool_local.export_local_db(sql_filepath_local)

    log.info(f'Copying files')
    sshrunner.run_passbased_rsync(f'{src_app_path}/', f'{userhost}:{dst_app_path}/')

    log.info(f'Copying database content')
    sshrunner.run_passbased_scp(sql_filepath_local, f'{userhost}:')
    os.remove(sql_filepath_local)

    log.info(f'Importing database')
    mariatool_remote.import_remote_db(sshrunner, sql_filepath_remote)
    sshrunner.run_passbased_ssh(f'rm {sql_filepath_remote}')

    log.info(f'Updating site url')
    sshrunner.run_passbased_ssh(f'/home/{DST_OSUSER_NAME}/bin/wp --path={dst_app_path} option set siteurl {site_url}')
    sshrunner.run_passbased_ssh(f'/home/{DST_OSUSER_NAME}/bin/wp --path={dst_app_path} option set home {site_url}')

    if DST_SITE_HTTPS:
        log.info(f'Site cloned: {site_url} (Note: Please allow a few minutes for an SSL certificate to be generated.)')
    else:
        log.info(f'Site cloned: {site_url}')

if __name__ == '__main__':
    args = get_args()
    main(args)
