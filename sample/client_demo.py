from findit.client import FindItClient
import pprint
import cv2


fic = FindItClient()
assert fic.heartbeat()
sc = cv2.imread('pics/screen.png')

# result = fic.analyse_with_path('pics/screen.png', 'wechat_logo.png')
result = fic.analyse_with_object(sc, 'wechat_logo.png')

pprint.pprint(result)
