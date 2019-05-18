""" standalone server """
import os
import tempfile
import argparse
from flask import Flask, request, jsonify

from findit import FindIt

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', help="port number")
parser.add_argument('-d', '--dir', help="pictures root directory", required=True)
args = parser.parse_args()

# init pic dir
PIC_DIR_PATH = args.dir
assert os.path.exists(PIC_DIR_PATH), 'dir path not existed'


# utils
def get_pic_path_by_name(pic_name: str) -> str:
    result = os.path.join(PIC_DIR_PATH, pic_name)
    if not os.path.isfile(result):
        return ''
    return result


# init findit
fi = FindIt()

# init server
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello From FindIt Server"


@app.route("/analyse", methods=['POST'])
def analyse():
    template_name = request.form.get('template_name')
    template_path = get_pic_path_by_name(template_name)
    if not template_path:
        return jsonify({
            'error': 'no template named {}'.format(template_name)
        })

    # save target pic
    target_pic_file = request.files['file']
    temp_pic_file_object = tempfile.NamedTemporaryFile(mode='wb+', suffix='.png', delete=False)
    temp_pic_file_object.write(target_pic_file.read())
    temp_pic_file_object.close()

    fi.load_template('temp_template', pic_path=template_path)
    r = fi.find('temp_target', target_pic_path=temp_pic_file_object.name)

    # clean
    os.remove(temp_pic_file_object.name)
    fi.clear()

    return jsonify(r)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(args.port or 9410),
    )
