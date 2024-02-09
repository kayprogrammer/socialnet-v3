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
    # You can test for other error responses yourself


async def test_retrieve_chat_messages(
    authorized_client, message, another_verified_user, mocker
):
    chat = message.chat
    # Verify the request fails with invalid chat ID
    response = await authorized_client.get(f"{BASE_URL_PATH}/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "User has no chat with that ID",
    }

    # Verify the request succeeds with valid chat ID
    response = await authorized_client.get(f"{BASE_URL_PATH}/{chat.id}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Messages fetched",
        "data": {
            "chat": {
                "id": str(chat.id),
                "name": chat.name,
                "owner": mocker.ANY,
                "ctype": chat.ctype,
                "description": chat.description,
                "image": chat.get_image,
                "latest_message": {
                    "sender": mocker.ANY,
                    "text": message.text,
                    "file": message.get_file,
                },
                "created_at": mocker.ANY,
                "updated_at": mocker.ANY,
            },
            "messages": {
                "per_page": 400,
                "current_page": 1,
                "last_page": 1,
                "items": [
                    {
                        "id": str(message.id),
                        "chat_id": str(chat.id),
                        "sender": mocker.ANY,
                        "text": message.text,
                        "file": message.get_file,
                        "created_at": mocker.ANY,
                        "updated_at": mocker.ANY,
                    }
                ],
            },
            "users": [
                {
                    "full_name": another_verified_user.full_name,
                    "username": another_verified_user.username,
                    "avatar": another_verified_user.get_avatar,
                }
            ],
        },
    }
