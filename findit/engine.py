import numpy as np
import typing
import cv2
import collections
import warnings
# https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
from sklearn.cluster import KMeans

from findit.logger import logger
from findit import toolbox
from findit.toolbox import Point

try:
    import tesserocr

    # tesserocr only supports PIL
    from PIL import Image
except ImportError:
    warnings.warn('tesserocr should be installed if you want to use OCR engine')


class FindItEngineResponse(object):
    """ standard response for engine """

    def __init__(self):
        self._content = dict()
        self._brief = dict()

    def append(self, key, value, important: bool = None):
        if important:
            self._brief[key] = value
        self._content[key] = value

    def get_brief(self) -> dict:
        return self._brief

    def get_content(self) -> dict:
        return self._content


class FindItEngine(object):
    def get_type(self):
        return self.__class__.__name__

    def execute(self, *_, **__) -> FindItEngineResponse:
        """ MUST BE IMPLEMENTED """
        raise NotImplementedError("this function must be implemented")


class TemplateEngine(FindItEngine):
    """
    Default cv method is TM_CCORR_NORMED

    1. Opencv support only CV_TM_CCORR_NORMED & CV_TM_SQDIFF
        (https://stackoverflow.com/questions/35658323/python-opencv-matchtemplate-is-mask-feature-implemented)
    2. Personally I do not want to use SQDIFF series. Its max value is totally different from what we thought.
    """
    DEFAULT_CV_METHOD_NAME: str = 'cv2.TM_CCORR_NORMED'
    DEFAULT_SCALE: typing.Sequence = (1, 3, 10)
    DEFAULT_MULTI_TARGET_MAX_THRESHOLD: float = 0.99
    DEFAULT_MULTI_TARGET_DISTANCE_THRESHOLD: float = 10.0

    def __init__(self,
                 engine_template_cv_method_name: str = None,
                 engine_template_scale: typing.Sequence = None,
                 engine_template_multi_target_max_threshold: float = None,
                 engine_template_multi_target_distance_threshold: float = None,
                 *_, **__):
        """ eg: engine_template_cv_method_name -> cv_method_name """
        logger.info('engine {} preparing ...'.format(self.get_type()))

        # cv
        self.engine_template_cv_method_name = engine_template_cv_method_name or self.DEFAULT_CV_METHOD_NAME
        self.engine_template_cv_method_code = eval(self.engine_template_cv_method_name)

        # scale
        self.engine_template_scale = engine_template_scale or self.DEFAULT_SCALE

        # multi target max threshold ( max_val * max_threshold == real threshold )
        self.engine_template_multi_target_max_threshold = engine_template_multi_target_max_threshold or self.DEFAULT_MULTI_TARGET_MAX_THRESHOLD
        self.engine_template_multi_target_distance_threshold = engine_template_multi_target_distance_threshold or self.DEFAULT_MULTI_TARGET_DISTANCE_THRESHOLD

        logger.debug(f'cv method: {self.engine_template_cv_method_name}')
        logger.debug(f'scale: {self.engine_template_scale}')
        logger.debug(f'multi target max threshold: {self.engine_template_multi_target_max_threshold}')
        logger.debug(f'multi target distance threshold: {self.engine_template_multi_target_distance_threshold}')
        logger.info(f'engine {self.get_type()} loaded')

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                engine_template_mask_pic_object: np.ndarray = None,
                engine_template_mask_pic_path: str = None,
                *_, **__) -> FindItEngineResponse:
        resp = FindItEngineResponse()
        resp.append('conf', self.__dict__)

        # mask
        if (engine_template_mask_pic_path is not None) or (engine_template_mask_pic_object is not None):
            logger.info('mask detected')
            engine_template_mask_pic_object = toolbox.pre_pic(engine_template_mask_pic_path,
                                                              engine_template_mask_pic_object)

        # template matching
        min_val, max_val, min_loc, max_loc, point_list = self._compare_template(
            template_object,
            target_object,
            self.engine_template_scale,
            engine_template_mask_pic_object
        )

        # 'target_point' must existed
        resp.append('target_point', max_loc, important=True)
        resp.append('target_sim', max_val, important=True)
        resp.append('raw', {
            'min_val': min_val,
            'max_val': max_val,
            'min_loc': min_loc,
            'max_loc': max_loc,
            'all': point_list,
        })

        return resp

    def _compare_template(self,
                          template_pic_object: np.ndarray,
                          target_pic_object: np.ndarray,
                          scale: typing.Sequence,
                          mask_pic_object: np.ndarray = None) -> typing.Sequence:
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
                mask_pic_object = toolbox.resize_pic_scale(mask_pic_object, each_scale)

            # if template's size is larger than raw picture, break
            if resize_template_pic_object.shape[0] > pic_height or resize_template_pic_object.shape[1] > pic_width:
                break

            res = cv2.matchTemplate(
                target_pic_object,
                resize_template_pic_object,
                self.engine_template_cv_method_code,
                mask=mask_pic_object)
            # each of current result is:
            # [(min_val, max_val, min_loc, max_loc), point_list, shape]

            current_result = [*self._parse_res(res), resize_template_pic_object.shape]
            result_list.append(current_result)

        # too much log here, remove it.
        # logger.debug('scale search result: {}'.format(result_list))

        # get the best one
        loc_val, point_list, shape = sorted(result_list, key=lambda i: i[0][1])[-1]
        min_val, max_val, min_loc, max_loc = loc_val

        # fix position
        logger.debug('raw compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
        min_loc, max_loc = map(lambda each_location: list(toolbox.fix_location(shape, each_location)),
                               [min_loc, max_loc])
        point_list = [list(toolbox.fix_location(shape, each))
                      for each in
                      toolbox.point_list_filter(point_list, self.engine_template_multi_target_distance_threshold)]
        # sort point list
        point_list.sort(key=lambda i: i[0])

        logger.debug('fixed compare result: {}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))

        return min_val, max_val, min_loc, max_loc, point_list

    def _parse_res(self, res: np.ndarray) -> typing.Sequence:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # multi target
        min_thresh = (max_val - 1e-6) * self.engine_template_multi_target_max_threshold
        match_locations = np.where(res >= min_thresh)
        point_list = zip(match_locations[1], match_locations[0])

        # convert int32 to float
        point_list = [tuple(map(float, _)) for _ in point_list]

        return (min_val, max_val, min_loc, max_loc), point_list


class FeatureEngine(FindItEngine):
    # TODO need many sample pictures to test
    DEFAULT_CLUSTER_NUM: int = 3
    DEFAULT_DISTANCE_THRESHOLD: float = 0.75
    DEFAULT_MIN_HESSIAN: int = 200

    def __init__(self,
                 engine_feature_cluster_num: int = None,
                 engine_feature_distance_threshold: float = None,
                 engine_feature_min_hessian: int = None,
                 *_, **__):
        logger.info('engine {} preparing ...'.format(self.get_type()))

        # for kmeans calculation
        self.engine_feature_cluster_num: int = engine_feature_cluster_num or self.DEFAULT_CLUSTER_NUM
        # for feature matching
        self.engine_feature_distance_threshold: float = engine_feature_distance_threshold or self.DEFAULT_DISTANCE_THRESHOLD
        # for determining if a point is a feature point
        # higher threshold, less points
        self.engine_feature_min_hessian: int = engine_feature_min_hessian or self.DEFAULT_MIN_HESSIAN

        logger.debug('cluster num: {}'.format(self.engine_feature_cluster_num))
        logger.debug('distance threshold: {}'.format(self.engine_feature_distance_threshold))
        logger.debug('hessian threshold: {}'.format(self.engine_feature_min_hessian))
        logger.info('engine {} loaded'.format(self.get_type()))

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
            return resp

        center_point = self.calculate_center_point(point_list)

        readable_center_point = list(center_point)
        readable_point_list = [list(each) for each in point_list]

        resp.append('target_point', readable_center_point, important=True)
        resp.append('raw', readable_point_list)
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


class OCREngine(FindItEngine):
    """ OCR engine, binding to tesseract """
    DEFAULT_LANGUAGE = 'eng'

    def __init__(self,
                 engine_ocr_lang: str = None,
                 *_, **__):
        logger.info('engine {} preparing ...'.format(self.get_type()))

        # check language data before execute function, not here.
        self.engine_ocr_lang = engine_ocr_lang or self.DEFAULT_LANGUAGE
        self.engine_ocr_tess_data_dir, self.engine_ocr_available_lang_list = tesserocr.get_languages()

        logger.debug(f'target lang: {self.engine_ocr_lang}')
        logger.debug(f'tess data dir: {self.engine_ocr_tess_data_dir}')
        logger.debug(f'available language: {self.engine_ocr_available_lang_list}')
        logger.info(f'engine {self.get_type()} loaded')

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> FindItEngineResponse:
        resp = FindItEngineResponse()
        resp.append('conf', self.__dict__, important=True)

        # check language
        if self.engine_ocr_lang not in self.engine_ocr_available_lang_list:
            resp.append('raw', 'this language not available', important=True)
            return resp

        api = tesserocr.PyTessBaseAPI(lang=self.engine_ocr_lang)
        target_pil_object = Image.fromarray(target_object)
        api.SetImage(target_pil_object)
        result_text = api.GetUTF8Text()

        resp.append('raw', result_text, important=True)
        return resp


engine_dict = {
    'feature': FeatureEngine,
    'template': TemplateEngine,
    'ocr': OCREngine,
}
