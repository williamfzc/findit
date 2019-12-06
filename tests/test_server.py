import pytest
import subprocess
import cv2
import time
import random

from findit_client import FindItStandardClient

# globals
TARGET_PATH = r"sample/pics/screen.png"
TEMPLATE_NAME = r"wechat_logo.png"
PORT = random.randint(9409, 11000)
find_it_client = None


@pytest.fixture(scope="session", autouse=True)
def life_time():
    start_cmd = [
        "python",
        "-m",
        "findit.server",
        "--dir",
        "sample/pics",
        "--port",
        str(PORT),
    ]
    server_process = subprocess.Popen(start_cmd)
    time.sleep(5)
    global find_it_client
    find_it_client = FindItStandardClient(port=PORT)
    yield
    server_process.terminate()
    server_process.kill()


def test_heartbeat():
    assert find_it_client.heartbeat()


def test_analyse_with_path():
    result = find_it_client.analyse_with_path(TARGET_PATH, TEMPLATE_NAME)

    arg_list = ["msg", "status", "request", "response", "data"]
    for each in arg_list:
        assert hasattr(result, each)
    assert result.template_engine.data


def test_analyse_with_extras():
    result = find_it_client.analyse_with_path(
        TARGET_PATH,
        TEMPLATE_NAME,
        a="123",
        b="456",
        pro_mode=True,
        engine_template_scale=(1, 4, 10),
    )

    request_dict = result.request

    assert "extras" in request_dict
    assert "a" in request_dict["extras"]
    assert "b" in request_dict["extras"]
    assert "engine_template_scale" in request_dict["extras"]


def test_analyse_without_template():
    result = find_it_client.analyse_with_path(TARGET_PATH, None, engine=["ocr"])
    assert result.ocr_engine.data
