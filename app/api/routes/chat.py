from uuid import UUID
from fastapi import APIRouter, Depends, Request
from app.api.deps import get_current_user
from app.api.routes.utils import (
    create_file,
    get_chat_object,
    get_message_object,
    is_secured,
    set_chat_latest_messages,
    usernames_to_add_and_remove_validations,
)
from app.api.schemas.chat import (
    ChatResponseSchema,
    ChatsResponseSchema,
    GroupChatCreateSchema,
    GroupChatInputResponseSchema,
    GroupChatInputSchema,
    MessageCreateResponseSchema,
    MessageCreateSchema,
    MessageUpdateSchema,
)
from app.api.sockets.chat import send_message_deletion_in_socket

from app.api.utils.file_processors import ALLOWED_FILE_TYPES
from app.api.utils.paginators import Paginator
from app.api.utils.utils import set_dict_attr
from app.common.handlers import ErrorCode

from app.api.schemas.base import ResponseSchema

from app.models.accounts.tables import User

from app.common.handlers import RequestError
from app.models.chat.tables import Chat, Message

router = APIRouter()
paginator = Paginator()


@router.get(
    "",
    summary="Retrieve User Chats",
    description="""
        This endpoint retrieves a paginated list of the current user chats
        Only chats with type "GROUP" have name, image and description.
    """,
)
async def retrieve_user_chats(
    page: int = 1, user: User = Depends(get_current_user)
) -> ChatsResponseSchema:
    chats = (
        Chat.objects(Chat.owner, Chat.owner.avatar, Chat.image)
        .where((Chat.owner == user.id) | (Chat.user_ids.any(user.id)))
        .order_by(Chat.updated_at, ascending=False)
    )
    paginator.page_size = 200
    paginated_data = await paginator.paginate_queryset(chats, page)
    # To attach latest messages
    items = paginated_data["items"]
    items = await set_chat_latest_messages(items)
    return {"message": "Chats fetched", "data": paginated_data}


@router.post(
    "",
    summary="Send a message",
    description=f"""
        This endpoint sends a message.
        You must either send a text or a file or both.
        If there's no chat_id, then its a new chat and you must set username and leave chat_id
        If chat_id is available, then ignore username and set the correct chat_id
        The file_upload_data in the response is what is used for uploading the file to cloudinary from client
        ALLOWED FILE TYPES: {", ".join(ALLOWED_FILE_TYPES)}
    """,
    status_code=201,
)
async def send_message(
    data: MessageCreateSchema, user: User = Depends(get_current_user)
) -> MessageCreateResponseSchema:
    chat_id = data.chat_id
    username = data.username

    # For sending
    chat = None
    if not chat_id:
        # Create a new chat dm with current user and recipient user
        recipient_user = await User.objects().get(User.username == username)
        if not recipient_user:
            raise RequestError(
                err_code=ErrorCode.INVALID_ENTRY,
                err_msg="Invalid entry",
                status_code=422,
                data={"username": "No user with that username"},
            )

        chat = (
            await Chat.objects()
            .where(
                Chat.ctype == "DM",
                ((Chat.owner == user.id) & (Chat.user_ids.any(recipient_user.id)))
                | ((Chat.owner == recipient_user.id) & (Chat.user_ids.any(user.id))),
            )
            .first()
        )

        # Check if a chat already exists between both users
        if chat:
            raise RequestError(
                err_code=ErrorCode.INVALID_ENTRY,
                err_msg="Invalid entry",
                status_code=422,
                data={"username": "A chat already exist between you and the recipient"},
            )
        chat = await Chat.objects().create(owner=user.id, user_ids=[recipient_user.id])
    else:
        # Get the chat with chat id and check if the current user is the owner or the recipient
        chat = (
            await Chat.objects()
            .where((Chat.owner == user.id) | (Chat.user_ids.any(user.id)))
            .get(Chat.id == chat_id)
        )
        if not chat:
            raise RequestError(
                err_code=ErrorCode.NON_EXISTENT,
                err_msg="User has no chat with that ID",
                status_code=404,
            )

    # Create Message
    file = await create_file(data.file_type)
    file_upload_id = file.id if file else None
    message = await Message.objects().create(
        chat=chat.id, sender=user.id, text=data.text, file=file
    )
    message.sender = user
    message.file_upload_id = file_upload_id
    return {"message": "Message sent", "data": message}


@router.get(
    "/{chat_id}",
    summary="Retrieve messages from a Chat",
    description="""
        This endpoint retrieves all messages in a chat.
    """,
)
async def retrieve_messages(
    chat_id: UUID, page: int = 1, user: User = Depends(get_current_user)
) -> ChatResponseSchema:
    chat = await get_chat_object(user, chat_id)
    paginator.page_size = 400
    paginated_data = await paginator.paginate_queryset(chat.messages, page)
    # Set latest message obj
    messages = paginated_data["items"]
    chat._latest_message_obj = messages[0] if len(messages) > 0 else None

    data = {"chat": chat, "messages": paginated_data, "users": chat.users}
    return {"message": "Messages fetched", "data": data}


