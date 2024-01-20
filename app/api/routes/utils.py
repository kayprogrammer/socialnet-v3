from typing import Literal

from fastapi import Request
from app.common.handlers import ErrorCode, RequestError
from app.models.accounts.tables import User

from app.models.feed.tables import Comment, Post, Reply, Reaction
from app.models.profiles.tables import Friend


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


reaction_focus = {"POST": Post, "COMMENT": Comment, "REPLY": Reply}


async def validate_reaction_focus(focus):
    if not focus in list(reaction_focus.keys()):
        raise RequestError(
            err_code=ErrorCode.INVALID_VALUE,
            err_msg="Invalid 'focus' value",
            status_code=404,
        )
    return reaction_focus[focus]


async def get_reaction_focus_object(focus, slug):
    focus_model = await validate_reaction_focus(focus)
    related = [focus_model.author]  # Related object to preload
    if focus_model == Comment:
        related.append(Comment.post)  # Also preload post object for comment
    obj = await focus_model.objects(*related).get(focus_model.slug == slug)
    if not obj:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg=f"{focus.capitalize()} does not exist",
            status_code=404,
        )
    return obj


async def get_reactions_queryset(focus, slug, rtype=None):
    focus_obj = await get_reaction_focus_object(focus, slug)
    focus_obj_field = (
        focus.lower()
    )  # Field to filter reactions by (e.g post, comment, reply)
    filter = [
        getattr(Reaction, focus_obj_field) == focus_obj.id
    ]  # e.g Reaction.post == "value", Reaction.comment == "value"
    if rtype:
        filter.append(
            Reaction.rtype == rtype
        )  # Filter by reaction type if the query param is present
    reactions = Reaction.objects(Reaction.user, Reaction.user.avatar).where(*filter)
    return reactions


async def get_comment_object(slug):
    comment = await Comment.objects(
        Comment.author, Comment.author.avatar, Comment.post
    ).get(Comment.slug == slug)
    if not comment:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="Comment does not exist",
            status_code=404,
        )
    return comment


async def get_reply_object(slug):
    reply = await Reply.objects(Reply.author, Reply.author.avatar).get(
        Reply.slug == slug
    )
    if not reply:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="Reply does not exist",
            status_code=404,
        )
    return reply


def is_secured(request: Request) -> bool:
    return request.scope["scheme"].endswith("s")  # if request is secured


async def get_requestee_and_friend_obj(user, username, status=None):
    # Get and validate username existence
    requestee = await User.objects().get(User.username == username)
    if not requestee:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="User does not exist!",
            status_code=404,
        )

    friend = Friend.objects().where(
        ((Friend.requester == user.id) & (Friend.requestee == requestee.id))
        | ((Friend.requester == requestee.id) & (Friend.requestee == user.id))
    )
    if status:
        friend = friend.where(Friend.status == status)
    friend = await friend.first()
    return requestee, friend
