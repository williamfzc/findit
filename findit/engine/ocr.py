import numpy as np
import warnings

from findit.logger import logger
from findit.engine.base import FindItEngine, FindItEngineResponse

try:
    import findtext
except ImportError:
    warnings.warn('findtext should be installed if you want to use OCR engine')


class OCREngine(FindItEngine):
    """ OCR engine, binding to tesseract """
    DEFAULT_LANGUAGE = 'eng'

    def __init__(self,
                 engine_ocr_lang: str = None,
                 *_, **__):
        logger.info(f'engine {self.get_type()} preparing ...')

        # check language data before execute function, not here.
        self.engine_ocr_lang = engine_ocr_lang or self.DEFAULT_LANGUAGE
        assert findtext, 'findtext should be installed if you want to use OCR engine'
        self._ft = findtext.FindText(lang=engine_ocr_lang)

        self.engine_ocr_tess_data_dir = self._ft.get_data_home()
        self.engine_ocr_available_lang_list = self._ft.get_available_lang()

        logger.debug(f'target lang: {self.engine_ocr_lang}')
        logger.debug(f'tess data dir: {self.engine_ocr_tess_data_dir}')
        logger.debug(f'available language: {self.engine_ocr_available_lang_list}')
        logger.info(f'engine {self.get_type()} loaded')

    def execute(self,
                template_object: np.ndarray,
                target_object: np.ndarray,
                *_, **__) -> FindItEngineResponse:
        resp = FindItEngineResponse()

        # _ft is not JSON serializable
        conf_dict = {k: _ for k, _ in self.__dict__.items() if k != '_ft'}
        resp.append('conf', conf_dict, important=True)

        # check language
        if self.engine_ocr_lang not in self.engine_ocr_available_lang_list:
            resp.append('raw', 'this language not available', important=True)
            resp.append('ok', False, important=True)
            return resp

        word_block_list = self._ft.find_word(image_object=target_object, deep=True, offset=5)
        result_text = ''.join([i.content for i in word_block_list])

        resp.append('raw', result_text, important=True)
        resp.append('ok', True, important=True)
        return resp
