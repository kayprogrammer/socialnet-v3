from enum import Enum
from piccolo.columns import (
    Varchar,
    ForeignKey,
    OnDelete,
    Text
)
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

class Post(FeedAbstract):
    image = ForeignKey(File, on_delete=OnDelete.set_null, null=True, blank=True)

    # def __str__(self):
    #     return f"{self.author.full_name} ------ {self.text[:10]}..."

    @property
    def get_image(self):
        image = self.image
        if image:
            return FileProcessor.generate_file_url(
                key=self.image_id,
                folder="posts",
                content_type=image.resource_type,
            )
        return None

class Comment(BaseModel):
    post = ForeignKey(Post, on_delete=OnDelete.cascade)

    # def __str__(self):
    #     return f"{self.author.full_name} ------ {self.text[:10]}..."


class Reply(BaseModel):
    comment = ForeignKey(Comment, on_delete=OnDelete.cascade)

    # def __str__(self):
    #     return f"{self.author.full_name} ------ {self.text[:10]}..."


class Reaction(BaseModel):
    user = ForeignKey(User, on_delete=OnDelete.cascade)
    rtype = Varchar(20, choices=ReactionChoices)
    post = ForeignKey(Post, on_delete=OnDelete.set_null, null=True, blank=True)
    comment = ForeignKey(Comment, on_delete=OnDelete.set_null, null=True, blank=True)
    reply = ForeignKey(Reply, on_delete=OnDelete.set_null, null=True, blank=True)

    # class Meta:
    #     ordering = ["-created_at"]
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["user", "post"],
    #             name="unique_user_post_reaction",
    #         ),
    #         models.UniqueConstraint(
    #             fields=["user", "comment"],
    #             name="unique_user_comment_reaction",
    #         ),
    #         models.UniqueConstraint(
    #             fields=["user", "reply"],
    #             name="unique_user_reply_reaction",
    #         ),
    #     ]

    def __str__(self):
        return f"{self.user.full_name} ------ {self.rtype}"

    @property
    def targeted_obj(self):
        # Return object the reaction object is targeted to (post, comment, or reply)
        obj = self.post
        if not obj:
            obj = self.comment if self.comment else self.reply
        return obj
