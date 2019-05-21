""" standalone server """
import os
import tempfile
import json
from flask import Flask, request, jsonify

from findit import FindIt
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
    extra_dict_after_filter = {k: v for k, v in extra_dict.items() if k in config.ALLOWED_EXTRA_ARGS}

    # mask pic path
    mask_pic_path_key = 'mask_pic_path'
    if mask_pic_path_key in extra_dict_after_filter:
        extra_dict_after_filter[mask_pic_path_key] = get_pic_path_by_name(
            extra_dict_after_filter[mask_pic_path_key])

    # and so on ...

    return extra_dict_after_filter


# init server
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello From FindIt Server"


@app.route("/analyse", methods=['POST'])
def analyse():
    # required
    template_name = request.form.get('template_name')
    template_path = get_pic_path_by_name(template_name)
    if not template_path:
        return jsonify({
            'error': 'no template named {}'.format(template_name)
        })

    # optional
    extra_dict = json.loads(request.form.get('extras'))
    new_extra_dict = handle_extras(extra_dict)

    # save target pic
    target_pic_file = request.files['file']
    temp_pic_file_object = tempfile.NamedTemporaryFile(mode='wb+', suffix='.png', delete=False)
    temp_pic_file_object.write(target_pic_file.read())
    temp_pic_file_object.close()

    # init findit
    fi = FindIt(**new_extra_dict)
    fi.load_template(template_path, pic_path=template_path)
    _response = fi.find(
        config.DEFAULT_TARGET_NAME,
        target_pic_path=temp_pic_file_object.name,
        **new_extra_dict
    )

    # clean
    os.remove(temp_pic_file_object.name)

    return jsonify({
        'request': request.form,
        'response': _response,
    })
