from uuid import UUID
from fastapi import APIRouter, Depends, Path, Request
from app.api.deps import get_current_user
from app.api.routes.utils import (
    get_comment_object,
    get_post_object,
    get_reaction_focus_object,
    get_reactions_queryset,
    get_reply_object,
    is_secured,
)
from app.api.schemas.feed import (
    CommentInputSchema,
    CommentResponseSchema,
    CommentWithRepliesResponseSchema,
    CommentsResponseSchema,
    PostInputResponseSchema,
    PostInputSchema,
    PostResponseSchema,
    PostsResponseSchema,
    ReactionInputSchema,
    ReactionResponseSchema,
    ReactionsResponseSchema,
    ReplyResponseSchema,
)
from app.api.utils.file_processors import ALLOWED_IMAGE_TYPES
from app.api.utils.notification import send_notification_in_socket
from app.api.utils.paginators import Paginator
from app.api.utils.utils import set_dict_attr
from app.common.handlers import ErrorCode

from app.api.schemas.base import ResponseSchema

from app.models.accounts.tables import User

from app.common.handlers import RequestError
from app.models.base.tables import File
from app.models.feed.tables import Comment, Post, Reaction, Reply
from app.models.profiles.tables import Notification

router = APIRouter()
paginator = Paginator()


@router.get(
    "/posts",
    summary="Retrieve Latest Posts",
    description="This endpoint retrieves a paginated response of latest posts",
)
async def retrieve_posts(page: int = 1) -> PostsResponseSchema:
    posts = Post.objects(
        Post.author,
        Post.author.avatar,
        Post.image,
    ).order_by("created_at", ascending=False)
    paginated_data = await paginator.paginate_queryset(posts, page)
    return {"message": "Posts fetched", "data": paginated_data}


@router.post(
    "/posts",
    summary="Create Post",
    description=f"""
        This endpoint creates a new post
        ALLOWED FILE TYPES: {", ".join(ALLOWED_IMAGE_TYPES)}
    """,
    status_code=201,
)
async def create_post(
    data: PostInputSchema, user: User = Depends(get_current_user)
) -> PostInputResponseSchema:
    data = data.model_dump()
    file_type = data.pop("file_type", None)
    image_upload_id = False
    if file_type:
        file = await File.objects().create(resource_type=file_type)
        data["image"] = file
        image_upload_id = file.id

    data["author"] = user
    post = await Post.objects(Post.image).create(**data)
    post.image_upload_id = image_upload_id
    return {"message": "Post created", "data": post}


@router.get(
    "/posts/{slug}",
    summary="Retrieve Single Post",
    description="This endpoint retrieves a single post",
)
async def retrieve_post(slug: str) -> PostResponseSchema:
    post = await get_post_object(slug, "detailed")
    return {"message": "Post Detail fetched", "data": post}


@router.put(
    "/posts/{slug}",
    summary="Update a Post",
    description="This endpoint updates a post",
)
async def update_post(
    slug: str, data: PostInputSchema, user: User = Depends(get_current_user)
) -> PostInputResponseSchema:
    post = await get_post_object(slug, "detailed")
    if post.author.id != user.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="This Post isn't yours",
        )

    data = data.model_dump()
    file_type = data.pop("file_type", None)
    image_upload_id = False
    if file_type:
        # Create or update image object
        file = post.image
        if not file.id:
            file = await File.objects().create(resource_type=file_type)
        else:
            file.resource_type = file_type
            await file.save()
        data["image"] = file
        image_upload_id = file.id

    post = set_dict_attr(data, post)
    post.image_upload_id = image_upload_id
    await post.save()
    return {"message": "Post updated", "data": post}


@router.delete(
    "/posts/{slug}/",
    summary="Delete a Post",
    description="This endpoint deletes a post",
)
async def delete_post(
    slug: str, user: User = Depends(get_current_user)
) -> ResponseSchema:
    post = await get_post_object(slug)  # simple post object
    if post.author != user.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="This Post isn't yours",
        )
    await post.remove()
    return {"message": "Post deleted"}


focus_query = Path(
    ...,
    description="Specify the usage. Use any of the three: POST, COMMENT, REPLY",
)
slug_query = Path(..., description="Enter the slug of the post or comment or reply")


@router.get(
    "/reactions/{focus}/{slug}",
    summary="Retrieve Latest Reactions of a Post, Comment, or Reply",
    description="""
        This endpoint retrieves paginated responses of reactions of post, comment, reply.
    """,
)
async def retrieve_reactions(
    focus: str = focus_query,
    slug: str = slug_query,
    reaction_type: str = None,
    page: int = 1,
) -> ReactionsResponseSchema:
    reactions = await get_reactions_queryset(focus, slug, reaction_type)
    paginated_data = await paginator.paginate_queryset(reactions, page)
    return {"message": "Reactions fetched", "data": paginated_data}


