import numpy as np
import typing
import cv2
import collections
# https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
from sklearn.cluster import KMeans

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
                 engine_template_cv_method_name: str = None,
                 engine_template_scale: typing.Sequence = None,
                 *_, **__):
        logger.info('engine {} preparing ...'.format(self.get_type()))

        # cv
        if not engine_template_cv_method_name:
            engine_template_cv_method_name = self.DEFAULT_CV_METHOD_NAME
        self.cv_method_name = engine_template_cv_method_name
        self.cv_method_code = eval(engine_template_cv_method_name)

        # scale
        if not engine_template_scale:
            # default scale
            engine_template_scale = self.DEFAULT_SCALE
        self.scale = engine_template_scale

        logger.debug('cv method: {}'.format(self.cv_method_name))
        logger.debug('scale: {}'.format(engine_template_scale))
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
            current_result = [cv2.minMaxLoc(res), resize_template_pic_object.shape]
            result_list.append(current_result)

        logger.debug('scale search result: {}'.format(result_list))
        # get the best one
        loc_val, shape = sorted(result_list, key=lambda i: i[0][1])[-1]
        min_val, max_val, min_loc, max_loc = loc_val
        logger.debug('raw compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
        min_loc, max_loc = map(lambda each_location: toolbox.fix_location(shape, each_location), [min_loc, max_loc])
        logger.debug('fixed compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
        return min_val, max_val, min_loc, max_loc


class FeatureEngine(FindItEngine):
    DEFAULT_CLUSTER_NUM = 3
    DEFAULT_DISTANCE_THRESHOLD = 0.75

    def __init__(self,
                 engine_feature_cluster_num: int = None,
                 engine_feature_distance_threshold: float = None,
                 *_, **__):
        logger.info('engine {} preparing ...'.format(self.get_type()))

        # for kmeans calculation
        self.cluster_num = engine_feature_cluster_num or self.DEFAULT_CLUSTER_NUM
        # for feature matching
        self.distance_threshold = engine_feature_distance_threshold or self.DEFAULT_DISTANCE_THRESHOLD

        logger.debug('cluster num: {}'.format(self.cluster_num))
        logger.debug('distance threshold: {}'.format(self.distance_threshold))
        logger.info('engine {} loaded'.format(self.get_type()))

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> dict:
        point_list = self.get_feature_point_list(template_object, target_object)
        
        # no point found
        if not point_list:
            return {
                'target_point': (-1, -1),
                'raw': [],
            }

        center_point = self.calculate_center_point(point_list)

        readable_point_list = [each.to_tuple() for each in point_list]
        readable_center_point = center_point.to_tuple()
        return {
            'target_point': readable_center_point,
            'raw': readable_point_list,
        }

    def get_feature_point_list(self,
                               template_pic_object: np.ndarray,
                               target_pic_object: np.ndarray) -> typing.Sequence[Point]:
        """
        compare via feature matching

        :param template_pic_object:
        :param target_pic_object:
        :return:
        """
        # Initiate SURF detector
        surf = cv2.xfeatures2d.SURF_create()

        # find the keypoints and descriptors with SURF
        kp1, des1 = surf.detectAndCompute(template_pic_object, None)
        kp2, des2 = surf.detectAndCompute(target_pic_object, None)

        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # TODO here is a sample to show feature points
        # temp = cv2.drawMatchesKnn(template_pic_object, kp1, target_pic_object, kp2, matches, None, flags=2)
        # cv2.imshow('feature_points', temp)
        # cv2.waitKey(0)

        # Apply ratio test
        good = []
        for m, n in matches:
            if m.distance < self.distance_threshold * n.distance:
                good.append([m])
        point_list = list()
        for each in good:
            img2_idx = each[0].trainIdx
            each_point = Point(*kp2[img2_idx].pt)
            point_list.append(each_point)

        return point_list

    def calculate_center_point(self, point_list: typing.Sequence[Point]) -> Point:
        np_point_list = np.array([_.to_tuple() for _ in point_list])
        point_num = len(np_point_list)

        # if match points' count is less than clusters
        if point_num < self.cluster_num:
            cluster_num = 1
        else:
            cluster_num = self.cluster_num

        k_means = KMeans(n_clusters=cluster_num).fit(np_point_list)
        mode_label_index = sorted(collections.Counter(k_means.labels_).items(), key=lambda x: x[1])[-1][0]
        return Point(*k_means.cluster_centers_[mode_label_index])


engine_dict = {
    'feature': FeatureEngine,
    'template': TemplateEngine,
}
