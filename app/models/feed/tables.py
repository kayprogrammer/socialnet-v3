from enum import Enum
from piccolo.columns import Varchar, ForeignKey, OnDelete, Text, BigInt
from app.api.utils.file_processors import FileProcessor
from app.models.accounts.tables import User
from app.models.base.tables import BaseModel, File


class ReactionChoices(Enum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    HAHA = "HAHA"
    WOW = "WOW"
    SAD = "SAD"
    ANGRY = "ANGRY"


class FeedAbstract(BaseModel):
    author = ForeignKey(references=User, on_delete=OnDelete.cascade)
    text = Text()
    slug = Varchar(1000, unique=True)
    reactions_count = (
        BigInt()
    )  # Doing this because inverse foreignkey isn't available in this orm yet.

    def save(self, *args, **kwargs):
        self.slug = f"{self.author.first_name}-{self.author.last_name}-{self.id}"
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.author.full_name} ------ {self.text[:10]}..."


class Post(FeedAbstract):
    image = ForeignKey(File, on_delete=OnDelete.set_null, null=True, blank=True)
    comments_count = (
        BigInt()
    )  # Doing this because inverse foreignkey isn't available in this orm yet.

    @property
    def get_image(self):
        image = self.image
        if image and image.id:
            return FileProcessor.generate_file_url(
                key=image.id,
                folder="posts",
                content_type=image.resource_type,
            )
        return None


class Comment(BaseModel):
    post = ForeignKey(Post, on_delete=OnDelete.cascade)
    replies_count = (
        BigInt()
    )  # Doing this because inverse foreignkey isn't available in this orm yet.


class Reply(BaseModel):
    comment = ForeignKey(Comment, on_delete=OnDelete.cascade)


class Reaction(BaseModel):
    user = ForeignKey(User, on_delete=OnDelete.cascade)
    rtype = Varchar(20, choices=ReactionChoices)
    post = ForeignKey(Post, on_delete=OnDelete.set_null, null=True, blank=True)
    comment = ForeignKey(Comment, on_delete=OnDelete.set_null, null=True, blank=True)
    reply = ForeignKey(Reply, on_delete=OnDelete.set_null, null=True, blank=True)

    # So I'm supposed to use composite unique constraints somewhere around here but piccolo
    # has no provision currently for that (at least this  version) except by writing raw sql
    # in your migration files which is something I don't want to do. So I'll just focus on
    # doing very good validations. But there will be no db level constraints
    # I'll surely update this when they've updated the orm

    def __str__(self):
        return f"{self.user.full_name} ------ {self.rtype}"

    @property
    def targeted_obj(self):
        # Return object the reaction object is targeted to (post, comment, or reply)
        obj = self.post
        if not obj:
            obj = self.comment if self.comment else self.reply
        return obj
