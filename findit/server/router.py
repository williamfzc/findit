""" standalone server """
import os
import tempfile
import json
from collections import namedtuple
from flask import Flask, request, jsonify

from findit import FindIt
import findit.server.config as config
import findit.server.utils as utils

# standard response
_FindItResponse = namedtuple('FindItResponse', ('status', 'msg', 'request', 'response'))
STATUS_OK = 'OK'
STATUS_CLIENT_ERROR = 'CLIENT_ERROR'
STATUS_SERVER_ERROR = 'SERVER_ERROR'


def std_response(**kwargs):
    _response = _FindItResponse(**kwargs)
    return jsonify(_response._asdict())


# init server
app = Flask(__name__)


@app.route("/")
def hello():
    return std_response(
        status=STATUS_OK,
        msg='hello from findit :) response will always contains status/msg/request/response.',
        request=request.form,
        response={
            'hello': 'world',
        }
    )


@app.route("/analyse", methods=['POST'])
def analyse():
    # required
    template_name = request.form.get('template_name')
    template_path = utils.get_pic_path_by_name(template_name)
    if not template_path:
        return std_response(
            status=STATUS_CLIENT_ERROR,
            msg='no template named {}'.format(template_name),
            request=request.form,
            response='',
        )

    # optional
    extra_dict = json.loads(request.form.get('extras'))
    new_extra_dict = utils.handle_extras(extra_dict)

    # save target pic
    target_pic_file = request.files['file']
    temp_pic_file_object = tempfile.NamedTemporaryFile(mode='wb+', suffix='.png', delete=False)
    temp_pic_file_object.write(target_pic_file.read())
    temp_pic_file_object.close()

    # init findit
    fi = FindIt(need_log=True, **new_extra_dict)
    fi.load_template(template_name, pic_path=template_path)
    _response = fi.find(
        config.DEFAULT_TARGET_NAME,
        target_pic_path=temp_pic_file_object.name,
        **new_extra_dict
    )

    # clean
    os.remove(temp_pic_file_object.name)

    return std_response(
        status=STATUS_OK,
        msg='',
        request=request.form,
        response=_response,
    )
