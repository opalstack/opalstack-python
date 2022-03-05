import pytest
from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

EXAMPLE_CERT = """
-----BEGIN CERTIFICATE-----
MIIFXTCCA0WgAwIBAgIUKnO9UZsgu2KJqR+aJk/tNpd7EgQwDQYJKoZIhvcNAQEL
BQAwRzELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkFaMRIwEAYDVQQKDAlFeGFtcGxl
Q0ExFzAVBgNVBAMMDmV4YW1wbGUtY2EuY29tMB4XDTIyMDMxMTE4MjE1M1oXDTMy
MDMwODE4MjE1M1owTzELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkFaMRYwFAYDVQQK
DA1FeGFtcGxlU2VydmVyMRswGQYDVQQDDBJleGFtcGxlLXNlcnZlci5jb20wggIi
MA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDPgd1drnvW6YEMOmPjtE9CpxAG
m/jQJQ91hO6vBLN3EDkI6MtCX/NyQAnJhOnCfU9cT/rGdGOMcZ+Ojm9GoZX9G6Ya
NgC+21m3t2k20+yUafrrYaMEK3w5qbTIRuly5kTSkKKs+LSoCQDBYqUanhO1Q9XV
KFgtDhXzAKlo5llBjVuJNRjtgICr26zy3MeJiBCU8cKWsMrXBOM4n2M6S611CMKA
vWU4ThWaZ9sUQ/pc+1J1a2jtgbizLbpwWS8sGcSwPtGzvadmnTq4/dRFumCWSPse
WrXekrF1YbICTfswnmfj3elHttrpMmgPXjZZ80FTPjUzFk8EG8dBLOZD6SFn8ZC3
Tj8+2YQHTFQfWUb64riYZxQ6UwuYxLFjFTg3S9e11YSZSm6jfE8CoYHCdUHclOG8
dZ6GY3jd0LAg8lh7HXr5jRfF0aBo1ZnxfFgPoj6USCMRJtLE8ocn0yWdCCDJFcS8
XRsRhiLGYelsK0tsYCvpkCSYQfpix0VYRUK5no3wCWNjHWbKy+M2aiaM0LK8mG1z
ua6unP0sAEKHXVg4nUeBDH0UppRYVdAfkqH1TTR1So4ScSZ+HuKUH6iJkQWIv9IZ
TxRMAPK/M5AbNuBRuO88CdkFai43+oUrsK2CwdhTy2kjx/Le5VYQSKT/zyEZKHo4
ECea+cJ+brw1UAMtgQIDAQABozkwNzA1BgNVHREELjAsghJleGFtcGxlLXNlcnZl
ci5jb22CFnd3dy5leGFtcGxlLXNlcnZlci5jb20wDQYJKoZIhvcNAQELBQADggIB
ABfg1LYfEux+4ksF2/HBnYMBTq9MBqnp5IYWC3qc12EaC9/km65WZcgV5umqp3iQ
OZgwKmqRVcdIxW8wVzpPukfb2SOYiTcvYAEqwKcleLKVMCp8Z3KogGMvmdR+ly3Y
Zysnr7U38ZDfQgcNHev3ToX0Uj0F7sF9lMB2+YJAWRixJtSYysj/okEbNFf5ZqgU
mq0/meakAO4StiBRK2Sd+bpyDMkwhGvvfzzOU7PVI2j/c8yZ5aNXfsrfwlo+iM4i
CkFL43CnZD+JqU7Vcyrcx4qgp9dQwdWOVpH1ZhWJHnEMSejjkPG8oNj2XddtRRHs
X0W5oyRhbKy7kWRIOOPYQKOe1Uzcyd04bbpBST1twNwPoWO6qVaMtk0vp1rqZM7R
goCnA5Xo93t2oaXLt17lZClOvIXxSvD1pGNrHwt36q3wbc3zg4QRhTYZvX+u2H3o
I3mFKmjj5GQq3oSOzBRxQpTVj3JdWK/4cyTDANfYSRqlCkY2TuJjzOIKHHE6GRQi
eGorcaHf5baVMf8QHyNtbaXrsIPPR69opZuQ/9WB5LN1QWCATws9M1v6QgGjyl9f
tyVkPxgkcwG+YLCoWjU23s2JAtvAWjY/OMDxk9vS2ApfUrDjbk3EiSgkglcYuRPv
Ts3RCKgadKdm7RNaDUasFDGifc7zkVLfVPgTK/lsxrLa
-----END CERTIFICATE-----
""".strip()

