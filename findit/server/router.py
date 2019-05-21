""" standalone server """
import os
import tempfile
import json
from flask import Flask, request, jsonify

from findit import FindIt
import findit.server.config as config
import findit.server.utils as utils


# init server
app = Flask(__name__)


@app.route("/")
def hello():
    # TODO standard response, eg: status/msg and something else
    return "Hello From FindIt Server"


@app.route("/analyse", methods=['POST'])
def analyse():
    # required
    template_name = request.form.get('template_name')
    template_path = utils.get_pic_path_by_name(template_name)
    if not template_path:
        return jsonify({
            'error': 'no template named {}'.format(template_name)
        })

    # optional
    extra_dict = json.loads(request.form.get('extras'))
    new_extra_dict = utils.handle_extras(extra_dict)

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
        'request': request,
        'response': _response,
    })
