from app.core.config import settings
from app.api.schemas.profiles import NotificationSchema
import websockets, json, os


def get_notification_message(obj):
    """This function returns a notification message"""
    ntype = obj.ntype
    sender = obj.sender.full_name
    message = f"{sender} reacted to your post"
    if ntype == "REACTION":
        if obj.comment.id:
            message = f"{sender} reacted to your comment"
        elif obj.reply.id:
            message = f"{sender} reacted to your reply"
    elif ntype == "COMMENT":
        message = f"{sender} commented on your post"
    elif ntype == "REPLY":
        message = f"{sender} replied your comment"
    return message


# Send notification in websocket
async def send_notification_in_socket(
    secured: bool, host: str, notification: object, status: str = "CREATED"
):
    if os.environ["ENVIRONMENT"] == "testing":
        return
    websocket_scheme = "wss://" if secured else "ws://"
    uri = f"{websocket_scheme}{host}/api/v3/ws/notifications"
    notification_data = {
        "id": str(notification.id),
        "status": status,
        "ntype": notification.ntype,
    }
    if status == "CREATED":
        notification_data = notification_data | NotificationSchema.model_validate(
            notification
        ).model_dump(exclude={"id", "ntype"}, by_alias=True)
    headers = [
        ("Authorization", settings.SOCKET_SECRET),
    ]
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send a notification to the WebSocket server
        await websocket.send(json.dumps(notification_data))
        await websocket.close()
