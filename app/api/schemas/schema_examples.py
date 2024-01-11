class UserExample:
    first_name = "John"
    last_name = "Doe"
    username = "john-doe"
    email = "johndoe@example.com"
    password = "strongpassword"
    avatar = "https://img.url"


token_example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

file_upload_data = {
    "public_id": "d23dde64-a242-4ed0-bd75-4c759624b3a6",
    "signature": "djsdsjAushsh",
    "timestamp": "16272637829",
}

user_data = {
    "name": f"{UserExample.first_name} {UserExample.last_name}",
    "username": UserExample.username,
    "avatar": UserExample.avatar,
}

latest_message_data = {
    "sender": user_data,
    "text": "Cool text",
    "file": "https://img.url",
}


class PostExample:
    slug = "john-doe-d10dde64-a242-4ed0-bd75-4c759644b3a6"
    file = "https://img.url"
