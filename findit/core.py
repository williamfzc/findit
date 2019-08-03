import os
import numpy as np
import typing
import json
# DO NOT remove this
import cv2

from findit.logger import logger, LOGGER_FLAG
from findit import toolbox
from findit.engine import engine_dict, FindItEngineResponse, FindItEngine


class _TemplateManager(object):
    def __init__(self):
        self._template_list: list = list()

    def reset(self):
        self._template_list = list()

    def save(self, pic_name: str, pic_item: typing.Union[str, np.ndarray]):
        self._template_list.append((pic_name, pic_item))

    def load(self) -> tuple:
        for pic_name, pic_item in self._template_list:
            # is path
            if isinstance(pic_item, str):
                yield pic_name, toolbox.load_grey_from_path(pic_item)
            # is object
            else:
                yield pic_name, toolbox.load_grey_from_cv2_object(pic_item)

    def is_empty(self):
        return len(self._template_list) == 0


class FindIt(object):
    """ FindIt Operator """

    def __init__(self,
                 need_log: bool = None,
                 engine: typing.Sequence = None,
                 pro_mode: bool = None,
                 *args, **kwargs):
        """
        Init everything. Args here will init the engines too. Read __init__ part in engine.py for details.

        :param need_log: enable or disable logger
        :param engine: choose image processing engine, eg: ['feature', 'template']
        :param pro_mode:

        kwargs here will be used to init engine, which starts with engine_{engine_name} :

            # feature
            engine_feature_cluster_num: int = None,
            engine_feature_distance_threshold: float = None,
            engine_feature_min_hessian: int = None,

            # ocr
            engine_ocr_lang: str = None,

            # sim
            engine_sim_interpolation: int = None,

            # template
            engine_template_cv_method_name: str = None,
            engine_template_scale: typing.Sequence = None,
            engine_template_multi_target_max_threshold: float = None,
            engine_template_multi_target_distance_threshold: float = None,
            engine_template_compress_rate: float = None,
        """
        # template manager
        self.template: _TemplateManager = _TemplateManager()

        # init logger
        self.switch_logger(bool(need_log))

        # init engine
        if not engine:
            # default
            engine = ['template', 'feature']
        self.engine_name_list: typing.List[str] = engine
        self.engine_list: typing.List[FindItEngine] = list()
        self.set_engine(engine, *args, **kwargs)

        # pro mode
        self.pro_mode = bool(pro_mode)
        logger.info(f'in pro mode: {self.pro_mode}')

    @staticmethod
    def switch_logger(status: bool):
        """ enable or disable logger """
        if status:
            logger.enable(LOGGER_FLAG)
            logger.info('logger up')
        else:
            logger.disable(LOGGER_FLAG)

    def set_engine(self, engine_name_list, *args, **kwargs):
        logger.info(f'set engine: {engine_name_list}')
        self.engine_list = [engine_dict[each](*args, **kwargs) for each in engine_name_list]

    def load_template(self,
                      pic_name: str,
                      pic_path: str = None,
                      pic_object: np.ndarray = None):
        """
        load template picture

        :param pic_name: use pic name as result's key, eg: 'your_picture_1'
        :param pic_path: eg: '../your_picture.png'
        :param pic_object: eg: your_pic_cv_object)
        :return:
        """
        assert (pic_path is not None) or (pic_object is not None), 'need path or cv object'

        if pic_object is not None:
            logger.info('load template from picture object directly ...')
            self.template.save(pic_name, pic_object)
        else:
            logger.info('load template from picture path ...')
            abs_path = os.path.abspath(pic_path)
            self.template.save(pic_name, abs_path)

        logger.info(f'load template [{pic_name}] successfully')

    def _need_template(self) -> bool:
        """
        check engine list, and return bool about dependencies of template picture (eg: ocr engine need no template)
        """
        return self.engine_name_list != ['ocr']

    def find(self,
             target_pic_name: str,
             target_pic_path: str = None,
             target_pic_object: np.ndarray = None,
             *args, **kwargs) -> dict:
        """
        start match

        :param target_pic_name: eg: 'your_target_picture_1'
        :param target_pic_path: '/path/to/your/target.png'
        :param target_pic_object: your_pic_cv_object (loaded by cv2)

        kwargs here will be used to engine.execute(), which starts with engine_{engine_name}:

            # ocr
            engine_ocr_offset: int = None,
            engine_ocr_deep: bool = None,

            # template
            engine_template_mask_pic_object: np.ndarray = None,
            engine_template_mask_pic_path: str = None,
        :return:
        """

        # pre assert
        assert (target_pic_path is not None) or (target_pic_object is not None), 'need path or cv object'

        # load target
        logger.info('start finding ...')
        target_pic_object = toolbox.pre_pic(target_pic_path, target_pic_object)

        if self._need_template():
            find_func = self._find_with_template
        else:
            find_func = self._find_without_template
        result = find_func(
            target_pic_object,
            target_pic_name=target_pic_name,
            target_pic_path=target_pic_path,
            *args, **kwargs
        )
        return {
            'target_name': target_pic_name,
            'target_path': target_pic_path,
            'data': result
        }

    def _find_without_template(self,
                               target_pic_object: np.ndarray,
                               target_pic_name: str = None,
                               *args, **kwargs) -> dict:
        logger.debug(f'start analysing: [{target_pic_name}] ...')

        current_result = dict()
        for each_engine in self.engine_list:
            each_result = each_engine.execute(None, target_pic_object, *args, **kwargs)

            # result filter
            each_result = self._prune_result(each_result)
            current_result[each_engine.get_type()] = each_result

        logger.debug(f'result for [{target_pic_name}]: {json.dumps(current_result, default=lambda x: x.__dict__)}')
        return {
            target_pic_name: current_result,
        }

    def _find_with_template(self,
                            target_pic_object: np.ndarray,
                            _mark_pic: bool = None,
                            *args, **kwargs) -> dict:
        # pre assert
        assert not self.template.is_empty(), 'template is empty'

        result = dict()
        for each_template_name, each_template_object in self.template.load():
            logger.debug(f'start analysing: [{each_template_name}] ...')

            # todo lazy load
            current_result = dict()
            for each_engine in self.engine_list:
                each_result = each_engine.execute(each_template_object, target_pic_object, *args, **kwargs)

                # for debug ONLY!
                if _mark_pic:
                    target_pic_object_with_mark = toolbox.mark_point(
                        target_pic_object,
                        each_result['target_point'],
                        cover=False)
                    temp_pic_path = toolbox.debug_cv_object(target_pic_object_with_mark)
                    logger.debug(
                        f'template: {each_template_name}, '
                        f'engine: {each_engine.get_type()}, '
                        f'path: {temp_pic_path}')

                # result filter
                each_result = self._prune_result(each_result)

                current_result[each_engine.get_type()] = each_result
            logger.debug(f'result for [{each_template_name}]: {json.dumps(current_result, default=lambda x: x.__dict__)}')
            result[each_template_name] = current_result

        return result

    def _prune_result(self, response: FindItEngineResponse) -> dict:
        if self.pro_mode:
            return response.get_content()
        return response.get_brief()

    def clear(self):
        """ reset template, target and result """
        self.template = dict()
        logger.info('findit clear successfully')
