from app.common.handlers import ErrorCode
import uuid

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


async def test_retrieve_post(client, post, mocker):
    # Test for post with invalid slug
    response = await client.get(f"{BASE_URL_PATH}/posts/invalid_slug")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "Post does not exist",
    }

    # Test for post with valid slug
    response = await client.get(f"{BASE_URL_PATH}/posts/{post.slug}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Post Detail fetched",
        "data": {
            "author": mocker.ANY,
            "text": post.text,
            "slug": post.slug,
            "reactions_count": mocker.ANY,
            "comments_count": mocker.ANY,
            "image": None,
            "created_at": mocker.ANY,
            "updated_at": mocker.ANY,
        },
    }


async def test_update_post(
    authorized_client, another_verified_user_tokens, post, mocker
):
    post_dict = {"text": "Post Text Updated"}

    # Check if endpoint fails for invalid post
    response = await authorized_client.put(
        f"{BASE_URL_PATH}/posts/invalid_slug", json=post_dict
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "Post does not exist",
    }

    # Check if endpoint fails for invalid owner
    response = await authorized_client.put(
        f"{BASE_URL_PATH}/posts/{post.slug}",
        json=post_dict,
        headers={"Authorization": f"Bearer {another_verified_user_tokens['access']}"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INVALID_OWNER,
        "message": "This Post isn't yours",
    }

    # Check if endpoint succeeds if all requirements are met
    response = await authorized_client.put(
        f"{BASE_URL_PATH}/posts/{post.slug}", json=post_dict
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Post updated",
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


async def test_delete_post(authorized_client, post):
    # Check if endpoint fails for invalid post
    response = await authorized_client.delete(f"{BASE_URL_PATH}/posts/invalid_slug")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.NON_EXISTENT,
        "message": "Post does not exist",
    }

    # Check if endpoint succeeds if all requirements are met
    response = await authorized_client.delete(f"{BASE_URL_PATH}/posts/{post.slug}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Post deleted",
    }


async def test_retrieve_reactions(client, reaction):
    author = reaction.user
    post = reaction.post
    # Test for invalid focus_value
    response = await client.get(f"{BASE_URL_PATH}/reactions/invalid_focus/{post.slug}")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Invalid 'focus' value",
        "code": ErrorCode.INVALID_VALUE,
    }

    # Test for invalid slug
    response = await client.get(f"{BASE_URL_PATH}/reactions/POST/invalid_slug")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Post does not exist",
        "code": ErrorCode.NON_EXISTENT,
    }

    # Test for valid values
    response = await client.get(f"{BASE_URL_PATH}/reactions/POST/{post.slug}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Reactions fetched",
        "data": {
            "per_page": 50,
            "current_page": 1,
            "last_page": 1,
            "reactions": [
                {
                    "id": str(reaction.id),
                    "user": {
                        "name": author.full_name,
                        "username": author.username,
                        "avatar": author.get_avatar,
                    },
                    "rtype": reaction.rtype,
                }
            ],
        },
    }


async def test_create_reaction(authorized_client, post, mocker):
    user = post.author
    reaction_dict = {"rtype": "LOVE"}
    response = await authorized_client.post(
        f"{BASE_URL_PATH}/reactions/POST/{post.slug}", json=reaction_dict
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Reaction created",
        "data": {
            "id": mocker.ANY,
            "user": {
                "name": user.full_name,
                "username": user.username,
                "avatar": user.get_avatar,
            },
            "rtype": reaction_dict["rtype"],
        },
    }


async def test_delete_reaction(authorized_client, reaction):
    # Test for invalid reaction id
    response = await authorized_client.delete(
        f"{BASE_URL_PATH}/reactions/{uuid.uuid4()}"
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Reaction does not exist",
        "code": ErrorCode.NON_EXISTENT,
    }
    response = await authorized_client.delete(
        f"{BASE_URL_PATH}/reactions/{reaction.id}"
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Reaction deleted",
    }

    # You can test for other error responses yourself


async def test_retrieve_comments(client, comment):
    user = comment.author
    post = comment.post

    # Test for invalid post slug
    response = await client.get(f"{BASE_URL_PATH}/posts/invalid_slug/comments")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Post does not exist",
        "code": ErrorCode.NON_EXISTENT,
    }

    # Test for valid values
    response = await client.get(f"{BASE_URL_PATH}/posts/{post.slug}/comments")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Comments Fetched",
        "data": {
            "per_page": 50,
            "current_page": 1,
            "last_page": 1,
            "comments": [
                {
                    "author": {
                        "name": user.full_name,
                        "username": user.username,
                        "avatar": user.get_avatar,
                    },
                    "slug": comment.slug,
                    "text": comment.text,
                    "reactions_count": comment.reactions_count,
                    "replies_count": comment.replies_count,
                }
            ],
        },
    }


async def test_create_comment(authorized_client, post, mocker):
    user = post.author
    comment_data = {"text": "My new comment"}

    response = await authorized_client.post(
        f"{BASE_URL_PATH}/posts/{post.slug}/comments", json=comment_data
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Comment Created",
        "data": {
            "author": {
                "name": user.full_name,
                "username": user.username,
                "avatar": user.get_avatar,
            },
            "slug": mocker.ANY,
            "text": comment_data["text"],
            "reactions_count": 0,
            "replies_count": 0,
        },
    }


async def test_retrieve_comment_with_replies(client, reply):
    user = reply.author
    comment = reply.comment

    # Test for invalid comment slug
    response = await client.get(f"{BASE_URL_PATH}/comments/invalid_slug")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Comment does not exist",
        "code": ErrorCode.NON_EXISTENT,
    }

    # Test for valid values
    response = await client.get(f"{BASE_URL_PATH}/comments/{comment.slug}")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
        "status": "success",
        "message": "Comment and Replies Fetched",
        "data": {
            "comment": {
                "author": {
                    "name": user.full_name,
                    "username": user.username,
                    "avatar": user.get_avatar,
                },
                "slug": comment.slug,
                "text": comment.text,
                "reactions_count": comment.reactions_count,
                "replies_count": 1,
            },
            "replies": {
                "per_page": 50,
                "current_page": 1,
                "last_page": 1,
                "items": [
                    {
                        "author": {
                            "name": user.full_name,
                            "username": user.username,
                            "avatar": user.get_avatar,
                        },
                        "slug": reply.slug,
                        "text": reply.text,
                        "reactions_count": 0,
                    }
                ],
            },
        },
    }
