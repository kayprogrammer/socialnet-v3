async def test_retrieve_sitedetail(client):
    # Check response validity
    response = await client.get("/api/v3/general/site-detail")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"
    assert json_resp["message"] == "Site Details fetched"
    keys = ["name", "email", "phone", "address", "fb", "tw", "wh", "ig"]
    assert all(item in json_resp["data"] for item in keys)
