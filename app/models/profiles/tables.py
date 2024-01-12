from enum import Enum
from app.api.utils.notification import get_notification_message
from app.models.accounts.tables import User
from app.models.base.tables import BaseModel
from piccolo.columns import (
    Varchar,
    ForeignKey,
    OnDelete,
    LazyTableReference,
)
from piccolo.columns.m2m import M2M

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
    receivers = M2M(
        LazyTableReference("NotificationToUserReceiver", module_path=__name__)
    )
    ntype = Varchar(100, choices=NotificationTypeChoices)
    post = ForeignKey(references=Post, on_delete=OnDelete.cascade, null=True)
    comment = ForeignKey(references=Comment, on_delete=OnDelete.cascade, null=True)
    reply = ForeignKey(references=Reply, on_delete=OnDelete.cascade, null=True)
    text = Varchar(100, null=True)
    read_by = M2M(LazyTableReference("NotificationToUserRead", module_path=__name__))

    def __str__(self):
        return str(self.id)

    @property
    def message(self):
        text = self.text
        if not text:
            text = get_notification_message(self)
        return text

    # So I'm supposed to do some check constraints somewhere around here but piccolo
    # has no provision currently for that (at least this  version) except by writing raw sql
    # in your migration files which is something I don't want to do. So I'll just focus on
    # doing very good validations. But there will be no db level constraints
    # I'll surely update this when they've updated the orm


class NotificationToUserReceiver(BaseModel):
    user = ForeignKey(User)
    notification = ForeignKey(Notification)


class NotificationToUserRead(BaseModel):
    user = ForeignKey(User)
    notification = ForeignKey(Notification)
