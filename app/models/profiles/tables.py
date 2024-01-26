from enum import Enum
from app.api.utils.notification import get_notification_message
from app.models.accounts.tables import User
from app.models.base.tables import BaseModel
from piccolo.columns import Varchar, ForeignKey, OnDelete, Array, UUID

from app.models.feed.tables import Comment, Post, Reply


class RequestStatusChoices(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"


class Friend(BaseModel):
    requester = ForeignKey(references=User, on_delete=OnDelete.cascade)
    requestee = ForeignKey(references=User, on_delete=OnDelete.cascade)
    status = Varchar(20, default="PENDING", choices=RequestStatusChoices)

    def __str__(self):
        return (
            f"{self.requester.full_name} & {self.requestee.full_name} --- {self.status}"
        )

    # So I'm supposed to do some bidirectional composite unique constraints somewhere around here but piccolo
    # has no provision currently for that (at least this  version) except by writing raw sql
    # in your migration files which is something I don't want to do. So I'll just focus on
    # doing very good validations. But there will be no db level constraints
    # I'll surely update this when they've updated the orm


class NotificationTypeChoices(Enum):
    REACTION = "REACTION"
    COMMENT = "COMMENT"
    REPLY = "REPLY"
    ADMIN = "ADMIN"


class Notification(BaseModel):
    sender = ForeignKey(references=User, on_delete=OnDelete.cascade, null=True)
    receiver_ids = Array(
        base_column=UUID()
    )  # IDs of users that has received the notification
    ntype = Varchar(100, choices=NotificationTypeChoices)
    post = ForeignKey(references=Post, on_delete=OnDelete.cascade, null=True)
    comment = ForeignKey(references=Comment, on_delete=OnDelete.cascade, null=True)
    reply = ForeignKey(references=Reply, on_delete=OnDelete.cascade, null=True)
    text = Varchar(100, null=True)
    read_by_ids = Array(
        base_column=UUID()
    )  # IDs of users that has read the notification

    def __str__(self):
        return str(self.id)

    @property
    def message(self):
        text = self.text
        if not text:
            text = get_notification_message(self)
        return text

    @property
    def post_slug(self):
        return self.post.slug if self.post else None

    @property
    def comment_slug(self):
        return self.comment.slug if self.comment else None

    @property
    def reply_slug(self):
        return self.reply.slug if self.reply else None

    # So I'm supposed to do some check constraints somewhere around here but piccolo
    # has no provision currently for that (at least this  version) except by writing raw sql
    # in your migration files which is something I don't want to do. So I'll just focus on
    # doing very good validations. But there will be no db level constraints
    # I'll surely update this when they've updated the orm
