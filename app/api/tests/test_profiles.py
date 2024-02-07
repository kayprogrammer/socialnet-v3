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
