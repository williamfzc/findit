from findit import FindIt
import cv2
import pprint
import time

# 初始化
fi = FindIt(
    # 是否需要log，默认否
    need_log=False,
    # 支持 模板匹配 与 特征识别，默认都使用
    engine=['template', 'feature'],
    # pro模式会带有更为丰富的结果数据，默认不打开
    pro_mode=False,

    # 模板匹配相关
    # 为了更好的检测率，findit专门设计了scale参数
    # 该参数会在一定范围内缩放模板图片，并进行逐一匹配
    # 默认为 (1, 3, 10) ，意思是：
    # 步长 = (3 - 1) / 10 = 0.2
    # 那么，模板图片会依次进行 (1.0, 1.2, 1.4, 1.6, ... 2.6, 2.8, 3.0) 倍的放缩逐一比较，以达到最佳的适配效果
    scale=(1, 3, 10),
    # 默认的模板匹配算法为 TM_CCORR_NORMED
    # 你也可以在此处修改为你偏好的
    cv_method_name='cv2.TM_CCORR_NORMED',
)

# 加载模板
# 1. 通过图片路径加载图片
fi.load_template('logo_from_path', pic_path='wechat_logo.png')

# 2. 或者直接加载通过cv2加载进来的图片
pic_object = cv2.imread('wechat_logo.png')
# 传入的时候注意，传入的是一个列表，形式为 （名称，图片对象）
fi.load_template('logo_from_object', pic_object=pic_object)

# 在加载模板后即可开始分析
result = fi.find(
    target_pic_name='screen',
    # 目标图片可以直接传入路径
    target_pic_path='wechat_screen.png',
    # 当然，也可以是cv2对象
    # target_pic_object=some_object,

    # 支持了蒙版图片的检测 （https://github.com/williamfzc/findit/issues/1）
    # 同样的，你可以传入图片路径或对象
    # mask_pic_path='wechat_logo.png',
    # mask_pic_object=some_object,
)

# 在分析后，你可以通过 clear 重置所有模板。当然你也可以选择保留以进行其他分析。
fi.clear()

# sample result
time.sleep(1)
pprint.pprint(result)
# {'data': {'logo_from_object': {'FeatureEngine': (514.9602695041233,
#                                                  378.0506880018446),
#                                'TemplateEngine': (475.0, 344.0)},
#           'logo_from_path': {'FeatureEngine': (514.9602695041233,
#                                                378.0506880018446),
#                              'TemplateEngine': (475.0, 344.0)}},
#  'target_name': 'screen',
#  'target_path': 'wechat_screen.png'}


# take this as a test case in travis (just a very simple check)

assert 'data' in result
assert 'target_name' in result
assert 'target_path' in result

data = result['data']
assert 'logo_from_object' in data
assert 'logo_from_path' in data

logo_from_object_result = data['logo_from_object']
logo_from_path_result = data['logo_from_path']
assert 'FeatureEngine' in logo_from_object_result
assert 'FeatureEngine' in logo_from_path_result
assert 'TemplateEngine' in logo_from_object_result
assert 'TemplateEngine' in logo_from_path_result
