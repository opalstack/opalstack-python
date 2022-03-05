from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

def test_tokens():
    # -- Create tokens --
    #
    # Create new tokens.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_tokens = opalapi.tokens.create([
        {'name': 'opalstack_library_test_token'},
    ])
    created_token = created_tokens[0]
    created_token_key = created_token['key']
    print(f'Created token named "opalstack_library_test_token" with key {created_token_key}')

    assert created_token['name'] == 'opalstack_library_test_token'

    # -- List tokens --
    #
    # Retrieve all existing tokens.
    #
    for token in opalapi.tokens.list_all():
        token_name = token['name']
        token_key = token['key']
        print(f'Listed token {token_name} with associated api key {token_key}')

    # -- Read single token --
    #
    # Retrieve one existing token by key.
    #
    token = opalapi.tokens.read(token_key)
    print(f'Read token by key: {token_key}')

    assert token['key'] == token_key

    # -- Update tokens --
    #
    # Change the name of existing tokens.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_tokens = opalapi.tokens.update([
        {'key': created_token_key, 'name': 'opalstack_library_renamed_token'},
    ])
    updated_token = updated_tokens[0]
    updated_token_name = updated_token['name']
    print(f'Updated token "opalstack_library_test_token" and renamed it to "{updated_token_name}"')

    assert updated_token['name'] == 'opalstack_library_renamed_token'
    assert updated_token['key'] == created_token_key

    # -- Delete tokens --
    #
    # Delete existing tokens by key.
    # Takes a list of items to delete.
    #
    opalapi.tokens.delete([
        {'key': created_token_key},
    ])
    print(f'Deleted token with key {created_token_key}')

    assert not any(token['key'] == created_token_key for token in opalapi.tokens.list_all())
