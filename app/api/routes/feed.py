from fastapi import APIRouter, BackgroundTasks, Depends
from app.api.deps import get_current_user
from app.api.routes.utils import get_post_object
from app.api.schemas.feed import (
    PostInputResponseSchema,
    PostInputSchema,
    PostResponseSchema,
    PostsResponseSchema,
)
from app.api.utils.auth import Authentication
from app.api.utils.file_processors import ALLOWED_IMAGE_TYPES
from app.api.utils.paginators import Paginator
from app.api.utils.utils import set_dict_attr
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
    post = await get_post_object(slug) # simple post object
    if post.author != user.id:
        raise RequestError(
            err_code=ErrorCode.INVALID_OWNER,
            err_msg="This Post isn't yours",
        )
    await post.remove()
    return {"message": "Post deleted"}
