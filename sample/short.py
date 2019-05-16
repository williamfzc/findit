import pprint
from findit import FindIt

fi = FindIt()
fi.load_template('wechat_logo', pic_path='wechat_logo.png')
fi.load_template('app_store_logo', pic_path='app_store_logo.png')

result = fi.find(
    target_pic_name='screen',
    target_pic_path='wechat_screen.png',
)

pprint.pprint(result)
