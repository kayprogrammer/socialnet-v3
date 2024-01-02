from typing import Dict

from app.api.utils.file_processors import ALLOWED_FILE_TYPES, ALLOWED_IMAGE_TYPES


def set_key_prefix(dict_val: Dict, prefix):
    return {
        f"{prefix}.{key}": value for key, value in dict_val.items()
    }  # This prefixes every key with the model


def set_dict_attr(dict_val: Dict, obj):
    for key, value in dict_val.items():
        setattr(obj, key, value)
    return obj

def validate_image_type(value):
    if value and value not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Image type not allowed!")
    return value


def validate_file_type(value):
    if value and value not in ALLOWED_FILE_TYPES:
        raise ValueError("File type not allowed!")
    return value
