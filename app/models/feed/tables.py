from enum import Enum
from uuid import UUID
from piccolo.columns import Varchar, ForeignKey, OnDelete, Text, BigInt
from slugify import slugify
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
    reactions_count = BigInt(
        default=0
    )  # Doing this because inverse foreignkey isn't available in this orm yet.

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.author.full_name} {self.id}")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.author.full_name} ------ {self.text[:10]}..."


class Post(FeedAbstract):
    image = ForeignKey(File, on_delete=OnDelete.set_null, null=True, blank=True)
    comments_count = BigInt(
        default=0
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


class Comment(FeedAbstract):
    post = ForeignKey(Post, on_delete=OnDelete.cascade)
    replies_count = BigInt(
        default=0
    )  # Doing this because inverse foreignkey isn't available in this orm yet.

    def save(self, *args, **kwargs):
        if not self._exists_in_db:
            # Update comments count for post when created
            post = self.post
            post_id = post if isinstance(post, UUID) else post.id
            Post.update({Post.comments_count: Post.comments_count + 1}).where(
                Post.id == post_id
            ).run_sync()
        return super().save(*args, **kwargs)


class Reply(FeedAbstract):
    comment = ForeignKey(Comment, on_delete=OnDelete.cascade)


class Reaction(BaseModel):
    user = ForeignKey(User, on_delete=OnDelete.cascade)
    rtype = Varchar(20, choices=ReactionChoices)
    post = ForeignKey(Post, on_delete=OnDelete.set_null, null=True, blank=True)
    comment = ForeignKey(Comment, on_delete=OnDelete.set_null, null=True, blank=True)
    reply = ForeignKey(Reply, on_delete=OnDelete.set_null, null=True, blank=True)
    _targeted_obj_class = Post
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
            obj = self.comment or self.reply
            if self.comment:
                self._targeted_obj_class = Comment
            else:
                self._targeted_obj_class = Reply
        return obj

    def save(self, *args, **kwargs):
        targeted_obj = (
            self.targeted_obj
        )  # Must stay on top to ensure the right targeted obj class
        model: Post | Comment | Reply = (
            self._targeted_obj_class
        )  # e.g Post, Comment, Reply
        if not self._exists_in_db:
            targeted_obj_id = (
                targeted_obj if isinstance(targeted_obj, UUID) else targeted_obj.id
            )
            # If creation, update reactions count
            model.update({model.reactions_count: model.reactions_count + 1}).where(
                model.id == targeted_obj_id
            ).run_sync()
        return super().save(*args, **kwargs)
