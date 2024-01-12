from typing import Literal
from app.common.handlers import ErrorCode, RequestError

from app.models.feed.tables import Comment, Post, Reply, Reaction


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
