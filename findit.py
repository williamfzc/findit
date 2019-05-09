import cv2
import os
import imutils
import numpy as np
import typing


def load_grey_from_path(pic_path: str) -> np.ndarray:
    """ load grey picture (with cv2) from path """
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


def fix_location(pic_object: np.ndarray, location: typing.Sequence):
    """ location from cv2 should be left-top location, and need to fix it and make it central """
    size_x, size_y = pic_object.shape
    old_x, old_y = location
    return old_x + size_x / 2, old_y + size_y / 2


class FindItConfig(object):
    """ DEPRECATED: cv method is always cv2.TM_CCORR_NORMED """
    cv_method = None


class FindIt(object):
    """ FindIt Operator """

    """
    Default cv method is TM_CCORR_NORMED, and CANNOT be changed. 
    
    1. Opencv support only CV_TM_CCORR_NORMED & CV_TM_SQDIFF
        (https://stackoverflow.com/questions/35658323/python-opencv-matchtemplate-is-mask-feature-implemented)
    2. Personally I do not want to use SQDIFF series. Its max value is totally different from what we thought.
    3. TM_CCORR_NORMED always (I think) works fine.
    """
    CV_METHOD_NAME = 'cv2.TM_CCORR_NORMED'
    CV_METHOD_CODE = eval(CV_METHOD_NAME)

    def __init__(self):
        # template pic dict,
        # { pic_name: pic_cv_object }
        self.template: typing.Dict[str, np.ndarray] = dict()

    def load_template(self,
                      pic_path: str = None,
                      pic_object_list: typing.Sequence = None):
        """ load template picture """
        assert (pic_path is not None) or (pic_object_list is not None), 'need path or cv object'

        if pic_object_list is not None:
            # pic_object: ('pic_name', cv_object)
            pic_name: str = pic_object_list[0]
            pic_object: np.ndarray = pic_object_list[1]
            self.template[pic_name] = load_grey_from_cv2_object(pic_object)
            return

        abs_path = os.path.abspath(pic_path)
        self.template[abs_path] = load_grey_from_path(abs_path)

    def find(self,
             target_pic_path: str = None,
             target_pic_object: np.ndarray = None,
             mask_pic_path: str = None,
             mask_pic_object: np.ndarray = None,
             scale: typing.Sequence = None):
        """
        start match

        :param target_pic_path:
        :param target_pic_object:
        :param mask_pic_path:
        :param mask_pic_object:
        :param scale:
        :return:
        """

        # pre assert
        assert self.template, 'template is empty'
        assert (target_pic_path is not None) or (target_pic_object is not None), 'need path or cv object'

        # load target
        target_pic_object = pre_pic(target_pic_path, target_pic_object)

        # mask
        if mask_pic_path or mask_pic_object is not None:
            mask_pic_object = pre_pic(mask_pic_path, mask_pic_object)

        result: typing.List[dict] = list()
        for each_template_path, each_template_object in self.template.items():
            # default scale
            if not scale:
                scale = (1, 3, 10)

            min_val, max_val, min_loc, max_loc = self.compare(
                target_pic_object,
                each_template_object,
                scale,
                mask_pic_object
            )
            min_loc, max_loc = map(lambda i: fix_location(each_template_object, i), [min_loc, max_loc])

            # add to result list
            result.append({
                'path': each_template_path,
                'min_val': min_val,
                'max_val': max_val,
                'min_loc': min_loc,
                'max_loc': max_loc,
            })

        return {
            'target_path': target_pic_path,
            'cv_method': self.CV_METHOD_NAME,
            'data': result,
        }

    def compare(self,
                target_pic_object: np.ndarray,
                template_pic_object: np.ndarray,
                scale: typing.Sequence,
                mask_pic_object: np.ndarray = None) -> typing.Sequence[float]:
        """
        match template between picture and template
        (https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/)

        :param target_pic_object:
        :param template_pic_object:
        :param scale: default to (1, 3, 10)
        :param mask_pic_object:
        :return: min_val, max_val, min_loc, max_loc
        """
        pic_height, pic_width = target_pic_object.shape[:2]
        result_list = list()

        for each_scale in np.linspace(*scale):
            # resize template
            resize_template_pic_object = resize_pic_scale(template_pic_object, each_scale)

            # resize mask
            if mask_pic_object is not None:
                resize_mask_pic_object = resize_pic_scale(mask_pic_object, each_scale)
            else:
                resize_mask_pic_object = None

            # if template's size is larger than raw picture, break
            if resize_template_pic_object.shape[0] > pic_height or resize_template_pic_object.shape[1] > pic_width:
                break

            res = cv2.matchTemplate(
                target_pic_object,
                resize_template_pic_object,
                self.CV_METHOD_CODE,
                mask=resize_mask_pic_object)
            result_list.append(cv2.minMaxLoc(res))

        # return the max one
        return sorted(result_list, key=lambda i: i[1])[-1]

    def reset(self):
        """ reset template, target and result """
        self.template = dict()
