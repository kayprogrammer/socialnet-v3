import uuid

from app.common.handlers import ErrorCode


BASE_URL_PATH = "/api/v3/chats"


async def test_retrieve_chats(authorized_client, chat):
    response = await authorized_client.get(BASE_URL_PATH)
    assert response.status_code == 200
    resp = response.json()
    assert resp["status"] == "success"
    assert resp["message"] == "Chats fetched"
    assert len(resp["data"]["chats"]) > 0


async def test_send_message(authorized_client, chat, mocker):
    message_data = {"chat_id": str(uuid.uuid4()), "text": "JESUS is KING"}
    # Verify the requests fails with invalid chat id
    response = await authorized_client.post(BASE_URL_PATH, json=message_data)
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "User has no chat with that ID",
    }

    # Verify the requests suceeds with valid chat id
    message_data["chat_id"] = str(chat.id)
    response = await authorized_client.post(BASE_URL_PATH, json=message_data)
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Message sent",
        "data": {
            "id": mocker.ANY,
            "chat_id": str(chat.id),
            "sender": mocker.ANY,
            "text": message_data["text"],
            "created_at": mocker.ANY,
            "updated_at": mocker.ANY,
            "file_upload_data": None,
        },
    }
