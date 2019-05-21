import os

import findit.server.config as config


# utils
def get_pic_path_by_name(pic_name: str) -> str:
    # auto fix ext name
    if '.' not in pic_name:
        pic_name += config.PIC_EXT_NAME

    result = os.path.join(config.PIC_DIR_PATH, pic_name)
    if not os.path.isfile(result):
        return ''
    return result


def handle_extras(extra_dict: dict) -> dict:
    """ filter for extras """

    # TODO need a filter? ... for safety
    # extra_dict_after_filter = {k: v for k, v in extra_dict.items() if k in config.ALLOWED_EXTRA_ARGS}

    # mask pic path
    mask_pic_path_key = 'mask_pic_path'
    if mask_pic_path_key in extra_dict:
        extra_dict[mask_pic_path_key] = get_pic_path_by_name(extra_dict[mask_pic_path_key])

    # and so on ...
    return extra_dict
