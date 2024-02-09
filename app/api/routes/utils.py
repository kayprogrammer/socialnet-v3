from typing import Literal

from fastapi import Request
from app.common.handlers import ErrorCode, RequestError
from app.models.accounts.tables import User
from app.models.base.tables import File
from app.models.chat.tables import Chat, Message

from app.models.feed.tables import Comment, Post, Reply, Reaction
from app.models.profiles.tables import Friend, Notification


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


def get_notifications_queryset(current_user):
    current_user_id = current_user.id
    # Fetch current user notifications
    notifications = (
        Notification.objects(
            Notification.sender,
            Notification.sender.avatar,
            Notification.post,
            Notification.comment,
            Notification.reply,
        )
        .where(Notification.receiver_ids.any(current_user_id))
        .order_by(Notification.created_at, ascending=False)
    )
    return notifications


async def set_chat_latest_messages(chats):
    latest_message_ids = [chat.latest_message_id for chat in chats]
    if latest_message_ids:
        latest_messages = await Message.objects(
            Message.sender, Message.sender.avatar, Message.file
        ).where(Message.id.is_in(latest_message_ids))
        latest_messages_dict = {
            latest_message.chat: latest_message for latest_message in latest_messages
        }
        for chat in chats:
            chat._latest_message_obj = latest_messages_dict.get(chat.id)
    return chats


# Create file object
async def create_file(file_type=None):
    file = None
    if file_type:
        file = await File.objects().create(resource_type=file_type)
    return file


async def get_chat_object(user, chat_id):
    chat = (
        await Chat.objects(Chat.owner, Chat.owner.avatar, Chat.image)
        .where((Chat.owner == user.id) | (Chat.user_ids.any(user.id)))
        .get(Chat.id == chat_id)
    )
    if not chat:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="User has no chat with that ID",
            status_code=404,
        )
    messages = (
        Message.objects(Message.sender, Message.sender.avatar, Message.file)
        .where(Message.chat == chat_id)
        .order_by(Message.created_at, ascending=False)
    )
    users = await User.objects(User.avatar).where(User.id.is_in(chat.user_ids))
    chat.messages = messages
    chat.users = users
    return chat


async def usernames_to_add_and_remove_validations(
    chat: Chat, usernames_to_add=None, usernames_to_remove=None
):
    original_user_ids = chat.user_ids
    if usernames_to_add:
        users_to_add = (
            await User.select(User.id)
            .where(User.username.is_in(usernames_to_add))
            .where((User.id.not_in(original_user_ids)) | (User.id != chat.owner))
        )
        user_ids_to_add = [user["id"] for user in users_to_add]
        chat.user_ids += user_ids_to_add
    if usernames_to_remove:
        if not original_user_ids:
            raise RequestError(
                err_code=ErrorCode.INVALID_ENTRY,
                err_msg="Invalid Entry",
                status_code=422,
                data={"usernames_to_remove": "No users to remove"},
            )
        users_to_remove = (
            await User.select(User.id)
            .where(User.username.is_in(usernames_to_remove))
            .where((User.id != chat.owner) & (User.id.is_in(original_user_ids)))
        )
        user_ids_to_remove = [user["id"] for user in users_to_remove]
        chat.user_ids = set(chat.user_ids) - set(user_ids_to_remove)

    if len(chat.user_ids) > 99:
        raise RequestError(
            err_code=ErrorCode.INVALID_ENTRY,
            err_msg="Invalid Entry",
            status_code=422,
            data={"usernames_to_add": "99 users limit reached"},
        )
    return chat


async def get_message_object(message_id, user):
    message = (
        await Message.objects(
            Message.sender, Message.sender.avatar, Message.chat, Message.file
        )
        .where(Message.sender == user.id)
        .get(Message.id == message_id)
    )
    if not message:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="User has no message with that ID",
            status_code=404,
        )
    return message
