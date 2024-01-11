from fastapi import APIRouter, BackgroundTasks, Depends
from app.api.deps import get_current_user
from app.api.schemas.feed import (
    PostInputResponseSchema,
    PostInputSchema,
    PostsResponseSchema,
)
from app.api.utils.auth import Authentication
from app.api.utils.file_processors import ALLOWED_IMAGE_TYPES
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
    "/posts/",
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
