from uuid import UUID
from fastapi import APIRouter, Depends, Path, Request
from app.api.deps import get_current_user
from app.api.routes.utils import (
    create_file,
    get_chat_object,
    is_secured,
    set_chat_latest_messages,
)
from app.api.schemas.chat import (
    ChatResponseSchema,
    ChatsResponseSchema,
    MessageCreateResponseSchema,
    MessageCreateSchema,
)

from app.api.utils.file_processors import ALLOWED_FILE_TYPES, ALLOWED_IMAGE_TYPES
from app.api.utils.paginators import Paginator
from app.api.utils.utils import set_dict_attr
from app.common.handlers import ErrorCode

from app.api.schemas.base import ResponseSchema

from app.models.accounts.tables import User

from app.common.handlers import RequestError
from app.models.base.tables import File
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
async def retrieve_messages(chat_id: UUID, page: int = 1, user: User = Depends(get_current_user)) -> ChatResponseSchema:
    chat = await get_chat_object(user, chat_id)
    paginator.page_size = 400
    paginated_data = await paginator.paginate_queryset(chat.messages, page)
    # Set latest message obj
    messages = paginated_data["items"]
    chat._latest_message_obj = messages[0] if len(messages) > 0 else None
    
    data = {"chat": chat, "messages": paginated_data, "users": chat.recipients}
    return {"message": "Messages fetched", "data": data}