@router.patch(
    "/{chat_id}",
    summary="Update a Group Chat",
    description="""
        This endpoint updates a group chat.
    """,
)
async def update_group_chat(
    chat_id: UUID, data: GroupChatInputSchema, user: User = Depends(get_current_user)
) -> GroupChatInputResponseSchema:
    chat = (
        await Chat.objects(Chat.image)
        .where(Chat.owner == user.id, Chat.ctype == "GROUP")
        .get(Chat.id == chat_id)
    )
    if not chat:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="User owns no group chat with that ID",
            status_code=404,
        )

    data = data.model_dump(exclude_none=True)

    # Handle File Upload
    file_type = data.pop("file_type", None)
    image_upload_id = False
    if file_type:
        file = chat.image
        if file.id:
            file.resource_type = file_type
            await file.save()
        else:
            file = await create_file(file_type)
            data["image"] = file.id
        image_upload_id = file.id
    # Handle Users Upload or Remove
    usernames_to_add = data.pop("usernames_to_add", None)
    usernames_to_remove = data.pop("usernames_to_remove", None)
    chat = await usernames_to_add_and_remove_validations(
        chat, usernames_to_add, usernames_to_remove
    )
    chat = set_dict_attr(data, chat)
    await chat.save()
    chat.users = await User.objects(User.avatar).where(User.id.is_in(chat.user_ids))
    chat.image_upload_id = image_upload_id
    return {"message": "Chat updated", "data": chat}


@router.delete(
    "/{chat_id}",
    summary="Delete a Group Chat",
    description="""
        This endpoint deletes a group chat.
    """,
)
async def delete_group_chat(
    chat_id: UUID, user: User = Depends(get_current_user)
) -> ResponseSchema:
    chat = (
        await Chat.objects()
        .where(Chat.owner == user.id, Chat.ctype == "GROUP")
        .get(Chat.id == chat_id)
    )
    if not chat:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="User owns no group chat with that ID",
            status_code=404,
        )
    await chat.remove()
    return {"message": "Group Chat Deleted"}


@router.put(
    "/messages/{message_id}",
    summary="Update a message",
    description=f"""
        This endpoint updates a message.
        You must either send a text or a file or both.
        The file_upload_data in the response is what is used for uploading the file to cloudinary from client
        ALLOWED FILE TYPES: {", ".join(ALLOWED_FILE_TYPES)}
    """,
)
async def update_message(
    message_id: UUID, data: MessageUpdateSchema, user: User = Depends(get_current_user)
) -> MessageCreateResponseSchema:
    message = await get_message_object(message_id, user)

    data = data.model_dump(exclude_none=True)
    # Handle File Upload
    file_upload_id = None
    file_type = data.pop("file_type", None)
    if file_type:
        file = message.file
        if file.id:
            file.resource_type = file_type
            await file.save()
        else:
            file = await create_file(file_type)
            data["file"] = file.id
        file_upload_id = file.id
    message = set_dict_attr(data, message)
    await message.save()
    message.file_upload_id = file_upload_id
    message.chat = message.chat.id
    return {"message": "Message updated", "data": message}


@router.delete(
    "/messages/{message_id}",
    summary="Delete a message",
    description="""
        This endpoint deletes a message.

    """,
)
async def delete_message(
    request: Request, message_id: UUID, user: User = Depends(get_current_user)
) -> ResponseSchema:
    message = await get_message_object(message_id, user)
    chat = message.chat
    chat_id = chat.id
    messages_count = await Message.count().where(Message.chat == chat_id)

    # Send socket message
    await send_message_deletion_in_socket(
        is_secured(request), request.headers["host"], chat_id, message_id
    )

    # Delete message and chat if its the last message in the dm being deleted
    if messages_count == 1 and chat.ctype == "DM":
        await chat.remove()  # Message deletes if chat gets deleted (CASCADE)
    else:
        # Set new latest message
        new_latest_message = (
            await Message.select(Message.id)
            .where(Message.chat == chat_id, Message.id != message.id)
            .order_by(Message.created_at, ascending=False)
            .first()
        )
        new_latest_message_id = new_latest_message["id"] if new_latest_message else None
        chat.latest_message_id = new_latest_message_id
        await chat.save()
        await message.remove()
    return {"message": "Message deleted"}


@router.post(
    "/groups/group",
    summary="Create a group chat",
    description="""
        This endpoint creates a group chat.
        The users_entry field should be a list of usernames you want to add to the group.
        Note: You cannot add more than 99 users in a group (1 owner + 99 other users = 100 users total)
    """,
    status_code=201,
)
async def create_group_chat(
    data: GroupChatCreateSchema, user: User = Depends(get_current_user)
) -> GroupChatInputResponseSchema:
    data = data.model_dump(exclude_none=True)
    data.update({"owner": user, "ctype": "GROUP"})
    # Handle File Upload
    file_type = data.pop("file_type", None)
    image_upload_id = None
    if file_type:
        file = await create_file(file_type)
        data["image"] = file.id
        image_upload_id = file.id

    # Handle Users Upload or Remove
    usernames_to_add = data.pop("usernames_to_add")
    users_to_add = await User.objects(User.avatar).where(
        User.username.is_in(usernames_to_add), User.id != user.id
    )
    if not users_to_add:
        raise RequestError(
            err_code=ErrorCode.INVALID_ENTRY,
            err_msg="Invalid Entry",
            data={"usernames_to_add": "Enter at least one valid username"},
            status_code=422,
        )

    # Create Chat
    data["user_ids"] = [user.id for user in users_to_add]
    chat = await Chat.objects().create(**data)
    chat.users = users_to_add
    chat.image_upload_id = image_upload_id
    return {"message": "Chat created", "data": chat}
