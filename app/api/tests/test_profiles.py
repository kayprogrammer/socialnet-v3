import uuid
from app.common.handlers import ErrorCode
from app.models.accounts.tables import User
from app.models.profiles.tables import Notification

BASE_URL_PATH = "/api/v3/profiles"


async def test_retrieve_cities(client, city):
    # Test for valid response for non-existent city name query
    response = await client.get(f"{BASE_URL_PATH}/cities?name=non_existent")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "No match found",
        "data": [],
    }

    # Test for valid response for existent city name query
    response = await client.get(f"{BASE_URL_PATH}/cities?name={city.name}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Cities Fetched",
        "data": [
            {
                "id": str(city.id),
                "name": city.name,
                "region": city.region.name,
                "country": city.country.name,
            }
        ],
    }


async def test_retrieve_profile(client, verified_user, mocker):
    # Test for valid response for non-existent username
    response = await client.get(f"{BASE_URL_PATH}/profile/invalid_username")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "No user with that username",
        "code": ErrorCode.NON_EXISTENT,
    }

    # Test for valid response for valid entry
    response = await client.get(f"{BASE_URL_PATH}/profile/{verified_user.username}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "User details fetched",
        "data": {
            "first_name": verified_user.first_name,
            "last_name": verified_user.last_name,
            "username": verified_user.username,
            "email": verified_user.email,
            "bio": verified_user.bio,
            "avatar": verified_user.get_avatar,
            "dob": str(verified_user.dob),
            "city": None,
            "created_at": mocker.ANY,
            "updated_at": mocker.ANY,
        },
    }


async def test_update_profile(authorized_client, verified_user, mocker):
    user_data = {
        "first_name": "TestUpdated",
        "last_name": "VerifiedUpdated",
        "bio": "Updated my bio",
    }

    # Test for valid response for valid entry
    response = await authorized_client.patch(f"{BASE_URL_PATH}/profile", json=user_data)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "User updated",
        "data": {
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "username": verified_user.username,
            "email": verified_user.email,
            "bio": user_data["bio"],
            "dob": str(verified_user.dob),
            "city": None,
            "created_at": mocker.ANY,
            "updated_at": mocker.ANY,
            "file_upload_data": None,
        },
    }


async def test_delete_profile(authorized_client, verified_user, mocker):
    user_data = {"password": "invalid_pass"}

    # Test for valid response for invalid entry
    response = await authorized_client.post(f"{BASE_URL_PATH}/profile", json=user_data)
    assert response.status_code == 422
    assert response.json() == {
        "status": "failure",
        "message": "Invalid Entry",
        "code": ErrorCode.INVALID_CREDENTIALS,
        "data": {"password": "Incorrect password"},
    }

    # Test for valid response for valid entry
    user_data["password"] = "testpassword"
    response = await authorized_client.post(f"{BASE_URL_PATH}/profile", json=user_data)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "User deleted",
    }


async def test_retrieve_friends(authorized_client, friend, mocker):
    friend = friend.requestee
    # Test for valid response
    response = await authorized_client.get(f"{BASE_URL_PATH}/friends")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Friends fetched",
        "data": {
            "per_page": 20,
            "current_page": 1,
            "last_page": 1,
            "users": [
                {
                    "first_name": friend.first_name,
                    "last_name": friend.last_name,
                    "username": friend.username,
                    "email": friend.email,
                    "bio": friend.bio,
                    "avatar": friend.get_avatar,
                    "dob": str(friend.dob),
                    "city": None,
                    "created_at": mocker.ANY,
                    "updated_at": mocker.ANY,
                }
            ],
        },
    }


async def test_send_friend_request(authorized_client):
    data = {"username": "invalid_username"}
    user = await User.create_user(
        first_name="Friend",
        last_name="User",
        email="friend_user@email.com",
        password="password",
    )
    # Test for valid response for non-existent user name
    response = await authorized_client.post(
        f"{BASE_URL_PATH}/friends/requests", json=data
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "User does not exist!",
    }

    # Test for valid response for valid inputs
    data["username"] = user.username
    response = await authorized_client.post(
        f"{BASE_URL_PATH}/friends/requests", json=data
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Friend Request sent",
    }
    # You can test for other error responses yourself.....


async def test_accept_or_reject_friend_request(another_authorized_client, friend):
    data = {"username": "invalid_username", "accepted": True}
    friend.status = "PENDING"
    await friend.save()

    # Test for valid response for non-existent user name
    response = await another_authorized_client.put(
        f"{BASE_URL_PATH}/friends/requests", json=data
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "User does not exist!",
    }

    # Test for valid response for valid inputs
    data["username"] = friend.requester.username
    response = await another_authorized_client.put(
        f"{BASE_URL_PATH}/friends/requests", json=data
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Friend Request Accepted",
    }
    # You can test for other error responses yourself.....


async def test_retrieve_notifications(authorized_client, verified_user):
    notification = await Notification.objects().create(
        ntype="ADMIN", text="A new update is coming!", receiver_ids=[verified_user.id]
    )

    # Test for valid response
    response = await authorized_client.get(f"{BASE_URL_PATH}/notifications")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Notifications fetched",
        "data": {
            "per_page": 20,
            "current_page": 1,
            "last_page": 1,
            "notifications": [
                {
                    "id": str(notification.id),
                    "sender": None,
                    "ntype": notification.ntype,
                    "message": notification.message,
                    "post_slug": None,
                    "comment_slug": None,
                    "reply_slug": None,
                    "is_read": False,
                }
            ],
        },
    }


async def test_read_notification(authorized_client, verified_user):
    notification = await Notification.objects().create(
        ntype="ADMIN", text="A new update is coming!", receiver_ids=[verified_user.id]
    )

    data = {"id": str(uuid.uuid4()), "mark_all_as_read": False}

    # Test for invalid response for non-existent id
    response = await authorized_client.post(f"{BASE_URL_PATH}/notifications", json=data)
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "User has no notification with that ID",
    }

    # Test for valid response for valid inputs
    data["id"] = str(notification.id)
    response = await authorized_client.post(f"{BASE_URL_PATH}/notifications", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Notification read",
    }