@router.post(
    "/reactions/{focus}/{slug}",
    summary="Create Reaction",
    description="""
        This endpoint creates a new reaction
        rtype should be any of these:
        
        - LIKE    - LOVE
        - HAHA    - WOW
        - SAD     - ANGRY
    """,
    status_code=201,
)
async def create_reaction(
    request: Request,
    data: ReactionInputSchema,
    focus: str = focus_query,
    slug: str = slug_query,
    user: User = Depends(get_current_user),
) -> ReactionResponseSchema:
    obj = await get_reaction_focus_object(focus, slug)

    data = data.model_dump()
    data["user"] = user
    rtype = data.pop("rtype").value
    obj_field = focus.lower()  # Focus object field (e.g post, comment, reply)
    data[obj_field] = obj

    # Update or create reaction
    reaction = await Reaction.objects(Reaction.user, Reaction.user.avatar).get(
        Reaction.user == user
    )
    if reaction:
        reaction.rtype = rtype
        await reaction.save()
    else:
        data["rtype"] = rtype
        reaction = await Reaction.objects().create(**data)

    # Create and Send Notification
    if (
        obj.author.id != user.id
    ):  # Send notification only when it's not the user reacting to his data
        notification = await Notification.objects(
            Notification.sender,
            Notification.sender.avatar,
            Notification.post,
            Notification.comment,
            Notification.comment.post,
            Notification.reply,
            Notification.reply.comment,
            Notification.reply.comment.post,
        ).get_or_create(
            Notification.sender == user.id,
            Notification.ntype == "REACTION",
            getattr(Notification, obj_field) == obj.id,
        )
        if notification._was_created:
            await notification.add_m2m(User(id=obj.author), m2m=Notification.receivers)

            # Send to websocket
            await send_notification_in_socket(
                is_secured(request),
                request.headers["host"],
                notification,
            )

    return {"message": "Reaction created", "data": reaction}


@router.delete(
    "/reactions/{id}",
    summary="Remove Reaction",
    description="""
        This endpoint deletes a reaction.
    """,
)
async def remove_reaction(
    request: Request, id: UUID, user: User = Depends(get_current_user)
) -> ResponseSchema:
    reaction = await Reaction.objects(
        Reaction.post, Reaction.comment, Reaction.reply
    ).get(Reaction.id == id)
    if not reaction:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="Reaction does not exist",
            status_code=404,
        )
    if user.id != reaction.user:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="Not yours to delete",
            status_code=401,
        )

    # Remove Reaction Notification
    targeted_obj = reaction.targeted_obj
    targeted_field = targeted_obj.__class__.__name__.lower()  # (post, comment or reply)

    notification = (
        await Notification.objects()
        .where(
            Notification.sender == user.id,
            Notification.ntype == "REACTION",
            getattr(Notification, targeted_field) == targeted_obj.id,
        )
        .first()
    )
    if notification:
        # Send to websocket and delete notification
        await send_notification_in_socket(
            is_secured(request), request.headers["host"], notification, status="DELETED"
        )
        await notification.remove()

    await reaction.remove()
    return {"message": "Reaction deleted"}


# COMMENTS


@router.get(
    "/posts/{slug}/comments",
    summary="Retrieve Post Comments",
    description="""
        This endpoint retrieves comments of a particular post.
    """,
)
async def retrieve_comments(slug: str, page: int = 1) -> CommentsResponseSchema:
    post = await get_post_object(slug)
    comments = Comment.objects(Comment.author, Comment.author.avatar).where(
        Comment.post == post.id
    )
    paginated_data = await paginator.paginate_queryset(comments, page)
    return {"message": "Comments Fetched", "data": paginated_data}


@router.post(
    "/posts/{slug}/comments",
    summary="Create Comment",
    description="""
        This endpoint creates a comment for a particular post.
    """,
    status_code=201,
)
async def create_comment(
    request: Request,
    slug: str,
    data: CommentInputSchema,
    user: User = Depends(get_current_user),
) -> CommentResponseSchema:
    post = await get_post_object(slug)
    comment = await Comment.objects().create(post=post, author=user, text=data.text)

    # Create and Send Notification
    if user.id != post.author:
        notification = await Notification.objects().create(
            sender=user.id, ntype="COMMENT", comment=comment.id
        )
        await notification.add_m2m(User(id=post.author), m2m=Notification.receivers)

        # Send to websocket
        await send_notification_in_socket(
            is_secured(request), request.headers["host"], notification
        )
    return {"message": "Comment Created", "data": comment}


