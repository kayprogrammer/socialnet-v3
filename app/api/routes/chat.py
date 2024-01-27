from uuid import UUID
from fastapi import APIRouter, Depends, Path, Request
from app.api.deps import get_current_user
from app.api.routes.utils import (
    is_secured,
    set_chat_latest_messages,
)
from app.api.schemas.chat import ChatsResponseSchema

from app.api.utils.file_processors import ALLOWED_IMAGE_TYPES
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
    chats = Chat.objects(Chat.owner, Chat.owner.avatar, Chat.image).where(
        (Chat.owner == user.id) | (Chat.user_ids.any(user.id))
    )
    paginator.page_size = 200
    paginated_data = await paginator.paginate_queryset(chats, page)
    # To attach latest messages
    items = paginated_data["items"]
    items = await set_chat_latest_messages(items)
    return {"message": "Chats fetched", "data": paginated_data}
