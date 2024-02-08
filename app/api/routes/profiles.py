import re
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_current_user_or_guest
from app.api.routes.utils import (
    get_notifications_queryset,
    get_requestee_and_friend_obj,
)
from app.api.schemas.base import ResponseSchema
from app.api.schemas.profiles import (
    AcceptFriendRequestSchema,
    CitiesResponseSchema,
    DeleteUserSchema,
    NotificationsResponseSchema,
    ProfileResponseSchema,
    ProfileUpdateResponseSchema,
    ProfileUpdateSchema,
    ProfilesResponseSchema,
    ReadNotificationSchema,
    SendFriendRequestSchema,
)
from app.api.utils.file_processors import ALLOWED_IMAGE_TYPES
from app.api.utils.paginators import Paginator
from app.api.utils.utils import set_dict_attr
from app.common.handlers import ErrorCode, RequestError
from app.models.accounts.tables import City, User
from app.models.base.tables import File
from app.models.profiles.tables import Friend, Notification

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
    if not cities:
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
        if avatar.id:
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
    friends = await Friend.select(Friend.requester, Friend.requestee).where(
        Friend.status == "ACCEPTED",
        (Friend.requester == user.id) | (Friend.requestee == user.id),
    )
    friend_ids = [
        friend["requester"] if friend["requester"] != user.id else friend["requestee"]
        for friend in friends
    ]
    friends = []
    if friend_ids:
        friends = User.objects(User.avatar, User.city).where(User.id.is_in(friend_ids))

    # Return paginated data
    paginator.page_size = 20
    paginated_data = await paginator.paginate_queryset(friends, page)
    return {"message": "Friends fetched", "data": paginated_data}


@router.get(
    "/friends/requests",
    summary="Retrieve Friend Requests",
    description="This endpoint retrieves friend requests of a user",
)
async def retrieve_friend_requests(
    page: int = 1, user: User = Depends(get_current_user)
) -> ProfilesResponseSchema:
    pending_friends = await Friend.select(Friend.requester).where(
        Friend.requestee == user.id, Friend.status == "PENDING"
    )
    pending_friend_ids = [friend["requester"] for friend in pending_friends]
    friends = []
    if pending_friend_ids:
        friends = User.objects(User.avatar, User.city).where(
            User.id.is_in(pending_friend_ids)
        )

    # Return paginated data
    paginator.page_size = 20
    paginated_data = await paginator.paginate_queryset(friends, page)
    return {"message": "Friend Requests fetched", "data": paginated_data}


@router.post(
    "/friends/requests",
    summary="Send Or Delete Friend Request",
    description="This endpoint sends or delete friend requests",
    responses={201: {"model": ResponseSchema}, 200: {"model": ResponseSchema}},
)
async def send_or_delete_friend_request(
    data: SendFriendRequestSchema, user: User = Depends(get_current_user)
) -> ResponseSchema:
    requestee, friend = await get_requestee_and_friend_obj(user, data.username)
    message = "Friend Request sent"
    status_code = 201
    if friend:
        status_code = 200
        message = "Friend Request removed"
        if friend.status == "ACCEPTED":
            message = "This user is already your friend"
        elif user.id != friend.requester:
            raise RequestError(
                err_code=ErrorCode.NOT_ALLOWED,
                err_msg="The user already sent you a friend request!",
                status_code=403,
            )
        else:
            await friend.remove()
    else:
        await Friend.objects().create(requester=user.id, requestee=requestee.id)

    return {"message": message, "status_code": status_code}


@router.put(
    "/friends/requests",
    summary="Accept Or Reject a Friend Request",
    description="""
        This endpoint accepts or reject a friend request
        accepted choices:
        - If true, then it was accepted
        - If false, then it was rejected
    """,
)
async def accept_or_reject_friend_request(
    data: AcceptFriendRequestSchema, user: User = Depends(get_current_user)
) -> ResponseSchema:
    _, friend = await get_requestee_and_friend_obj(user, data.username, "PENDING")
    if not friend:
        raise RequestError(
            err_code=ErrorCode.NON_EXISTENT,
            err_msg="No friend request exist between you and that user",
            status_code=404,
        )
    if friend.requester == user.id:
        raise RequestError(
            err_code=ErrorCode.NOT_ALLOWED,
            err_msg="You cannot accept or reject a friend request you sent ",
            status_code=403,
        )

    # Update or delete friend request based on status
    accepted = data.accepted
    if accepted:
        msg = "Accepted"
        friend.status = "ACCEPTED"
        await friend.save()
    else:
        msg = "Rejected"
        await friend.remove()
    return {"message": f"Friend Request {msg}"}


@router.get(
    "/notifications",
    summary="Retrieve Auth User Notifications",
    description="""
        This endpoint retrieves a paginated list of auth user's notifications
        Note:
            - Use post slug to navigate to the post.
            - Use comment slug to navigate to the comment.
            - Use reply slug to navigate to the reply.

        WEBSOCKET ENDPOINT: /api/v4/ws/notifications/ e.g (ws://{host}/api/v4/ws/notifications/) 
            NOTE:
            * This endpoint requires authorization, so pass in the Authorization header with Bearer and its value.
            * You can only read and not send notification messages into this socket.
    """,
)
async def retrieve_user_notifications(
    page: int = 1, user: User = Depends(get_current_user)
) -> NotificationsResponseSchema:
    notifications = get_notifications_queryset(user)

    # Return paginated data and set is_read to every item
    paginated_data = await paginator.paginate_queryset(notifications, page)
    items = paginated_data["items"]
    for item in items:
        item.is_read = True if user.id in item.read_by_ids else False
    return {"message": "Notifications fetched", "data": paginated_data}


@router.post(
    "/notifications",
    summary="Read Notification",
    description="""
        This endpoint reads a notification
    """,
)
async def read_notification(
    data: ReadNotificationSchema, user: User = Depends(get_current_user)
) -> ResponseSchema:
    id = data.id
    mark_all_as_read = data.mark_all_as_read

    resp_message = "Notifications read"
    if mark_all_as_read:
        notifications = await Notification.select(
            Notification.id, Notification.read_by_ids
        ).where(Notification.receiver_ids.any(user.id))
        notification_ids_to_update = [
            notification["id"]
            for notification in notifications
            if not user.id in notification["read_by_ids"]
        ]
        # Mark all notifications as read
        if len(notification_ids_to_update) > 0:
            await Notification.update(
                {Notification.read_by_ids: Notification.read_by_ids + user.id}
            ).where(Notification.id.is_in(notification_ids_to_update))
    elif id:
        # Mark single notification as read
        notification = (
            await Notification.objects()
            .where(Notification.receiver_ids.any(user.id), Notification.id == id)
            .first()
        )
        if not notification:
            raise RequestError(
                err_code=ErrorCode.NON_EXISTENT,
                err_msg="User has no notification with that ID",
                status_code=404,
            )
        if not user.id in notification.read_by_ids:
            notification.read_by_ids.append(user.id)
            await notification.save()
        resp_message = "Notification read"
    return {"message": resp_message}