@router.get(
    "/comments/{slug}",
    summary="Retrieve Comment with replies",
    description="""
        This endpoint retrieves a comment with replies.
    """,
)
async def retrieve_comment_with_replies(
    slug: str, page: int = 1
) -> CommentWithRepliesResponseSchema:
    comment = await get_comment_object(slug)
    replies = Reply.objects(Reply.author, Reply.author.avatar).where(
        Reply.comment == comment.id
    )
    paginated_data = await paginator.paginate_queryset(replies, page)
    data = {"comment": comment, "replies": paginated_data}
    return {"message": "Comment and Replies Fetched", "data": data}


@router.post(
    "/comments/{slug}",
    summary="Create Reply",
    description="""
        This endpoint creates a reply for a comment.
    """,
    status_code=201,
)
async def create_reply(
    request: Request,
    slug: str,
    data: CommentInputSchema,
    user: User = Depends(get_current_user),
) -> ReplyResponseSchema:
    comment = await get_comment_object(slug)
    reply = await Reply.objects().create(author=user, comment=comment, text=data.text)

    # Create and Send Notification
    if user.id != comment.author.id:
        notification = await Notification.objects().create(
            sender=user.id, ntype="REPLY", reply=reply.id
        )
        await notification.add_m2m(User(id=comment.author), m2m=Notification.receivers)

        # Send to websocket
        await send_notification_in_socket(
            is_secured(request), request.headers["host"], notification
        )
    return {"message": "Reply Created", "data": reply}


@router.put(
    "/comments/{slug}",
    summary="Update Comment",
    description="""
        This endpoint updates a particular comment.
    """,
)
async def update_comment(
    slug: str, data: CommentInputSchema, user: User = Depends(get_current_user)
) -> CommentResponseSchema:
    comment = await get_comment_object(slug)
    if comment.author.id != user.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="Not yours to edit",
            status_code=401,
        )
    comment.text = data.text
    await comment.save()
    return {"message": "Comment Updated", "data": comment}


@router.delete(
    "/comments/{slug}",
    summary="Delete Comment",
    description="""
        This endpoint deletes a comment.
    """,
)
async def delete_comment(
    request: Request, slug: str, user: User = Depends(get_current_user)
) -> ResponseSchema:
    comment = await get_comment_object(slug)
    if user.id != comment.author.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="Not yours to delete",
            status_code=401,
        )

    # # Remove Comment Notification
    notification = (
        await Notification.objects()
        .where(
            Notification.sender == user.id,
            Notification.ntype == "COMMENT",
            Notification.comment == comment.id,
        )
        .first()
    )
    if notification:
        # Send to websocket and delete notification
        await send_notification_in_socket(
            is_secured(request), request.headers["host"], notification, status="DELETED"
        )
        await notification.remove()

    await comment.remove()
    return {"message": "Comment Deleted"}


@router.get(
    "/replies/{slug}",
    summary="Retrieve Reply",
    description="""
        This endpoint retrieves a reply.
    """,
)
async def retrieve_reply(slug: str) -> ReplyResponseSchema:
    reply = await get_reply_object(slug)
    return {"message": "Reply Fetched", "data": reply}


@router.put(
    "/replies/{slug}",
    summary="Update Reply",
    description="""
        This endpoint updates a particular reply.
    """,
)
async def update_reply(
    slug: str, data: CommentInputSchema, user: User = Depends(get_current_user)
) -> ReplyResponseSchema:
    reply = await get_reply_object(slug)
    if reply.author.id != user.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="Not yours to edit",
            status_code=401,
        )
    reply.text = data.text
    await reply.save()
    return {"message": "Reply Updated", "data": reply}


@router.delete(
    "/replies/{slug}",
    summary="Delete reply",
    description="""
        This endpoint deletes a reply.
    """,
)
async def delete_reply(
    request: Request, slug: str, user: User = Depends(get_current_user)
) -> ResponseSchema:
    reply = await get_reply_object(slug)
    if user.id != reply.author.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="Not yours to delete",
            status_code=401,
        )

    # Remove Reply Notification
    notification = (
        await Notification.objects()
        .where(
            Notification.sender == user,
            Notification.ntype == "REPLY",
            Notification.reply == reply.id,
        )
        .first()
    )
    if notification:
        # Send to websocket and delete notification
        await send_notification_in_socket(
            is_secured(request), request.headers["host"], notification, status="DELETED"
        )
        await notification.remove()

    await reply.remove()
    return {"message": "Reply Deleted"}
