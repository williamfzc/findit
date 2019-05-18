import pprint
from findit import FindIt

fi = FindIt()
fi.load_template('wechat_logo', pic_path='pics/wechat_logo.png')
fi.load_template('app_store_logo', pic_path='pics/app_store_logo.png')
fi.load_template('music_logo', pic_path='pics/music_logo.png')
fi.load_template('album_logo', pic_path='pics/album_logo.png')

result = fi.find(
    target_pic_name='screen',
    target_pic_path='pics/screen.png',
)

pprint.pprint(result)
