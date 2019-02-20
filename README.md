# findit

利用opencv，对图像进行模板匹配，并得到模板在图片中出现与否及其位置。

## 使用

```python
from findit import FindIt
import cv2
import pprint


fi = FindIt()
# 配置算法（SQDIFF系列不支持）
fi.config.cv_method = cv2.TM_CCOEFF_NORMED

# 加载模板
fi.load_template('./wechat_logo.png')

# 在目标图片中寻找
# 在很多时候，模板图片的分辨率很可能与目标图片是不一致的，这会导致模板匹配失效
# scale会将模板图片进行缩放，并逐一进行比较，寻找最匹配的分辨率
# (1, 3, 10) 的意思是 放大倍数为 1倍~3倍，步长为 2/10 = 0.2
result = fi.find('./wechat_screen.png', scale=(1, 3, 10))
pprint.pprint(result)

# 可能的结果
"""
{
     'config': {'cv_method': 5},
     'data': [{'max_loc': (475.0, 344.0),
               'max_val': 0.9855659604072571,
               'min_loc': (448.0, 392.0),
               'min_val': -0.6501237154006958,
               'name': 'wechat_logo.png',
               'path': 'F:\\findit\\sample\\wechat_logo.png'}],
     'target_name': 'wechat_screen.png',
     'target_path': 'F:\\findit\\sample\\wechat_screen.png'
}
"""
```

可以浏览[示例项目](sample)。
