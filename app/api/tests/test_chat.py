BASE_URL_PATH = "/api/v3/chats"


async def test_retrieve_chats(authorized_client, chat):
    response = await authorized_client.get(BASE_URL_PATH)
    assert response.status_code == 200
    resp = response.json()
    assert resp["status"] == "success"
    assert resp["message"] == "Chats fetched"
    assert len(resp["data"]["chats"]) > 0
