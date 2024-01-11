from fastapi import APIRouter, BackgroundTasks, Depends
from app.api.deps import get_current_user
from app.api.schemas.feed import PostsResponseSchema
from app.api.utils.auth import Authentication
from app.api.utils.paginators import Paginator
from app.common.handlers import ErrorCode
from piccolo.query.methods.select import Count

from app.api.schemas.base import ResponseSchema
from app.api.schemas.auth import (
    LoginUserSchema,
    RefreshTokensSchema,
    RegisterResponseSchema,
    RegisterUserSchema,
    RequestOtpSchema,
    SetNewPasswordSchema,
    TokensResponseSchema,
    VerifyOtpSchema,
)

from app.api.utils.emails import send_email

from app.models.accounts.tables import Otp, User

from app.common.handlers import RequestError
from app.models.base.tables import File
from app.models.feed.tables import Post

router = APIRouter()


@router.get(
    "/posts",
    summary="Retrieve Latest Posts",
    description="This endpoint retrieves paginated responses of latest posts",
)
async def retrieve_posts(page: int = 1) -> PostsResponseSchema:
    paginator = Paginator()
    posts = Post.objects(
        Post.author,
        Post.author.avatar,
        Post.image,
    ).order_by("created_at", ascending=False)
    paginated_data = await paginator.paginate_queryset(posts, page)
    return {"message": "Posts fetched", "data": paginated_data}
