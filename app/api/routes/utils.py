from typing import Literal
from app.common.handlers import ErrorCode, RequestError

from app.models.feed.tables import Post


async def get_post_object(slug, object_type: Literal["simple", "detailed"] = "simple"):
    # object_type simple fetches the post object without prefetching related objects because they aren't needed
    # detailed fetches the post object with the related objects because they are needed

    post = Post.objects()
    if object_type == "detailed":
        post = post.prefetch(Post.author, Post.author.avatar, Post.image)
    post = await post.get(Post.slug == slug)
    if not post:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="Post does not exist",
            status_code=404,
        )
    return post
