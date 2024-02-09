BASE_URL_PATH = "/api/v3/feed"


async def test_retrieve_posts(client, post, mocker):
    response = await client.get(f"{BASE_URL_PATH}/posts")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Posts fetched",
        "data": {
            "per_page": 50,
            "current_page": 1,
            "last_page": 1,
            "posts": [
                {
                    "author": mocker.ANY,
                    "text": post.text,
                    "slug": post.slug,
                    "reactions_count": mocker.ANY,
                    "comments_count": mocker.ANY,
                    "image": None,
                    "created_at": mocker.ANY,
                    "updated_at": mocker.ANY,
                }
            ],
        },
    }


async def test_create_post(authorized_client, mocker):
    post_dict = {"text": "My new Post"}
    response = await authorized_client.post(f"{BASE_URL_PATH}/posts", json=post_dict)
    assert response.status_code == 201
    print(response.json())
    assert response.json() == {
        "status": "success",
        "message": "Post created",
        "data": {
            "author": mocker.ANY,
            "text": post_dict["text"],
            "slug": mocker.ANY,
            "reactions_count": 0,
            "comments_count": 0,
            "created_at": mocker.ANY,
            "updated_at": mocker.ANY,
            "file_upload_data": None,
        },
    }
