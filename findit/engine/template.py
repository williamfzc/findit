import numpy as np
import typing
import cv2

from findit.logger import logger
from findit import toolbox
from findit.engine.base import FindItEngine, FindItEngineResponse


class TemplateEngine(FindItEngine):
    """
    Default cv method is TM_CCORR_NORMED

    1. Opencv support only CV_TM_CCORR_NORMED & CV_TM_SQDIFF
        (https://stackoverflow.com/questions/35658323/python-opencv-matchtemplate-is-mask-feature-implemented)
    2. Personally I do not want to use SQDIFF series. Its max value is totally different from what we thought.
    """

    DEFAULT_CV_METHOD_NAME: str = "cv2.TM_CCORR_NORMED"
    DEFAULT_SCALE: typing.Sequence = (1, 3, 10)
    DEFAULT_MULTI_TARGET_MAX_THRESHOLD: float = 0.99
    DEFAULT_MULTI_TARGET_DISTANCE_THRESHOLD: float = 10.0
    DEFAULT_COMPRESS_RATE: float = 1.0

    def __init__(
        self,
        engine_template_cv_method_name: str = None,
        engine_template_scale: typing.Sequence = None,
        engine_template_multi_target_max_threshold: float = None,
        engine_template_multi_target_distance_threshold: float = None,
        engine_template_compress_rate: float = None,
        *_,
        **__,
    ):
        """ eg: engine_template_cv_method_name -> cv_method_name """
        logger.info(f"engine {self.get_type()} preparing ...")

        # cv
        self.engine_template_cv_method_name = (
            engine_template_cv_method_name or self.DEFAULT_CV_METHOD_NAME
        )
        self.engine_template_cv_method_code = eval(self.engine_template_cv_method_name)

        # scale
        self.engine_template_scale = engine_template_scale or self.DEFAULT_SCALE

        # multi target max threshold ( max_val * max_threshold == real threshold )
        self.engine_template_multi_target_max_threshold = (
            engine_template_multi_target_max_threshold
            or self.DEFAULT_MULTI_TARGET_MAX_THRESHOLD
        )
        self.engine_template_multi_target_distance_threshold = (
            engine_template_multi_target_distance_threshold
            or self.DEFAULT_MULTI_TARGET_DISTANCE_THRESHOLD
        )

        # compression
        self.engine_template_compress_rate = (
            engine_template_compress_rate or self.DEFAULT_COMPRESS_RATE
        )

        logger.debug(f"cv method: {self.engine_template_cv_method_name}")
        logger.debug(f"scale: {self.engine_template_scale}")
        logger.debug(
            f"multi target max threshold: {self.engine_template_multi_target_max_threshold}"
        )
        logger.debug(
            f"multi target distance threshold: {self.engine_template_multi_target_distance_threshold}"
        )
        logger.debug(f"compress rate: {self.engine_template_compress_rate}")
        logger.info(f"engine {self.get_type()} loaded")

    def execute(
        self,
        template_object: np.ndarray,
        target_object: np.ndarray,
        engine_template_mask_pic_object: np.ndarray = None,
        engine_template_mask_pic_path: str = None,
        *_,
        **__,
    ) -> FindItEngineResponse:
        resp = FindItEngineResponse()
        resp.append("conf", self.__dict__)

        # mask
        if (engine_template_mask_pic_path is not None) or (
            engine_template_mask_pic_object is not None
        ):
            logger.info("mask detected")
            engine_template_mask_pic_object = toolbox.pre_pic(
                engine_template_mask_pic_path, engine_template_mask_pic_object
            )

        # template matching
        min_val, max_val, min_loc, max_loc, point_list = self._compare_template(
            template_object,
            target_object,
            self.engine_template_scale,
            engine_template_mask_pic_object,
        )

        # 'target_point' must existed
        resp.append("target_point", max_loc, important=True)
        resp.append("target_sim", max_val, important=True)
        resp.append(
            "raw",
            {
                "min_val": min_val,
                "max_val": max_val,
                "min_loc": min_loc,
                "max_loc": max_loc,
                "all": point_list,
            },
        )
        resp.append("ok", True, important=True)

        return resp

    def _compare_template(
        self,
        template_pic_object: np.ndarray,
        target_pic_object: np.ndarray,
        scale: typing.Sequence,
        mask_pic_object: np.ndarray = None,
    ) -> typing.Sequence:
        """
        compare via template matching
        (https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/)

        :param template_pic_object:
        :param target_pic_object:
        :param scale: default to (1, 3, 10)
        :param mask_pic_object:
        :return: min_val, max_val, min_loc, max_loc
        """
        result_list = list()

        # compress
        pic_width, pic_height = target_pic_object.shape[:2]
        logger.debug(
            f"target object size before compressing: w={pic_width}, h={pic_height}"
        )
        target_pic_object = toolbox.compress_frame(
            target_pic_object, self.engine_template_compress_rate
        )
        pic_width, pic_height = target_pic_object.shape[:2]
        logger.debug(
            f"target object size after compressing: w={pic_width}, h={pic_height}"
        )

        for each_scale in np.linspace(*scale):
            # resize template
            resize_template_pic_object = toolbox.resize_pic_scale(
                template_pic_object, each_scale
            )

            # resize mask
            if mask_pic_object is not None:
                mask_pic_object = toolbox.resize_pic_scale(mask_pic_object, each_scale)

            # if template's size is larger than raw picture, break
            if (
                resize_template_pic_object.shape[0] > pic_width
                or resize_template_pic_object.shape[1] > pic_height
            ):
                break

            res = cv2.matchTemplate(
                target_pic_object,
                resize_template_pic_object,
                self.engine_template_cv_method_code,
                mask=mask_pic_object,
            )
            # each of current result is:
            # [(min_val, max_val, min_loc, max_loc), point_list, shape]

            current_result = [*self._parse_res(res), resize_template_pic_object.shape]
            result_list.append(current_result)

        # too much log here, remove it.
        # logger.debug('scale search result: {}'.format(result_list))

        # get the best one
        try:
            loc_val, point_list, shape = sorted(result_list, key=lambda i: i[0][1])[-1]
        except IndexError:
            raise IndexError(
                """
                template picture is larger than your target.
                
                1. pick another template picture.
                2. set engine_template_scale in __init__, see demo.py for details.
                """
            )
        min_val, max_val, min_loc, max_loc = loc_val

        # fix position
        logger.debug(f"raw compare result: {max_loc}, {max_val}")
        min_loc, max_loc = map(
            lambda each_location: list(toolbox.fix_location(shape, each_location)),
            [min_loc, max_loc],
        )

        # de compress
        logger.debug(f"decompress compare result: {max_loc}, {max_val}")
        min_loc, max_loc = map(
            lambda p: toolbox.decompress_point(p, self.engine_template_compress_rate),
            [min_loc, max_loc],
        )

        point_list = [
            list(toolbox.fix_location(shape, each))
            for each in toolbox.point_list_filter(
                point_list, self.engine_template_multi_target_distance_threshold
            )
        ]
        # sort point list
        point_list.sort(key=lambda i: i[0])

        logger.debug(f"fixed compare result: {max_loc}, {max_val}")
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
