from findit import FindIt
import cv2
import pprint


# new one
fi = FindIt()

# load template picture
fi.load_template(pic_path='wechat_logo.png')
# or, load cv2 object
pic_object = cv2.imread('wechat_logo.png')
# pic_object is a list (or tuple): (pic_name, cv_object)
fi.load_template(pic_object_list=('wechat_logo1', pic_object))

# and find it
result = fi.find(
    # target pic
    'wechat_screen.png',

    # scale will resize template picture and auto-compare
    # (1, 3, 10) means:
    # step = (3 - 1) / 10 = 0.2
    # and, template's shape will become (1.0, 1.2, 1.4, 1.6, ... 2.6, 2.8, 3.0) times
    scale=(1, 3, 10),

    # optional:
    # mask feature, which supports template matching with transparent templates by defining a mask on the template
    # mask_pic_path='mask.png',
)

# after that, you can reset it or reuse it for another analysis.
fi.reset()

# sample result
pprint.pprint(result)
# {'config': {'cv_method': 5},
#  'data': [{'max_loc': (475.0, 344.0),
#            'max_val': 0.984991729259491,
#            'min_loc': (448.0, 392.0),
#            'min_val': -0.6493372321128845,
#            'path': 'F:\\findit\\sample\\wechat_logo.png'},
#           {'max_loc': (475.0, 344.0),
#            'max_val': 0.984991729259491,
#            'min_loc': (448.0, 392.0),
#            'min_val': -0.6493372321128845,
#            'path': 'wechat_logo1'}],
#  'target_path': './wechat_screen.png'}


# take this as a test case in travis :)
assert 'data' in result
assert len(result['data']) == 2
assert result['data'][0]['max_val'] > 0.99
assert result['data'][1]['max_val'] > 0.99
