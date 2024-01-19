import re
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Request
from app.api.deps import get_current_user, get_current_user_or_guest
from app.api.schemas.profiles import CitiesResponseSchema, ProfilesResponseSchema
from app.api.utils.paginators import Paginator
from app.models.accounts.tables import City, User

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
