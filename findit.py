import cv2
import os
import imutils
import numpy as np
import typing
import json
from loguru import logger


# default: no log
LOGGER_FLAG = 'findit'
logger.disable(LOGGER_FLAG)


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


class FindIt(object):
    """ FindIt Operator """

    """
    Default cv method is TM_CCORR_NORMED
    
    1. Opencv support only CV_TM_CCORR_NORMED & CV_TM_SQDIFF
        (https://stackoverflow.com/questions/35658323/python-opencv-matchtemplate-is-mask-feature-implemented)
    2. Personally I do not want to use SQDIFF series. Its max value is totally different from what we thought.
    """
    DEFAULT_CV_METHOD_NAME = 'cv2.TM_CCORR_NORMED'

    def __init__(self,
                 cv_method_name: str = None,
                 need_log: bool = None):
        # template pic dict,
        # { pic_name: pic_cv_object }
        self.template: typing.Dict[str, np.ndarray] = dict()

        # init logger
        self.switch_logger(bool(need_log))

        # set cv method
        self._cv_method_name: str = None
        self._cv_method_code: int = None

        if cv_method_name is None:
            cv_method_name = self.DEFAULT_CV_METHOD_NAME
        self.set_cv_method(cv_method_name)

    def set_cv_method(self, method_name: str):
        """ change cv method, for match template. eg: FindIt.set_cv_method('cv2.TM_CCOEFF_NORMED') """
        self._cv_method_name = method_name
        self._cv_method_code = eval(method_name)
        logger.info('CV method: {}'.format(method_name))

    @staticmethod
    def switch_logger(status: bool):
        """ enable or disable logger """
        if status:
            logger.enable(LOGGER_FLAG)
            logger.info('logger up')
        else:
            logger.disable(LOGGER_FLAG)

    def load_template(self,
                      pic_path: str = None,
                      pic_object_list: typing.Sequence = None):
        """
        load template picture

        :param pic_path: eg: '../your_picture.png'
        :param pic_object_list: eg: ('your_picture_name', your_pic_cv_object)
        :return:
        """
        assert (pic_path is not None) or (pic_object_list is not None), 'need path or cv object'

        if pic_object_list is not None:
            logger.info('load template from picture object directly ...')
            # pic_object: ('pic_name', cv_object)
            pic_name: str = pic_object_list[0]
            pic_object: np.ndarray = pic_object_list[1]
            self.template[pic_name] = load_grey_from_cv2_object(pic_object)
        else:
            logger.info('load template from picture path ...')
            abs_path = os.path.abspath(pic_path)
            pic_name = abs_path
            self.template[abs_path] = load_grey_from_path(abs_path)
        logger.info('load template [{}] successfully'.format(pic_name))

    def find(self,
             target_pic_path: str = None,
             target_pic_object: np.ndarray = None,
             mask_pic_path: str = None,
             mask_pic_object: np.ndarray = None,
             scale: typing.Sequence = None):
        """
        start match

        :param target_pic_path: '/path/to/your/target.png'
        :param target_pic_object: your_pic_cv_object (loaded by cv2)
        :param mask_pic_path: '/path/to/your/target.png'
        :param mask_pic_object: your_pic_cv_object (loaded by cv2)
        :param scale: default to (1, 3, 10)
        :return:
        """

        # pre assert
        assert self.template, 'template is empty'
        assert (target_pic_path is not None) or (target_pic_object is not None), 'need path or cv object'

        # load target
        logger.info('start finding ...')
        target_pic_object = pre_pic(target_pic_path, target_pic_object)

        # mask
        if mask_pic_path or mask_pic_object is not None:
            logger.info('mask detected')
            mask_pic_object = pre_pic(mask_pic_path, mask_pic_object)

        # scale
        if not scale:
            # default scale
            scale = (1, 3, 10)
        logger.info('scale: {}'.format(str(scale)))

        result: typing.List[dict] = list()
        for each_template_path, each_template_object in self.template.items():
            logger.debug('start analysing: [{}] ...'.format(each_template_path))
            min_val, max_val, min_loc, max_loc = self._compare(
                target_pic_object,
                each_template_object,
                scale,
                mask_pic_object
            )
            logger.debug('raw compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
            min_loc, max_loc = map(lambda i: fix_location(each_template_object, i), [min_loc, max_loc])
            logger.debug('fixed compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))

            # add to result list
            current_result = {
                'path': each_template_path,
                'min_val': min_val,
                'max_val': max_val,
                'min_loc': min_loc,
                'max_loc': max_loc,
            }
            logger.debug('result for [{}]: {}'.format(each_template_path, json.dumps(current_result)))
            result.append(current_result)

        final_result = {
            'target_path': target_pic_path,
            'cv_method': self._cv_method_name,
            'data': result,
        }
        logger.info('result: {}'.format(json.dumps(final_result)))
        return final_result

    def _compare(self,
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
                self._cv_method_code,
                mask=resize_mask_pic_object)
            result_list.append(cv2.minMaxLoc(res))

        logger.debug('scale search result: {}'.format(result_list))
        # return the max one
        return sorted(result_list, key=lambda i: i[1])[-1]

    def reset(self):
        """ reset template, target and result """
        self.template = dict()
        logger.info('findit reset successfully')
