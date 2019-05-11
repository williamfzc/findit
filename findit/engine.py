import numpy as np
import typing
import cv2

from findit.logger import logger
from findit import toolbox


class FindItEngine(object):
    def get_type(self):
        return self.__name__


class TemplateEngine(FindItEngine):
    DEFAULT_CV_METHOD_NAME = 'cv2.TM_CCORR_NORMED'

    def __init__(self,
                 cv_method_name: str = None,
                 scale: typing.Sequence = None,
                 *_, **__):
        # cv
        if not cv_method_name:
            cv_method_name = self.DEFAULT_CV_METHOD_NAME
        self.cv_method_name = cv_method_name
        self.cv_method_code = eval(cv_method_name)

        # scale
        if not scale:
            # default scale
            scale = (1, 3, 10)
        self.scale = scale
        logger.info('scale: {}'.format(str(scale)))

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                mask_pic_object: np.ndarray = None,
                mask_pic_path: str = None,
                *_, **__) -> dict:
        # mask
        if (mask_pic_path is not None) or (mask_pic_object is not None):
            logger.info('mask detected')
            mask_pic_object = toolbox.pre_pic(mask_pic_path, mask_pic_object)

        # template matching
        min_val, max_val, min_loc, max_loc = self._compare_template(
            target_object,
            template_object,
            self.scale,
            mask_pic_object
        )
        logger.debug('raw compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
        min_loc, max_loc = map(lambda i: toolbox.fix_location(template_object, i), [min_loc, max_loc])
        logger.debug('fixed compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))

        return {
            'min_val': min_val,
            'max_val': max_val,
            'min_loc': min_loc,
            'max_loc': max_loc,
        }

    def _compare_template(self,
                          target_pic_object: np.ndarray,
                          template_pic_object: np.ndarray,
                          scale: typing.Sequence,
                          mask_pic_object: np.ndarray = None) -> typing.Sequence[float]:
        """
        compare via template matching
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
            resize_template_pic_object = toolbox.resize_pic_scale(template_pic_object, each_scale)

            # resize mask
            if mask_pic_object is not None:
                resize_mask_pic_object = toolbox.resize_pic_scale(mask_pic_object, each_scale)
            else:
                resize_mask_pic_object = None

            # if template's size is larger than raw picture, break
            if resize_template_pic_object.shape[0] > pic_height or resize_template_pic_object.shape[1] > pic_width:
                break

            res = cv2.matchTemplate(
                target_pic_object,
                resize_template_pic_object,
                self.cv_method_code,
                mask=resize_mask_pic_object)
            result_list.append(cv2.minMaxLoc(res))

        logger.debug('scale search result: {}'.format(result_list))
        # return the max one
        return sorted(result_list, key=lambda i: i[1])[-1]


class FeatureEngine(FindItEngine):
    def __init__(self, *args, **kwargs):
        # TODO
        pass

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> dict:
        center_point = self._compare_feature(template_object, target_object)
        return {
            'center': center_point,
        }

    def _compare_feature(self,
                         template_pic_object: np.ndarray,
                         target_pic_object: np.ndarray) -> typing.Sequence[float]:
        """
        compare via feature matching

        :param target_pic_object:
        :param template_pic_object:
        :return:
        """
        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        _, des1 = sift.detectAndCompute(template_pic_object, None)
        kp2, des2 = sift.detectAndCompute(target_pic_object, None)

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply ratio test
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append([m])
        point_list = list()
        for each in good:
            img2_idx = each[0].trainIdx
            point_list.append(kp2[img2_idx].pt)

        # cal the central point
        center_x = sum([_[0] for _ in point_list]) / len(point_list)
        center_y = sum([_[1] for _ in point_list]) / len(point_list)
        return center_x, center_y
