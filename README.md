# Opalstack API Library

This is the official Python wrapper for the [Opalstack API](https://my.opalstack.com/api/v1/doc/).

The **opalstack** library is designed to streamline common CRUD *(Create/Read/Update/Delete)* operations. By default, all methods wait for objects to become ready or deleted before returning, allowing you to interact synchronously with a fundamentally asynchronous API.

This library is maintained in tandem with the Opalstack API. This way, your code is able to preserve compatibility with future API changes by simply updating the library instead of having to make additional changes to your code (we hope!).

## Installation

These examples assume that you have an active [Opalstack](https://www.opalstack.com/ "Opalstack") account. If you don't, then give it a try with our 14-day free trial. We think you'll like what you see.

Once logged in, obtain your API token from https://my.opalstack.com/tokens/ .

Then, to install the **opalstack** library using **pypi**:
```bash
pip3 install opalstack
```

This is a pure-python library, so if you just want to try without installing, you can do:
```bash
mkdir -p $HOME/src
cd $HOME/src
git clone 'https://github.com/opalstack/opalstack-python.git'
export PYTHONPATH="$PYTHONPATH:$HOME/src/opalstack-python/src"
python3 -c 'import opalstack'
```
Note that the library does depend on [requests](https://pypi.org/project/requests/ "requests"), so you will need to install that first.

The library is [MIT-licensed](https://github.com/opalstack/opalstack-python/blob/master/LICENSE "MIT-licensed"), so feel free to embed it in your project if needed.
## Examples

#### List web servers
```python
import opalstack
opalapi = opalstack.Api(token='0123456789abcdef0123456789abcdef01234567')

# List all web servers on the account.
#
web_servers = opalapi.servers.list_all()['web_servers']

from pprint import pprint
pprint(web_servers)


# Get UUID of web server on the account with hostname 'opal1.opalstack.com'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
#
web_server = [
    web_server
    for web_server in opalapi.servers.list_all()['web_servers']
    if web_server['hostname'] == 'opal1.opalstack.com'
][0]
print(web_server)

# A cleaner way to do this makes use of the filt or filt_one utility functions from opalstack.util
#
# >>> help(filt)
#
# filt(items, keymap, sep='.')
#     Filters a list of dicts by given keymap.
#     By default, periods represent nesting (configurable by passing `sep`).
#
#     For example:
#         items = [
#             {'name': 'foo', 'server': {'id': 1234, 'hostname': 'host1'}, 'loc': 4},
#             {'name': 'bar', 'server': {'id': 2345, 'hostname': 'host2'}, 'loc': 3},
#             {'name': 'baz', 'server': {'id': 3456, 'hostname': 'host3'}, 'loc': 4},
#         ]
#         filt(items, {'loc': 4})                                   # Returns [foo, baz]
#         filt(items, {'loc': 4, 'server.hostname': 'host1'})       # Returns [foo]
#         filt(items, {'name': 'bar', 'server.hostname': 'host2'})  # Returns [bar]
#         filt(items, {'name': 'bar', 'server.hostname': 'host3'})  # Returns []
#
# filt_one() is like filt(), but returns a single unique result instead of a list.
#
from opalstack.util import filt, filt_one
web_server = filt_one(opalapi.servers.list_all()['web_servers'], {'hostname': 'opal1.opalstack.com'})
print(web_server)
```

#### Create OSUser (Shell User)
```python
import opalstack
from opalstack.util import filt, filt_one
opalapi = opalstack.Api(token='0123456789abcdef0123456789abcdef01234567')

# Choose the server to create on. This example uses 'opal1.opalstack.com'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
#
web_server = filt_one(opalapi.servers.list_all()['web_servers'], {'hostname': 'opal1.opalstack.com'})

osusers_to_create = [{
    'name':  'mytestuser1234',
    'server': web_server['id'],
}]
created_osusers = opalapi.osusers.create(osusers_to_create)
created_osuser = created_osusers[0]

print(created_osuser['id'])
print(created_osuser['name'])
print(created_osuser['default_password'])
```

#### List OSUsers (Shell Users)
```python
import opalstack
from opalstack.util import filt, filt_one
opalapi = opalstack.Api(token='0123456789abcdef0123456789abcdef01234567')

# Get all existing osusers.
#
osusers = opalapi.osusers.list_all()
pprint(osusers)

first_osuser = osusers[0]
pprint(first_osuser['server'])


# Get all existing osusers, but embed the 'server' field with a dict instead of a UUID.
#
osusers = opalapi.osusers.list_all(embed=['server'])
pprint(osusers)

first_osuser = osusers[0]
pprint(first_osuser['server'])


# Retrieve one OSUser by UUID
#
osuser_id = first_osuser['id']
retrieved_osuser = opalapi.osusers.read(osuser_id)
pprint(retrieved_osuser)


# Retrieve one OSUser by UUID, embedding 'server' dict
#
osuser_id = first_osuser['id']
retrieved_osuser = opalapi.osusers.read(osuser_id, embed=['server'])
pprint(retrieved_osuser)


# Get all existing osusers which are on server 'opal1.opalstack.com'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
#
osusers = filt(opalapi.osusers.list_all(embed=['server']), {'server.hostname': 'opal1.opalstack.com'})
pprint(osusers)


# Get one osuser on server 'opal1.opalstack.com' named 'mytestuser1234'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
# Be sure to replace 'mytestuser1234' with the name of an osuser you have.
#
osuser = filt_one(opalapi.osusers.list_all(embed=['server']), {'server.hostname': 'opal1.opalstack.com', 'name': 'mytestuser1234'})
pprint(osuser)
```

#### Delete OSUsers (Shell Users)
```python
import opalstack
from opalstack.util import one, filt, filt_one
opalapi = opalstack.Api(token='0123456789abcdef0123456789abcdef01234567')

# Delete the osuser on server 'opal1.opalstack.com' named 'mytestuser1234'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
# Be sure to replace 'mytestuser1234' with the name of an osuser you want to delete.
#
osuser = filt_one(opalapi.osusers.list_all(embed=['server']), {'server.hostname': 'opal1.opalstack.com', 'name': 'mytestuser1234'})
osusers_to_delete = [osuser]
opalapi.osusers.delete(osusers_to_delete)
```


#### Create, Update, and Delete a Domain, OSUSer, App, and Site
```python
import opalstack
from opalstack.util import filt, filt_one
opalapi = opalstack.Api(token='0123456789abcdef0123456789abcdef01234567')

# Retrieve the "opalstacked" gift domain.
# Be sure to replace 'myusername' with your account username.
#
opalstacked_domain = filt_one(opalapi.domains.list_all(), {'name': 'myusername.opalstacked.com'})
pprint(opalstacked_domain)


# Create a new "mytestdomain" subdomain under the opalstacked gift domain.
# Be sure to replace 'mytestdomain' with the name of a subdomain you want to create.
#
# This also demonstrates the opalstack.util one() function:
#
# That is, this:
#     created_domain = one(opalapi.domains.create(domains_to_create))
#
# Is equivalent to:
#     created_domains = opalapi.domains.create(domains_to_create)
#     assert len(created_domains) == 1
#     created_domain = created_domains[0]
#
opalstacked_domain_name = opalstacked_domain['name']
testdomain_name = f'mytestdomain.{opalstacked_domain_name}'
domains_to_create = [{
    'name': f'mytestdomain.{opalstacked_domain_name}',
}]
created_domain = one(opalapi.domains.create(domains_to_create))


# Choose the server to create on. This example uses 'opal1.opalstack.com'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
#
web_server = filt_one(opalapi.servers.list_all()['web_servers'], {'hostname': 'opal1.opalstack.com'})


# Create a new 'mytestuser2345' osuser on the chosen web server.
# Be sure to replace 'mytestuser2345' with the name of an osuser you want to create.
#
osusers_to_create = [{
    'name':  'mytestuser2345',
    'server': web_server['id'],
}]
created_osuser = one(opalapi.osusers.create(osusers_to_create))


# Create a new 'mytestwp' Wordpress app under the created osuser.
# Be sure to replace 'mytestwp' with the name of an app you want to create.
#
# The App type represents the underlying type of the application:
#   'STA': Static Only
#   'NPF': Nginx/PHP-FPM
#   'APA': Apache/PHP-CGI
#   'CUS': Proxied port
#   'SLS': Symbolic link, Static only
#   'SLP': Symbolic link, Apache/PHP-CGI
#   'SLN': Symbolic link, Nginx/PHP-FPM
#   'SVN': Subversion
#   'DAV': WebDAV
#
# The 'installer_url' points to an install script,
# usually the raw content of a script somewhere under https://github.com/opalstack/installers.
# The field is optional (omit to create an empty app).
#
apps_to_create = [{
    'name': 'mytestwp',
    'osuser': created_osuser['id'],
    'type': 'APA',
    'installer_url': 'https://raw.githubusercontent.com/opalstack/installers/master/core/wordpress/install.sh'
}]
created_app = one(opalapi.apps.create(apps_to_create))


# Create a new 'mytestsite' site to mount the created app onto the created domain.
# Be sure to replace 'mytestsite' with the name of a site you want to create.
#
# In order to create a site, we first need to choose the IP address to use.
# This is because a server may have multiple IPs.
#
# We will use the primary IP address for server 'opal1.opalstacked.com'.
# Be sure to replace 'opal1.opalstack.com' with the hostname of a server you have access to.
#
webserver_primary_ip = filt_one(
    opalapi.ips.list_all(embed=['server']), {'server.hostname': 'opal1.opalstack.com', 'primary': True}
)

sites_to_create = [{
    'name': 'mytestsite',
    'ip4': webserver_primary_ip['id'],
    'domains': [created_domain['id']],
    'routes': [{'app': created_app['id'], 'uri': '/'}],
}]
created_site = one(opalapi.sites.create(sites_to_create))


# Wait a couple of minutes for everything to take effect.
# Trying too soon could cause an invalid DNS cache, which will take longer to refresh.
#
import time
time.sleep(120.0)

import requests
url = f'http://{created_domain["name"]}/'
resp = requests.get(url)
assert resp.status_code == 200
assert 'wordpress' in str(resp.content).lower()
print(f'Assuming there were no AsserionErrors, your site is now live at {url}')


# Update the created site, renaming it to 'mytestsite2'
#
# Only provided fields are updated. Omitted fields remain as-is.
#
sites_to_update = [{
    'id': created_site['id'],
    'name': 'mytestsite2',
}]
updated_site = one(opalapi.sites.update(sites_to_update))


# Delete the created site, app, osuser, and domain
#
opalapi.sites.delete([created_site])
opalapi.apps.delete([created_app])
opalapi.osusers.delete([created_osuser])
opalapi.domains.delete([created_domain])
```
