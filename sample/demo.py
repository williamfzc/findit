from findit import FindIt
import cv2
import pprint


# new one
fi = FindIt()
# change config
fi.config.cv_method = cv2.TM_CCOEFF_NORMED

# load template picture
fi.load_template(pic_path='./wechat_logo.png')
# or, load cv2 object
pic_obj = cv2.imread('./wechat_logo.png')
# pic_object is a list (or tuple): (pic_name, cv_object)
fi.load_template(pic_object=('wechat_logo1', pic_obj))

# and find it
# scale will resize template picture and auto-compare
# (1, 3, 10) means looping (1.0, 1.2, 1.4, 1.6, ... 2.6, 2.8, 3.0) times
result = fi.find('./wechat_screen.png', scale=(1, 3, 10))

# result looks like:
# {
#     'some desc': 'xxx',
#     'data': {
#         'template1.png': {
#             'position': (100, 500),
#             'sim': 0.66,
#         }
#     }
# }
pprint.pprint(result)

# assert (take this as a test case ..)
assert 'data' in result
assert len(result['data']) == 2
assert result['data'][0]['max_val'] > 0.98
assert result['data'][1]['max_val'] > 0.98
