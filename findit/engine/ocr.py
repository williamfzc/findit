import numpy as np
import warnings
import typing

from findit.logger import logger
from findit.engine.base import FindItEngine, FindItEngineResponse

try:
    import findtext
except ImportError:
    logger.debug("findtext should be installed if you want to use OCR engine")


class OCREngine(FindItEngine):
    """ OCR engine, binding to tesseract """

    # language settings, same as tesseract
    # if you want to use chi_sim and eng, you can set it 'chi_sim+eng'
    DEFAULT_LANGUAGE: str = "eng"
    # offset for words ( sometimes causes out of range, take care )
    DEFAULT_OFFSET: int = 0
    # deep query
    DEFAULT_DEEP: bool = False

    def __init__(self, engine_ocr_lang: str = None, *_, **__):
        logger.info(f"engine {self.get_type()} preparing ...")

        # check language data before execute function, not here.
        self.engine_ocr_lang = engine_ocr_lang or self.DEFAULT_LANGUAGE
        self.engine_ocr_offset = self.DEFAULT_OFFSET
        self.engine_ocr_deep = self.DEFAULT_DEEP

        assert findtext, "findtext should be installed if you want to use OCR engine"
        self._ft = findtext.FindText(lang=engine_ocr_lang)

        self.engine_ocr_tess_data_dir = self._ft.get_data_home()
        self.engine_ocr_available_lang_list = self._ft.get_available_lang()

        logger.debug(f"target lang: {self.engine_ocr_lang}")
        logger.debug(f"tess data dir: {self.engine_ocr_tess_data_dir}")
        logger.debug(f"available language: {self.engine_ocr_available_lang_list}")
        logger.info(f"engine {self.get_type()} loaded")

    def execute(
        self,
        template_object: np.ndarray,
        target_object: np.ndarray,
        engine_ocr_offset: int = None,
        engine_ocr_deep: bool = None,
        *_,
        **__,
    ) -> FindItEngineResponse:
        resp = FindItEngineResponse()

        if engine_ocr_offset:
            self.engine_ocr_offset = engine_ocr_offset
        if engine_ocr_deep:
            self.engine_ocr_deep = engine_ocr_deep

        # _ft is not JSON serializable
        conf_dict = {k: _ for k, _ in self.__dict__.items() if k != "_ft"}
        resp.append("conf", conf_dict, important=True)

        # check language
        for each_lang in self.engine_ocr_lang.split("+"):
            if each_lang not in self.engine_ocr_available_lang_list:
                resp.append("raw", "this language not available", important=True)
                resp.append("ok", False, important=True)
                return resp

        word_block_list = self._ft.find_word(
            image_object=target_object,
            deep=self.engine_ocr_deep,
            offset=self.engine_ocr_offset,
        )

        available_result_list = [i for i in word_block_list if i.content]
        result_text = self._improve_text_result(
            [i.content for i in available_result_list]
        )

        resp.append("content", result_text, important=True)
        resp.append("raw", [i.__dict__ for i in word_block_list])
        resp.append("ok", True, important=True)
        return resp

    @staticmethod
    def _improve_text_result(origin: typing.List[str]) -> typing.List[str]:
        try:
            import jieba
        except ImportError:
            warnings.warn(
                "no package named jieba, you can install it for better ocr result"
            )
            return origin

        new = list()
        for each in origin:
            text_cut = jieba.cut(each)
            new.extend(text_cut)
        return list(set(new))
