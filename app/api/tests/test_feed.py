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
