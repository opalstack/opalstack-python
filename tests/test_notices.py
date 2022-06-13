from testutil import *

import opalstack
opalapi = opalstack.Api(APIKEY)

def test_notices():
    # -- Create notices --
    #
    # Create new notices.
    # Takes a list of items to create and returns a list of the created items.
    #
    created_notices = opalapi.notices.create([
        {'type': 'M', 'content': 'Hello from the API!'},
    ])
    created_notice = created_notices[0]
    created_notice_id = created_notice['id']
    print(f'Created a Message-type notice with content "Hello from the API!" with id {created_notice_id}')

    assert created_notice['type'] == 'M'
    assert created_notice['content'] == 'Hello from the API!'

    # -- List notices --
    #
    # Retrieve all existing notices.
    #
    for notice in opalapi.notices.list_all():
        notice_id = notice['id']
        notice_type = notice['type'] # 'M': Message
                                     # 'P': Password Change
                                     # 'D': Default Password
                                     # 'R': Resource Overage
        notice_content = notice['content']
        notice_timestamp = notice['created_at']
        print(f'Listed notice (type {notice_type}, timestamp: {notice_timestamp}): {notice_content}')

    # -- Read single notice --
    #
    # Retrieve one existing notice by id.
    #
    notice = opalapi.notices.read(notice_id)
    print(f'Read notice by id: {notice_id}')

    assert notice['id'] == notice_id

    # -- Update notices --
    #
    # Change the name of existing notices.
    # Takes a list of items to update and returns a list of the updated items.
    #
    updated_notices = opalapi.notices.update([
        {'id': created_notice_id, 'content': 'Goodbye from the API!'},
    ])
    updated_notice = updated_notices[0]
    updated_notice_content = updated_notice['content']
    print(f'Updated notice content from "Hello from the API!" to "{updated_notice_content}"')

    assert updated_notice['content'] == 'Goodbye from the API!'
    assert updated_notice['id'] == created_notice_id

    # -- Delete notices --
    #
    # Delete existing notices by id.
    # Takes a list of items to delete.
    #
    opalapi.notices.delete([
        {'id': created_notice_id},
    ])
    print(f'Deleted notice with id {created_notice_id}')

    assert not any(notice['id'] == created_notice_id for notice in opalapi.notices.list_all())
