from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

def test_accounts():
    # -- Account info --
    #
    # Retrieve information about:
    #  * Account contact
    #  * Payment processing
    #  * Server types
    #  * Quota usage
    #
    # Returns a list for consistency with other API endpoints,
    # but the list only contains one account item.
    #
    account = opalapi.accounts.list_all()[0]
    account_email = account['email']
    account_payment_processor = account['payment_processor']
    account_web_server_count = len(account['web_servers'])
    print(f'Account has {account_web_server_count} web server(s), contact email "{account_email}", and uses payment processor "{account_payment_processor}"')

    for webserver_id in account['usage_data']['webservers']:
        webserver_hostname = account['usage_data']['webservers'][webserver_id]['hostname']
        disk_used_mb = account['usage_data']['webservers'][webserver_id]['disk_used']
        disk_total_mb = account['usage_data']['webservers'][webserver_id]['disk_total']
        rss_used_mb = account['usage_data']['webservers'][webserver_id]['rss_used']
        rss_total_mb = account['usage_data']['webservers'][webserver_id]['rss_total']
        print(f'Used {disk_used_mb:0.1f} out of {disk_total_mb:0.0f} MB disk space and {rss_used_mb:0.1f} out of {rss_total_mb:0.0f} MB rss on {webserver_hostname}')

    # Use embed to include more information about imap_servers.
    #   Without the embed, account['imap_servers'] would contain a list of uuids.
    #   By adding embed=['imap_servers'], it is a list of dicts instead.
    account = opalapi.accounts.list_all(embed=['imap_servers'])[0]
    for imap_server in account['imap_servers']:
        imap_server_hostname = imap_server['hostname']
        print(f'Available IMAP server: {imap_server_hostname}')
