import re
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_current_user_or_guest
from app.api.schemas.base import ResponseSchema
from app.api.schemas.profiles import (
    CitiesResponseSchema,
    DeleteUserSchema,
    ProfileResponseSchema,
    ProfileUpdateResponseSchema,
    ProfileUpdateSchema,
    ProfilesResponseSchema,
)
from app.api.utils.file_processors import ALLOWED_IMAGE_TYPES
from app.api.utils.paginators import Paginator
from app.api.utils.utils import set_dict_attr
from app.common.handlers import ErrorCode, RequestError
from app.models.accounts.tables import City, User
from app.models.base.tables import File
from app.models.profiles.tables import Friend

router = APIRouter()
paginator = Paginator()


def get_users_queryset(current_user):
    users = User.objects(User.avatar, User.city)
    if current_user:
        users = users.where(User.id != current_user.id)
        # Right here I wanted to do some ordering by city and regions but that will not be a possibility
        # in piccolo orm, there'll probably be a provision for it in the future I guess.
    return users


@router.get(
    "",
    summary="Retrieve Users",
    description="This endpoint retrieves a paginated list of users",
)
async def retrieve_users(
    page: int = 1, user: User = Depends(get_current_user_or_guest)
) -> ProfilesResponseSchema:
    users = get_users_queryset(user)
    paginated_data = await paginator.paginate_queryset(users, page)
    return {"message": "Users fetched", "data": paginated_data}


@router.get(
    "/cities",
    summary="Retrieve Cities based on query params",
    description="This endpoint retrieves the first 10 cities that matches the query params",
)
async def retrieve_cities(name: str = None) -> CitiesResponseSchema:
    cities = []
    message = "Cities Fetched"
    if name:
        name = re.sub(r"[^\w\s]", "", name)  # Remove special chars
        cities = (
            await City.select(
                City.all_columns(),
                City.region.name.as_alias("region"),
                City.country.name.as_alias("country"),
            )
            .where(City.name.ilike(f"%{name}%"))
            .limit(10)
        )
    if len(cities) == 0:
        message = "No match found"
    return {"message": message, "data": cities}


@router.get(
    "/profile/{username}",
    summary="Retrieve user's profile",
    description="This endpoint retrieves a particular user profile",
)
async def retrieve_user_profile(username: str) -> ProfileResponseSchema:
    user = await User.objects(User.avatar, User.city).get(User.username == username)
    if not user:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="No user with that username",
            status_code=404,
        )
    return {"message": "User details fetched", "data": user}


@router.patch(
    "/profile",
    summary="Update user's profile",
    description=f"""
        This endpoint updates a particular user profile
        ALLOWED FILE TYPES: {", ".join(ALLOWED_IMAGE_TYPES)}
    """,
)
async def update_profile(
    data: ProfileUpdateSchema, user: User = Depends(get_current_user)
) -> ProfileUpdateResponseSchema:
    data = data.model_dump(exclude_none=True)
    # Validate City ID Entry
    city_id = data.pop("city_id", None)
    city = None
    if city_id:
        print("Halala")
        city = await City.objects().get(City.id == city_id)
        if not city:
            raise RequestError(
                err_code=ErrorCode.INVALID_ENTRY,
                err_msg="Invalid Entry",
                data={"city_id": "No city with that ID"},
                status_code=422,
            )
        data["city"] = city_id

    # Handle file upload
    image_upload_id = False
    file_type = data.pop("file_type", None)
    if file_type:
        # Create or update file object
        avatar = user.avatar
        if avatar:
            avatar.resource_type = file_type
            await avatar.save()
        else:
            avatar = await File.objects().create(resource_type=file_type)
        image_upload_id = avatar.id
        data["avatar"] = avatar

    # Set attributes from data to user object
    user = set_dict_attr(data, user)
    user.image_upload_id = image_upload_id
    await user.save()
    user.city = city  # Set city to object instead of ID for response sake
    return {"message": "User updated", "data": user}


@router.post(
    "/profile",
    summary="Delete user's account",
    description="This endpoint deletes a particular user's account (irreversible)",
)
async def delete_user(
    data: DeleteUserSchema, user: User = Depends(get_current_user)
) -> ResponseSchema:
    # Check if password is valid
    if not User.check_password(data.password, user.password):
        raise RequestError(
            err_code=ErrorCode.INVALID_CREDENTIALS,
            err_msg="Invalid Entry",
            status_code=422,
            data={"password": "Incorrect password"},
        )

    # Delete user
    await user.remove()
    return {"message": "User deleted"}


# FRIENDS


@router.get(
    "/friends",
    summary="Retrieve Friends",
    description="This endpoint retrieves friends of a user",
)
async def retrieve_friends(
    page: int = 1, user: User = Depends(get_current_user)
) -> ProfilesResponseSchema:
    friends = await Friend.objects().where(
        Friend.status == "ACCEPTED",
        (Friend.requester == user.id) | (Friend.requestee == user.id),
    )
    friend_ids = [
        friend.requester if friend.requester != user.id else friend.requestee
        for friend in friends
    ]
    friends = User.objects(User.avatar, User.city).where(User.id.is_in(friend_ids))

    # Return paginated data
    paginator.page_size = 20
    paginated_data = await paginator.paginate_queryset(friends, page)
    return {"message": "Friends fetched", "data": paginated_data}
