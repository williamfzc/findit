import cv2
import os
import imutils
import numpy as np
import typing


def load_grey_from_path(pic_path: str) -> np.ndarray:
    """ load grey picture (with cv2) from path """
    raw_img = cv2.imread(pic_path)
    return load_grey_from_cv2_object(raw_img)


def load_grey_from_cv2_object(pic_object: np.ndarray) -> np.ndarray:
    """ preparation for cv2 object (force turn it into gray) """
    pic_object = pic_object.astype(np.uint8)
    grey_pic = cv2.cvtColor(pic_object, cv2.COLOR_BGR2GRAY)
    return grey_pic


def fix_location(pic_object: np.ndarray, location: typing.Sequence):
    """ location from cv2 should be left-top location, and need to fix it and make it central """
    size_x, size_y = pic_object.shape
    old_x, old_y = location
    return old_x + size_x / 2, old_y + size_y / 2


class FindItConfig(object):
    cv_method = cv2.TM_CCORR_NORMED


class FindIt(object):
    def __init__(self):
        # config
        self.config: FindItConfig = FindItConfig()

        # template pic dict,
        # { pic_name: pic_cv_object }
        self.template: typing.Dict[str, np.ndarray] = dict()

    def load_template(self, pic_path: str = None, pic_object_list: typing.Sequence = None):
        """ load template picture """
        assert (pic_path is not None) or (pic_object_list is not None), 'need path or cv object'

        if pic_object_list is not None:
            # pic_object: ('pic_name', cv_object)
            pic_name: str = pic_object_list[0]
            pic_object: np.ndarray = pic_object_list[1]
            self.template[pic_name] = load_grey_from_cv2_object(pic_object)
            return

        abs_path = os.path.abspath(pic_path)
        self.template[abs_path] = load_grey_from_path(abs_path)

    def find(self, target_pic_path: str = None, target_pic_object: np.ndarray = None, scale: typing.Sequence = None):
        """ start matching """
        assert self.template, 'template is empty'
        assert self.config.cv_method not in (cv2.TM_SQDIFF_NORMED, cv2.TM_SQDIFF), \
            'TM_SQDIFF & TM_SQDIFF_NORMED not supported'
        assert (target_pic_path is not None) or (target_pic_object is not None), 'need path or cv object'

        # load target
        if target_pic_object is not None:
            target_pic_object = load_grey_from_cv2_object(target_pic_object)
        else:
            target_pic_object = load_grey_from_path(target_pic_path)

        result: typing.List[dict] = list()
        for each_template_path, each_template_object in self.template.items():
            # default scale
            if not scale:
                scale = (1, 3, 10)

            min_val, max_val, min_loc, max_loc = self.compare(target_pic_object, each_template_object, scale)
            min_loc, max_loc = map(lambda i: fix_location(each_template_object, i), [min_loc, max_loc])

            # add to result list
            result.append({
                'path': each_template_path,
                'min_val': min_val,
                'max_val': max_val,
                'min_loc': min_loc,
                'max_loc': max_loc,
            })

        # TODO managed by developer themselves?
        self.reset()

        return {
            'target_path': target_pic_path,
            'config': self.config.__dict__,
            'data': result,
        }

    def compare(self,
                target_pic_object: np.ndarray,
                template_pic_object: np.ndarray,
                scale: typing.Sequence) -> typing.Sequence[float]:
        """
        match template between picture and template
        (https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/)

        :param target_pic_object:
        :param template_pic_object:
        :param scale: default to (1, 3, 10)
        :return: min_val, max_val, min_loc, max_loc
        """
        pic_height, pic_width = target_pic_object.shape[:2]
        result_list = list()

        for each_scale in np.linspace(*scale):
            # resize template
            resized_pic = imutils.resize(template_pic_object, width=int(template_pic_object.shape[1] * each_scale))

            # if template's size is larger than raw picture, break
            if resized_pic.shape[0] > pic_height or resized_pic.shape[1] > pic_width:
                break

            res = cv2.matchTemplate(target_pic_object, resized_pic, self.config.cv_method)
            result_list.append(cv2.minMaxLoc(res))

        # return the max one
        return sorted(result_list, key=lambda i: i[1])[-1]

    def reset(self):
        """ reset template, target and result """
        self.template = dict()
