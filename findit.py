import cv2
import os


class FindItConfig(object):
    cv_method = cv2.TM_SQDIFF_NORMED


def load_grey_from_path(pic_path):
    """ load grey picture (with cv2) from path """
    raw_img = cv2.imread(pic_path)
    grey_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
    return grey_img


class FindIt(object):
    def __init__(self):
        # config
        self.config = FindItConfig()
        # template pic dict,
        # { pic_name: pic_cv_object }
        self.template = dict()
        # target picture path
        self.target_name = None
        self.target_path = None
        # result dict
        self.result = dict()

    def get_pic_name(self, pic_path):
        """ confirm picture is existed and get its name """
        assert os.path.isfile(pic_path), 'picture not found: {}'.format(pic_path)
        pic_name = os.path.basename(pic_path)
        assert pic_name not in self.template, 'picture already existed'
        return pic_name

    def load_template(self, pic_path):
        """ load template picture """
        pic_name = self.get_pic_name(pic_path)
        self.template[pic_name] = load_grey_from_path(pic_path)

    def find(self, target_pic_path):
        """ start matching """
        assert self.template, 'template is empty'
        pic_name = self.get_pic_name(target_pic_path)
        target_pic = load_grey_from_path(target_pic_path)
        for each_template_name, each_template in self.template.items():
            self.result[each_template_name] = self.compare(target_pic, each_template)
        self.target_name = pic_name
        self.target_path = target_pic_path
        return self.build_result()

    def compare(self, pic, template_pic):
        res = cv2.matchTemplate(pic, template_pic, self.config.cv_method)
        return cv2.minMaxLoc(res)

    def build_result(self):
        """ build final result dict """
        final_result = dict()
        final_result['target_name'] = self.target_name
        final_result['target_path'] = self.target_path
        final_result['config'] = self.config.__dict__
        final_result['data'] = self.result

        return final_result
