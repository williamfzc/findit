import cv2
import numpy as np
import imutils
import typing
import copy
import datetime
import tempfile
import contextlib
import os
from collections import namedtuple
from scipy.spatial.distance import euclidean

Point = namedtuple("Point", ("x", "y"))


def load_grey_from_path(pic_path: str) -> np.ndarray:
    """ load grey picture (with cv2) from path """
    assert os.path.isfile(pic_path), f"picture [{pic_path}] not existed"
    raw_img = cv2.imread(pic_path)
    return load_grey_from_cv2_object(raw_img)


def load_grey_from_cv2_object(pic_object: np.ndarray) -> np.ndarray:
    """ preparation for cv2 object (force turn it into gray) """
    pic_object = pic_object.astype(np.uint8)
    try:
        # try to turn it into grey
        grey_pic = cv2.cvtColor(pic_object, cv2.COLOR_BGR2GRAY)
    except cv2.error:
        # already grey
        return pic_object
    return grey_pic


def pre_pic(pic_path: str = None, pic_object: np.ndarray = None) -> np.ndarray:
    """ this method will turn pic path and pic object into grey pic object """
    if pic_object is not None:
        return load_grey_from_cv2_object(pic_object)
    return load_grey_from_path(pic_path)


def resize_pic_scale(pic_object: np.ndarray, target_scale: np.ndarray) -> np.ndarray:
    return imutils.resize(pic_object, width=int(pic_object.shape[1] * target_scale))


def turn_grey(old: np.ndarray) -> np.ndarray:
    try:
        return cv2.cvtColor(old, cv2.COLOR_RGB2GRAY)
    except cv2.error:
        return old


def decompress_point(old: typing.Tuple, compress_rate: float) -> typing.List:
    return [int(i / compress_rate) for i in old]


def compress_frame(
    old: np.ndarray,
    compress_rate: float = None,
    target_size: typing.Tuple[int, int] = None,
    not_grey: bool = None,
    interpolation: int = None,
) -> np.ndarray:
    """
    Compress frame

    :param old:
        origin frame

    :param compress_rate:
        before_pic * compress_rate = after_pic. default to 1 (no compression)
        eg: 0.2 means 1/5 size of before_pic

    :param target_size:
        tuple. (100, 200) means compressing before_pic to 100x200

    :param not_grey:
        convert into grey if True

    :param interpolation:
    :return:
    """

    target = turn_grey(old) if not not_grey else old
    if not interpolation:
        interpolation = cv2.INTER_AREA
    # target size first
    if target_size:
        return cv2.resize(target, target_size, interpolation=interpolation)
    # else, use compress rate
    # default rate is 1 (no compression)
    if not compress_rate:
        return target
    return cv2.resize(
        target, (0, 0), fx=compress_rate, fy=compress_rate, interpolation=interpolation
    )


def fix_location(shape: typing.Sequence, location: typing.Sequence) -> typing.Sequence:
    """ location from cv2 should be left-top location, and need to fix it and make it central """
    size_y, size_x = shape
    old_x, old_y = location
    return old_x + size_x / 2, old_y + size_y / 2


def mark_point(
    pic_object: np.ndarray, location: typing.Sequence, cover: bool = None
) -> np.ndarray:
    """ draw a mark on your picture, or your picture copy. """
    if not cover:
        pic_object = copy.deepcopy(pic_object)
    distance = 50
    target_x, target_y = map(int, location)
    start_point = (target_x - distance, target_y - distance)
    end_point = (target_x + distance, target_y + distance)
    cv2.rectangle(pic_object, start_point, end_point, -1)
    return pic_object


def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


@contextlib.contextmanager
def cv2file(pic_object: np.ndarray) -> str:
    """ save cv object to file, and return its path """
    temp_pic_file_object = tempfile.NamedTemporaryFile(
        mode="wb+", suffix=".png", delete=False
    )
    cv2.imwrite(temp_pic_file_object.name, pic_object)
    temp_pic_file_object_path = temp_pic_file_object.name
    yield temp_pic_file_object_path
    os.remove(temp_pic_file_object_path)


def point_list_filter(
    point_list: typing.Sequence, distance: float, point_limit: int = None
) -> typing.Sequence:
    """ remove some points which are too close """
    if not point_limit:
        point_limit = 20

    point_list = sorted(list(set(point_list)), key=lambda o: o[0])
    new_point_list = [point_list[0]]
    for cur_point in point_list[1:]:
        for each_confirmed_point in new_point_list:
            cur_distance = euclidean(cur_point, each_confirmed_point)
            # existed
            if cur_distance < distance:
                break
        else:
            new_point_list.append(cur_point)
            if len(new_point_list) >= point_limit:
                break
    return new_point_list


def debug_cv_object(target_object: np.ndarray, prefix: str) -> str:
    """ save target object as a temp picture, and return its path """
    mark_pic_path = f"{prefix}_{get_timestamp()}.png"
    cv2.imwrite(mark_pic_path, target_object)
    return mark_pic_path
