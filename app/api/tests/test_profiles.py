from slugify import slugify
from app.common.handlers import ErrorCode


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

