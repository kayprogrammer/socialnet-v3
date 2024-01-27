from enum import Enum
from app.api.schemas.base import UserDataSchema
from app.api.utils.file_processors import FileProcessor
from app.models.accounts.tables import User
from app.models.base.tables import BaseModel, File
from piccolo.columns import Varchar, ForeignKey, OnDelete, Array, UUID, Text


class ChatChoices(Enum):
    DM = "DM"
    GROUP = "GROUP"


class Chat(BaseModel):
    name = Varchar(length=100, null=True)
    owner = ForeignKey(references=User, on_delete=OnDelete.cascade)
    ctype = Varchar(10, default="DM", choices=ChatChoices)
    user_ids = Array(
        base_column=UUID(default=None)
    )  # IDs of users that are part of the chat
    description = Varchar(length=1000, null=True)
    image = ForeignKey(references=File, on_delete=OnDelete.set_null, null=True)
    latest_message_id = UUID(default=None, null=True)
    _latest_message_obj = None

    def __str__(self):
        return str(self.id)

    @property
    def get_image(self):
        image = self.image
        if image.id:
            return FileProcessor.generate_file_url(
                key=image.id,
                folder="chats",
                content_type=image.resource_type,
            )
        return None

    @property
    def latest_message(self):
        message: Message = self._latest_message_obj
        if message:
            message = {
                "sender": UserDataSchema.model_validate(message.sender).model_dump(
                    by_alias=True
                ),
                "text": message.text,
                "file": message.get_file,
            }
        return message

    # So I'm supposed to do some bidirectional composite unique constraints somewhere around here but piccolo
    # has no provision currently for that (at least this  version) except by writing raw sql
    # in your migration files which is something I don't want to do. So I'll just focus on
    # doing very good validations. But there will be no db level constraints
    # I'll surely update this when they've updated the orm


class Message(BaseModel):
    chat = ForeignKey(references=Chat, on_delete=OnDelete.cascade)
    sender = ForeignKey(references=User, on_delete=OnDelete.cascade)
    text = Text(null=True)
    file = ForeignKey(references=File, on_delete=OnDelete.set_null, null=True)

    def save(self, *args, **kwargs):
        if not self._exists_in_db:
            # Update the chat latest message ID
            Chat.update({Chat.latest_message_id: self.id}).where(
                Chat.id == self.chat
            ).run_sync()
        return super().save(*args, **kwargs)

    @property
    def get_file(self):
        file = self.file
        if file.id:
            return FileProcessor.generate_file_url(
                key=file.id,
                folder="messages",
                content_type=file.resource_type,
            )
        return None
