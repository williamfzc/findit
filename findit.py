import cv2
import os
import imutils
import numpy as np


class FindItConfig(object):
    cv_method = cv2.TM_CCORR_NORMED


def load_from_path(pic_path):
    """ load grey picture (with cv2) from path """
    raw_img = cv2.imread(pic_path)
    return prepare_pic(raw_img)


def prepare_pic(pic_object):
    raw_img = pic_object.astype(np.uint8)
    grey_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
    return grey_img


class FindIt(object):
    def __init__(self):
        # config
        self.config = FindItConfig()
        # template pic dict,
        # { pic_name: pic_cv_object }
        self.template = dict()

    def load_template(self, pic_path=None, pic_object=None):
        """ load template picture """
        assert (pic_path is not None) or (pic_object is not None), 'need path or cv object'
        if pic_object is not None:
            # pic_object: ('pic_name', cv_object)
            pic_name = pic_object[0]
            pic_data = pic_object[1]
            self.template[pic_name] = prepare_pic(pic_data)
            return
        abs_path = os.path.abspath(pic_path)
        self.template[abs_path] = load_from_path(abs_path)

    def find(self, target_pic_path=None, target_cv_object=None, scale=None):
        """ start matching """
        assert self.template, 'template is empty'
        assert self.config.cv_method not in (cv2.TM_SQDIFF_NORMED, cv2.TM_SQDIFF), \
            'TM_SQDIFF & TM_SQDIFF_NORMED not supported'
        assert (target_pic_path is not None) or (target_cv_object is not None), 'need path or cv object'

        # load target
        if target_cv_object is not None:
            target_pic = prepare_pic(target_cv_object)
        else:
            target_pic = load_from_path(target_pic_path)

        result = list()
        for each_template_path, each_template in self.template.items():
            # default scale
            if not scale:
                scale = (1, 3, 10)

            min_val, max_val, min_loc, max_loc = self.compare(target_pic, each_template, scale)
            min_loc, max_loc = map(lambda i: self.fix_location(each_template, i), [min_loc, max_loc])

            # add to result list
            result.append({
                'path': each_template_path,
                'min_val': min_val,
                'max_val': max_val,
                'min_loc': min_loc,
                'max_loc': max_loc,
            })

        self.reset()
        return self.build_result(target_pic_path, result)

    @staticmethod
    def fix_location(pic_object, location):
        """ location from cv2 should be left-top location, and need to fix it and make it central """
        size_x, size_y = pic_object.shape
        old_x, old_y = location
        return old_x + size_x / 2, old_y + size_y / 2

    def compare(self, pic, template_pic, scale):
        """
        match template between picture and template
        (https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/)

        :param pic:
        :param template_pic:
        :param scale: default to (1, 3, 10)
        :return:
        """
        pic_height, pic_width = pic.shape[:2]
        result_list = list()

        for each_scale in np.linspace(*scale):
            # resize template
            resized_pic = imutils.resize(template_pic, width=int(template_pic.shape[1] * each_scale))

            # if template's size is larger than raw picture, break
            if resized_pic.shape[0] > pic_height or resized_pic.shape[1] > pic_width:
                break

            res = cv2.matchTemplate(pic, resized_pic, self.config.cv_method)
            result_list.append(cv2.minMaxLoc(res))

        # return the max one
        return sorted(result_list, key=lambda i: i[1])[-1]

    def build_result(self, target_path, result):
        """ build final result dict """

        return {
            'target_path': target_path,
            'config': self.config.__dict__,
            'data': result,
        }

    def reset(self):
        """ reset template, target and result """
        self.template = dict()
