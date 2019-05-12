import numpy as np
import typing
import cv2

from findit.logger import logger
from findit import toolbox
from findit.toolbox import Point


class FindItEngine(object):
    def get_type(self):
        return self.__class__.__name__


class TemplateEngine(FindItEngine):
    """
    Default cv method is TM_CCORR_NORMED

    1. Opencv support only CV_TM_CCORR_NORMED & CV_TM_SQDIFF
        (https://stackoverflow.com/questions/35658323/python-opencv-matchtemplate-is-mask-feature-implemented)
    2. Personally I do not want to use SQDIFF series. Its max value is totally different from what we thought.
    """
    DEFAULT_CV_METHOD_NAME = 'cv2.TM_CCORR_NORMED'
    DEFAULT_SCALE = (1, 3, 10)

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
            scale = self.DEFAULT_SCALE
        self.scale = scale

        logger.debug('cv method: {}'.format(self.cv_method_name))
        logger.debug('scale: {}'.format(scale))
        logger.info('engine {} loaded'.format(self.get_type()))

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
            template_object,
            target_object,
            self.scale,
            mask_pic_object
        )
        logger.debug('raw compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
        min_loc, max_loc = map(lambda i: toolbox.fix_location(template_object, i), [min_loc, max_loc])
        logger.debug('fixed compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))

        # 'target_point' must existed
        return {
            'target_point': max_loc,
            'target_sim': max_val,
            'raw': {
                'min_val': min_val,
                'max_val': max_val,
                'min_loc': min_loc,
                'max_loc': max_loc,
            }
        }

    def _compare_template(self,
                          template_pic_object: np.ndarray,
                          target_pic_object: np.ndarray,
                          scale: typing.Sequence,
                          mask_pic_object: np.ndarray = None) -> typing.Sequence[float]:
        """
        compare via template matching
        (https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/)

        :param template_pic_object:
        :param target_pic_object:
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
    def __init__(self,
                 *_, **__):
        logger.info('engine {} loaded'.format(self.get_type()))

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> dict:
        point_list = self._get_feature_point_list(template_object, target_object)
        center_point = toolbox.calculate_center_point(point_list)

        readable_point_list = [each.to_tuple() for each in point_list]
        readable_center_point = center_point.to_tuple()
        return {
            'target_point': readable_center_point,
            'raw': readable_point_list,
        }

    @classmethod
    def _get_feature_point_list(cls,
                                template_pic_object: np.ndarray,
                                target_pic_object: np.ndarray) -> typing.Sequence[Point]:
        """
        compare via feature matching

        :param template_pic_object:
        :param target_pic_object:
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
            each_point = Point(*kp2[img2_idx].pt)
            point_list.append(each_point)

        return point_list


engine_dict = {
    'feature': FeatureEngine,
    'template': TemplateEngine,
}
