from findit.engine.feature import FeatureEngine
from findit.engine.template import TemplateEngine
from findit.engine.ocr import OCREngine
from findit.engine.sim import SimEngine

from findit.engine.base import FindItEngineResponse, FindItEngine

engine_dict = {
    "feature": FeatureEngine,
    "template": TemplateEngine,
    "ocr": OCREngine,
    "sim": SimEngine,
}