EXAMPLE_INTERMEDIATES = """
-----BEGIN CERTIFICATE-----
MIIFbzCCA1egAwIBAgIUV0SKbvX1Y79/YnptMomrJcc82KEwDQYJKoZIhvcNAQEL
BQAwRzELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkFaMRIwEAYDVQQKDAlFeGFtcGxl
Q0ExFzAVBgNVBAMMDmV4YW1wbGUtY2EuY29tMB4XDTIyMDMxMTE4MjEyMloXDTMy
MDMwODE4MjEyMlowRzELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkFaMRIwEAYDVQQK
DAlFeGFtcGxlQ0ExFzAVBgNVBAMMDmV4YW1wbGUtY2EuY29tMIICIjANBgkqhkiG
9w0BAQEFAAOCAg8AMIICCgKCAgEAqG+CgIpmERwRKh1SDV9pb6MKBEjieA9qGVQP
pxEIhUd/u3rqOBgL6JEkmD0iIxVe661CFA30mBVDCmVkxtt03TtNnZseHbF7kqeV
yt53qlWJgmundYIb2euGnSdFpXV6dIC3+L7fiTguTSVX46yTOhehsOjMnQ0hxRwc
raf8/Bdnzh/yDDxiPC/UEUVj9TTnlFXMI67Ojg4HOjGHn93lkfjmGz8RFw1N1GzD
PVwjJwraMBDUQnKh5p+mREv+NrWzp46Se4P908//RlmW6cs+Wq3E1vsUZFDyVaaI
VqJVFjISwNAzCFCOqDQIg5lEDJQKXBBfmEYHYTH8IzSLbSg1gI94foEdkYmKI1qL
x0kQ8pH9yD07ZSUhNDxeKYnAj/O8aYqeVYAdcr6GdsNnUA17+sXOEmls+MjlsHFM
sH5/nkFP/ubmV0pfj95M6qQ4w7Rndm09CUzYryYhUPWAki0Ev+dqAoVfk31iLweT
nC/fzvTcxKgq54fnjx6/OFtQwOTcgpbHri+FK7SyFMNTwcN/m9iZNtgtkDi6rErk
3sflKyHTAunp8wC1kRD4TRAUmVXRWQsknjxpT8qTlWxxLtcUOFVUoAhsEiBtaEtf
4bLFScgCPjyt0vnXquIHhVE90VqGeqcIhw7XgurOe/U8j18YwGgpeAd3/sw6WkyS
/cdQYKUCAwEAAaNTMFEwHQYDVR0OBBYEFI106feVIeiTH5TPCTw5O+quexZSMB8G
A1UdIwQYMBaAFI106feVIeiTH5TPCTw5O+quexZSMA8GA1UdEwEB/wQFMAMBAf8w
DQYJKoZIhvcNAQELBQADggIBAB4Sfj6tZEXW6mOq8/5/CFo0yfkqhrER2MBPUlAz
UWSl617GYFI/jEJZWuom//5Mjqop9khMQVomBsj7/lU8zDUb/GBCKwhqqVPG00Cc
ZDUqYK05wuriyiy1C7lAyk0BD8No9mcYx6fRJJuPlDScaGlRir/7eggH62+plhTd
bskT+6DKoV5k/y74dMXVqqQUE5yEcR6vKm58Kjtkpd5w9i6R38GhJvB6L2PHEVXe
kbEDFwn9g3Vpa43H7Af68woeTZbvjAmVKtj8AueJZfUaEHX5+kUwlgIqx36BD5Sz
Xamx14jHgw4xzhZSmBY7KPJ82mnRBx058tbNbyEUpoAG8xQ8fdTqQhRllMq38dmN
3AuLbL8yhkE5xcpOearpa9mEa1w2DpTfouxPDzPcq6msG7SL9gWxNqkJRrygEG8I
o8tUoy4ZyDjiO15T0wEZb0PuB5JVi9+ceYMIXPfSQF32MW2w03Xuapv4NPD/H/Ac
OmUNuQUpxQm32T/6t1qwhUWbrM9UFS5e7SG/OcjBGz6SnmuUW003ipHfMAAPkZV3
c4yRCfrDnfJ3qG8MXk96DXEi3H/V7Ty3X2AtlR6S+5Q/Q8Xozx4Jw/59m7EF7Bsp
gp5J3EKSeTZChZqukVC12IV5kKQcK8hv6+QjpXYXTnTT9xN0jYAnU+s05E5IwKi/
Z6ir
-----END CERTIFICATE-----
""".strip()

EXAMPLE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
""".strip()

def test_certs():
    # -- Create certs --
    #
    # Create new certs.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_certs = opalapi.certs.create([
        { 'name': f'test-cert-{RANDID}',
          'cert': EXAMPLE_CERT,
          'intermediates': EXAMPLE_INTERMEDIATES,
          'key': EXAMPLE_KEY,
        },
    ])
    created_cert = created_certs[0]
    created_cert_id = created_cert['id']
    created_cert_name = created_cert['name']
    print(f'Created cert {created_cert_name}')

    assert created_cert['name'] == f'test-cert-{RANDID}'
    assert created_cert['cert'] == EXAMPLE_CERT
    assert created_cert['intermediates'] == EXAMPLE_INTERMEDIATES
    assert created_cert['key'] == EXAMPLE_KEY

    # -- List certs --
    #
    # Retrieve all existing certs.
    #
    for cert in opalapi.certs.list_all():
        cert_id = cert['id']
        cert_name = cert['name']
        print(f'Listed cert {cert_id} (name: {cert_name})')

    # -- Read single cert --
    #
    # Retrieve one existing cert by id.
    #
    cert = opalapi.certs.read(cert_id)
    print(f'Read cert by id: {cert_id}')

    assert cert['id'] == cert_id

    # -- Update certs --
    #
    # Change the name or cert/intermediates/key text for existing cert.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_certs = opalapi.certs.update([
        {'id': created_cert_id, 'name': f'test-updated-cert-{RANDID}'},
    ])
    updated_cert = updated_certs[0]
    print(f'Updated cert name')

    assert updated_cert['id'] == created_cert_id
    assert updated_cert['name'] == f'test-updated-cert-{RANDID}'

    # -- Delete certs --
    #
    # Delete existing certs by id.
    # Takes a list of items to delete.
    #
    opalapi.certs.delete([
        {'id': created_cert_id},
    ])
    print(f'Deleted cert with id {created_cert_id}')

    assert not any(cert['id'] == created_cert_id for cert in opalapi.certs.list_all())
