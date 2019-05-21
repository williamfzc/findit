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

    # 引擎相关参数均为engine开头
    # 模板匹配相关
    # 为了更好的检测率，findit专门设计了scale参数
    # 该参数会在一定范围内缩放模板图片，并进行逐一匹配
    # 默认为 (1, 3, 10) ，意思是：
    # 步长 = (3 - 1) / 10 = 0.2
    # 那么，模板图片会依次进行 (1.0, 1.2, 1.4, 1.6, ... 2.6, 2.8, 3.0) 倍的放缩逐一比较，以达到最佳的适配效果
    engine_template_scale=(1, 3, 10),
    # 默认的模板匹配算法为 TM_CCORR_NORMED
    # 你也可以在此处修改为你偏好的
    engine_template_cv_method_name='cv2.TM_CCORR_NORMED',

    # 特征识别相关
    # 距离阈值
    engine_feature_distance_threshold=0.75,
    # 聚类核心数
    engine_feature_cluster_num=3,
)

# 加载模板
# 1. 通过图片路径加载图片
fi.load_template('wechat_logo', pic_path='pics/wechat_logo.png')

# 2. 或者直接加载通过cv2加载进来的图片
pic_object = cv2.imread('pics/app_store_logo.png')
# 传入的时候注意，传入的是一个列表，形式为 （名称，图片对象）
fi.load_template('app_store_logo', pic_object=pic_object)

# 在加载模板后即可开始分析
result = fi.find(
    target_pic_name='screen',
    # 目标图片可以直接传入路径
    target_pic_path='pics/screen.png',
    # 当然，也可以是cv2对象
    # target_pic_object=some_object,

    # 支持了蒙版图片的检测 （https://github.com/williamfzc/findit/issues/1）
    # 同样的，你可以传入图片路径或对象
    # mask_pic_path='wechat_logo.png',
    # mask_pic_object=some_object,

    # 如果你希望确认分析结果，你可以打开 mark_pic 开关
    # 打开后，将会保存一张 标记了最终结果 的图片到本地，供参考用
    # mark_pic=True,
)

# 在分析后，你可以通过 clear 重置所有模板。当然你也可以选择保留以进行其他分析。
fi.clear()

# sample result
time.sleep(1)
pprint.pprint(result)
# {'data': {'app_store_logo': {'FeatureEngine': (94.66734313964844,
#                                                380.8362731933594),
#                              'TemplateEngine': (56.0, 340.0)},
#           'wechat_logo': {'FeatureEngine': (528.9216674804687,
#                                             383.21449890136716),
#                           'TemplateEngine': (475.0, 344.0)}},
#  'target_name': 'screen',
#  'target_path': 'wechat_screen.png'}


# take this as a test case in travis (just a very simple check)

# TODO move these to test case
assert 'data' in result
assert 'target_name' in result
assert 'target_path' in result

data = result['data']
app_store_logo_result = data['app_store_logo']
wechat_logo_result = data['wechat_logo']
assert 'FeatureEngine' in app_store_logo_result
assert 'FeatureEngine' in wechat_logo_result
assert 'TemplateEngine' in app_store_logo_result
assert 'TemplateEngine' in wechat_logo_result
