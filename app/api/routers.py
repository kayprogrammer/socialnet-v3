from fastapi import APIRouter
from app.api.routes import general, auth, feed, profiles, chat

main_router = APIRouter()
main_router.include_router(general.router, prefix="/general", tags=["General"])
main_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
main_router.include_router(feed.router, prefix="/feed", tags=["Feed"])
main_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
main_router.include_router(chat.router, prefix="/chats", tags=["Chats"])
