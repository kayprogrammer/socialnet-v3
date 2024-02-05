from piccolo_admin.endpoints import TableConfig
from app.models.general.tables import SiteDetail
from app.models.accounts.tables import City, Country, Region, User
from app.models.chat.tables import Chat, Message
from app.models.feed.tables import Comment, Post, Reaction, Reply
from app.models.profiles.tables import Friend, Notification

# PROFILES
profiles = "Profiles"
user_visible_columns = [
    User.id,
    User.first_name,
    User.last_name,
    User.email,
    User.active,
    User.admin,
]
user_config = TableConfig(
    User,
    visible_columns=user_visible_columns,
    visible_filters=user_visible_columns,
    menu_group=profiles,
)

country_visible_columns = [Country.name, Country.code]
country_config = TableConfig(
    Country,
    visible_columns=country_visible_columns,
    visible_filters=country_visible_columns,
    menu_group=profiles,
    link_column=Country.name,
)

region_visible_columns = [Region.name, Region.country]
region_config = TableConfig(
    Region,
    visible_columns=region_visible_columns,
    visible_filters=region_visible_columns,
    menu_group=profiles,
    link_column=Region.name,
)

city_visible_columns = [City.name, City.region, City.country]
city_config = TableConfig(
    City,
    visible_columns=city_visible_columns,
    visible_filters=city_visible_columns,
    menu_group=profiles,
    link_column=City.name,
)

friend_visible_columns = [
    Friend.id,
    Friend.requester,
    Friend.requestee,
    Friend.status,
    Friend.created_at,
    Friend.updated_at,
]
friend_config = TableConfig(
    Friend,
    visible_columns=user_visible_columns,
    visible_filters=friend_visible_columns,
    menu_group=profiles,
)

notification_visible_columns = [
    Notification.id,
    Notification.sender,
    Notification.ntype,
    Notification.created_at,
    Notification.updated_at,
]
notification_config = TableConfig(
    Notification,
    visible_columns=notification_visible_columns,
    visible_filters=notification_visible_columns,
    menu_group=profiles,
)
# ----------------------------------------------------

# CHAT
chats = "Chats"
chat_visible_columns = [
    Chat.id,
    Chat.name,
    Chat.owner,
    Chat.ctype,
    Chat.created_at,
    Chat.updated_at,
]
chat_config = TableConfig(
    Chat,
    visible_columns=chat_visible_columns,
    visible_filters=chat_visible_columns,
    menu_group=chats,
)

message_visible_columns = [
    Message.id,
    Message.chat,
    Message.sender,
    Message.text,
    Message.updated_at,
]
message_config = TableConfig(
    Message,
    visible_columns=message_visible_columns,
    visible_filters=message_visible_columns,
    menu_group=chats,
)
# --------------------------------------------------

# FEED
feed = "Feed"
reaction_visible_columns = [Reaction.id, Reaction.user, Reaction.rtype]
reaction_config = TableConfig(
    Reaction,
    visible_columns=reaction_visible_columns,
    visible_filters=reaction_visible_columns,
    menu_group=feed,
)

post_visible_columns = [
    Post.id,
    Post.author,
    Post.slug,
    Post.created_at,
    Post.updated_at,
]
post_config = TableConfig(
    Post,
    visible_columns=post_visible_columns,
    visible_filters=post_visible_columns,
    menu_group=feed,
)

comment_visible_columns = [
    Comment.id,
    Comment.author,
    Comment.created_at,
    Comment.updated_at,
]
comment_config = TableConfig(
    Comment,
    visible_columns=comment_visible_columns,
    visible_filters=comment_visible_columns,
    menu_group=feed,
)

reply_visible_columns = [Reply.id, Reply.author, Reply.created_at, Reply.updated_at]
reply_config = TableConfig(
    Reply,
    visible_columns=reply_visible_columns,
    visible_filters=reply_visible_columns,
    menu_group=feed,
)
# --------------------------------------------------------

ALL_TABLE_CLASSES = [
    SiteDetail,
    user_config,
    country_config,
    region_config,
    city_config,
    friend_config,
    notification_config,
    chat_config,
    message_config,
    reaction_config,
    post_config,
    comment_config,
    reply_config,
]

# I've done my best. You can add custom forms, validations etc if you want.
