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
