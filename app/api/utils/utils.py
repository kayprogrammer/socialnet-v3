from typing import Dict


def set_key_prefix(dict_val: Dict, prefix):
    return {
        f"{prefix}.{key}": value for key, value in dict_val.items()
    }  # This prefixes every key with the model


def set_dict_attr(dict_val: Dict, obj):
    for key, value in dict_val.items():
        setattr(obj, key, value)
    return obj
