# findit

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/findit.svg)](https://badge.fury.io/py/findit)
[![Build Status](https://travis-ci.org/williamfzc/findit.svg?branch=master)](https://travis-ci.org/williamfzc/findit)
[![Maintainability](https://api.codeclimate.com/v1/badges/d824d06146383ef721c8/maintainability)](https://codeclimate.com/github/williamfzc/findit/maintainability)

利用opencv，对图像进行模板匹配，并得到模板在图片中出现与否及其位置。

## 定位

该工具主要作为基础组件出现，用于在目标图像中寻找模板图片的位置。

![feature_matching](sample/pics/feature_matching_sample.png)

目前，[stagesep2](https://github.com/williamfzc/stagesep2) 与 [fitch](https://github.com/williamfzc/fitch) 均使用该工具作为图像处理引擎。

## 使用场景

例如你有两张图片，分别是微信图标：

![wechat_icon](sample/pics/wechat_logo.png)

与包含微信图标的手机截图：

![wechat_screen](sample/pics/screen.png)

那么，你只需要：

```python
import pprint
from findit import FindIt

fi = FindIt()
fi.load_template('wechat_logo', pic_path='pics/wechat_logo.png')
fi.load_template('app_store_logo', pic_path='pics/app_store_logo.png')

result = fi.find(
    target_pic_name='screen',
    target_pic_path='pics/screen.png',
)

pprint.pprint(result)
```

就可以得到：

```text
{'data': {'app_store_logo': {'FeatureEngine': (96.2968017578125,
                                               386.9249633789062),
                             'TemplateEngine': (92.0, 382.0)},
          'wechat_logo': {'FeatureEngine': (524.6688232421875, 364.54248046875),
                          'TemplateEngine': (505.5, 374.5)}},
 'target_name': 'screen',
 'target_path': 'pics/screen.png'}
```

通过上述数据可以知道，微信图标最可能出现的点位：

- Feature Matching 的计算结果是 `(524, 364)`
- Template Matching 的计算结果是 `(505, 374)`

上述完整例子与图片在[sample](sample)中。更多进阶用法请参考 [sample/demo.py](sample/demo.py)。

## 安装

python3.6+

```bash
pip install findit
```

另外，如果你希望体验未发布的最新特性，你可以选择从源码安装：

```bash
git clone https://github.com/williamfzc/findit.git
cd findit
pip install -e .
```

## 相关参考

- [feature matching](sample/how_feature_matching_works.py)
- [template matching](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html)

## 旧版本

稳定（旧）版本会存在于 [stable 分支](https://github.com/williamfzc/findit/tree/stable) 并在重要节点同步。

## LICENSE

[MIT](LICENSE)
