import cv2
import os
import numpy as np
import typing
import json

from findit.logger import logger, LOGGER_FLAG
from findit import toolbox
from findit.engine import engine_dict


class FindIt(object):
    """ FindIt Operator """

    def __init__(self,
                 need_log: bool = None,
                 engine: typing.Sequence = None,
                 pro_mode: bool = None,
                 *args, **kwargs):
        """

        :param need_log: enable or disable logger
        :param engine: choose image processing engine, eg: ['feature', 'template']
        :param pro_mode:
        """
        # template pic dict,
        # { pic_name: pic_cv_object }
        self.template: typing.Dict[str, np.ndarray] = dict()

        # init logger
        self.switch_logger(bool(need_log))

        # init engine
        if not engine:
            # default
            engine = ['template', 'feature']
        self.engine_list = None
        self.set_engine(engine, *args, **kwargs)

        # pro mode
        self.pro_mode = bool(pro_mode)
        logger.info('in pro mode: {}'.format(self.pro_mode))

    @staticmethod
    def switch_logger(status: bool):
        """ enable or disable logger """
        if status:
            logger.enable(LOGGER_FLAG)
            logger.info('logger up')
        else:
            logger.disable(LOGGER_FLAG)

    def set_engine(self, engine_name_list, *args, **kwargs):
        logger.info('set engine: {}'.format(engine_name_list))
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
            self.template[pic_name] = toolbox.load_grey_from_cv2_object(pic_object)
        else:
            logger.info('load template from picture path ...')
            abs_path = os.path.abspath(pic_path)
            self.template[pic_name] = toolbox.load_grey_from_path(abs_path)
        logger.info('load template [{}] successfully'.format(pic_name))

    def find(self,
             target_pic_name: str,
             target_pic_path: str = None,
             target_pic_object: np.ndarray = None,
             *args, **kwargs):
        """
        start match

        :param target_pic_name: eg: 'your_target_picture_1'
        :param target_pic_path: '/path/to/your/target.png'
        :param target_pic_object: your_pic_cv_object (loaded by cv2)
        :return:
        """

        # pre assert
        assert self.template, 'template is empty'
        assert (target_pic_path is not None) or (target_pic_object is not None), 'need path or cv object'

        # load target
        logger.info('start finding ...')
        target_pic_object = toolbox.pre_pic(target_pic_path, target_pic_object)

        result = dict()
        for each_template_name, each_template_object in self.template.items():
            logger.debug('start analysing: [{}] ...'.format(each_template_name))

            current_result = dict()
            for each_engine in self.engine_list:
                each_result = each_engine.execute(each_template_object, target_pic_object, *args, **kwargs)

                # if not in pro mode,
                if not self.pro_mode:
                    each_result = each_result['target_point']
                current_result[each_engine.get_type()] = each_result

            logger.debug('result for [{}]: {}'.format(each_template_name, json.dumps(current_result)))
            result[each_template_name] = current_result

        final_result = {
            'target_name': target_pic_name,
            'target_path': target_pic_path,
            'data': result,
        }
        logger.info('result: {}'.format(json.dumps(final_result)))
        return final_result

    def clear(self):
        """ reset template, target and result """
        self.template = dict()
        logger.info('findit clear successfully')
