from app.core.config import settings
import websockets
import json
from app.api.schemas.profiles import NotificationSchema


def get_notification_message(obj):
    """This function returns a notification message"""
    ntype = obj.ntype
    message = f"{obj.sender.full_name} reacted to your post"
    if ntype == "REACTION":
        if obj.comment.id:
            message = f"{obj.sender.full_name} reacted to your comment"
        elif obj.reply.id:
            message = f"{obj.sender.full_name} reacted to your reply"
    elif ntype == "COMMENT":
        message = f"{obj.sender.full_name} commented on your post"
    elif ntype == "REPLY":
        message = f"{obj.sender.full_name} replied your comment"
    return message


async def sort_notification_slugs(notification):
    if notification.post.id:
        notification.post_slug = notification.post.slug
    elif notification.comment.id:
        notification.comment_slug = notification.comment.slug
        notification.post_slug = notification.comment.post.slug
    elif notification.reply.id:
        notification.reply_slug = notification.reply.slug
        notification.comment_slug = notification.reply.comment.slug
        notification.post_slug = notification.reply.comment.post.slug
    return notification


# Send notification in websocket
async def send_notification_in_socket(
    secured: bool, host: str, notification: object, status: str = "CREATED"
):
    websocket_scheme = "wss://" if secured else "ws://"
    uri = f"{websocket_scheme}{host}/api/v3/ws/notifications/"
    notification_data = {
        "id": str(notification.id),
        "status": status,
        "ntype": notification.ntype,
    }
    if status == "CREATED":
        notification = await sort_notification_slugs(notification)
        notification_data = notification_data | NotificationSchema.model_validate(
            notification
        ).model_dump(exclude={"id", "ntype"})
    headers = [
        ("Authorization", settings.SOCKET_SECRET),
    ]
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send a notification to the WebSocket server
        await websocket.send(json.dumps(notification_data))
        await websocket.close()
