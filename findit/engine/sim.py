import numpy as np
import cv2
from skimage.measure import compare_ssim

from findit.logger import logger
from findit.engine.base import FindItEngine, FindItEngineResponse


class SimEngine(FindItEngine):
    """ Similarity engine """
    DEFAULT_INTERPOLATION = cv2.INTER_CUBIC

    def __init__(self,
                 engine_sim_interpolation: int = None,
                 *_, **__):
        logger.info(f'engine {self.get_type()} preparing ...')

        self.engine_sim_interpolation = engine_sim_interpolation or self.DEFAULT_INTERPOLATION

        logger.debug(f'interpolation: {self.DEFAULT_INTERPOLATION}')
        logger.info(f'engine {self.get_type()} loaded')

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> FindItEngineResponse:
        resp = FindItEngineResponse()

        resized_target = cv2.resize(target_object, template_object.shape[::-1], interpolation=cv2.INTER_CUBIC)
        ssim = compare_ssim(resized_target, template_object)

        resp.append('conf', self.__dict__)
        resp.append('ssim', ssim, important=True)
        resp.append('ok', True, important=True)
        return resp
