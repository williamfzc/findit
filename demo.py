from findit import FindIt
import cv2
import pprint


# new one
fi = FindIt()
# change config
fi.config.cv_method = cv2.TM_SQDIFF_NORMED
# load template picture
fi.load_template('./point.png')
# and find it
result = fi.find('./screen2.png')

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
