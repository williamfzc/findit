import numpy as np
import typing
import cv2
import collections
# https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
from sklearn.cluster import KMeans

from findit.logger import logger
from findit.toolbox import Point
from findit.engine.base import FindItEngine, FindItEngineResponse


class FeatureEngine(FindItEngine):
    # TODO need many sample pictures to test
    DEFAULT_CLUSTER_NUM: int = 3
    # higher -> more
    DEFAULT_DISTANCE_THRESHOLD: float = 0.9
    # higher -> less
    DEFAULT_MIN_HESSIAN: int = 200

    def __init__(self,
                 engine_feature_cluster_num: int = None,
                 engine_feature_distance_threshold: float = None,
                 engine_feature_min_hessian: int = None,
                 *_, **__):
        logger.info(f'engine {self.get_type()} preparing ...')

        # for kmeans calculation
        self.engine_feature_cluster_num: int = engine_feature_cluster_num or self.DEFAULT_CLUSTER_NUM
        # for feature matching
        self.engine_feature_distance_threshold: float = engine_feature_distance_threshold or self.DEFAULT_DISTANCE_THRESHOLD
        # for determining if a point is a feature point
        # higher threshold, less points
        self.engine_feature_min_hessian: int = engine_feature_min_hessian or self.DEFAULT_MIN_HESSIAN

        logger.debug(f'cluster num: {self.engine_feature_cluster_num}')
        logger.debug(f'distance threshold: {self.engine_feature_distance_threshold}')
        logger.debug(f'hessian threshold: {self.engine_feature_min_hessian}')
        logger.info(f'engine {self.get_type()} loaded')

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> FindItEngineResponse:
        resp = FindItEngineResponse()
        resp.append('conf', self.__dict__)

        point_list = self.get_feature_point_list(template_object, target_object)

        # no point found
        if not point_list:
            resp.append('target_point', (-1, -1), important=True)
            resp.append('raw', 'not found')
            resp.append('ok', False, important=True)
            return resp

        center_point = self.calculate_center_point(point_list)

        readable_center_point = list(center_point)
        readable_point_list = [list(each) for each in point_list]

        resp.append('target_point', readable_center_point, important=True)
        resp.append('feature_point_num', len(readable_point_list), important=True)
        resp.append('raw', readable_point_list)
        resp.append('ok', True, important=True)
        return resp

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
        surf = cv2.xfeatures2d.SURF_create(self.engine_feature_min_hessian)

        # find the keypoints and descriptors with SURF
        template_kp, template_desc = surf.detectAndCompute(template_pic_object, None)
        target_kp, target_desc = surf.detectAndCompute(target_pic_object, None)

        # key points count
        logger.debug(f'template key point count: {len(template_kp)}')
        logger.debug(f'target key point count: {len(target_kp)}')

        # find 2 points, which are the closest
        # 找到帧和帧之间的一致性的过程就是在一个描述符集合（询问集）中找另一个集合（相当于训练集）的最近邻。 这里找到 每个描述符 的 最近邻与次近邻
        # 一个正确的匹配会更接近第一个邻居。换句话说，一个不正确的匹配，两个邻居的距离是相似的。因此，我们可以通过查看二者距离的不同来评判距匹配程度的好坏。
        # more details: https://blog.csdn.net/liangjiubujiu/article/details/80418079
        flann = cv2.FlannBasedMatcher()
        matches = flann.knnMatch(template_desc, target_desc, k=2)
        # matches are something like:
        # [[<DMatch 0x12400a350>, <DMatch 0x12400a430>], [<DMatch 0x124d6a170>, <DMatch 0x124d6a450>]]

        logger.debug(f'matches num: {len(matches)}')

        # TODO here is a sample to show feature points
        # temp = cv2.drawMatchesKnn(template_pic_object, kp1, target_pic_object, kp2, matches, None, flags=2)
        # cv2.imshow('feature_points', temp)
        # cv2.waitKey(0)

        # filter for invalid points
        good = []
        # only one matches
        if len(matches) == 1:
            good = matches[0]
        # more than one matches
        else:
            for m, n in matches:
                if m.distance < self.engine_feature_distance_threshold * n.distance:
                    good.append(m)

        # get positions
        point_list = list()
        for each in good:
            target_idx = each.trainIdx
            each_point = Point(*target_kp[target_idx].pt)
            point_list.append(each_point)

        return point_list

    def calculate_center_point(self, point_list: typing.Sequence[Point]) -> Point:
        np_point_list = np.array(point_list)
        point_num = len(np_point_list)

        # if match points' count is less than clusters
        if point_num < self.engine_feature_cluster_num:
            cluster_num = 1
        else:
            cluster_num = self.engine_feature_cluster_num

        k_means = KMeans(n_clusters=cluster_num).fit(np_point_list)
        mode_label_index = sorted(collections.Counter(k_means.labels_).items(), key=lambda x: x[1])[-1][0]
        return Point(*k_means.cluster_centers_[mode_label_index])
