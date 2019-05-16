# findit

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/findit.svg)](https://badge.fury.io/py/findit)
[![Build Status](https://travis-ci.org/williamfzc/findit.svg?branch=master)](https://travis-ci.org/williamfzc/findit)
[![Maintainability](https://api.codeclimate.com/v1/badges/d824d06146383ef721c8/maintainability)](https://codeclimate.com/github/williamfzc/findit/maintainability)

利用opencv，对图像进行模板匹配，并得到模板在图片中出现与否及其位置。

## 定位

该工具主要作为基础组件出现，用于在目标图像中寻找模板图片的位置。

![feature_matching](sample/feature_matching_sample.png)

目前，[stagesep2](https://github.com/williamfzc/stagesep2) 与 [fitch](https://github.com/williamfzc/fitch) 均使用该工具作为图像处理引擎。

## 使用场景

例如你有两张图片，分别是微信图标：

![wechat_icon](sample/wechat_logo.png)

与包含微信图标的手机截图：

![wechat_screen](sample/wechat_screen.png)

那么，你只需要：

```python
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
```

就可以得到：

```text
{'data': {'app_store_logo': {'FeatureEngine': (94.66734313964844,
                                               380.8362731933594),
                             'TemplateEngine': (56.0, 340.0)},
          'wechat_logo': {'FeatureEngine': (528.9216674804687,
                                            383.21449890136716),
                          'TemplateEngine': (475.0, 344.0)}},
 'target_name': 'screen',
 'target_path': 'wechat_screen.png'}
```

通过上述数据可以知道，微信图标最可能出现的点位：

- Feature Matching 的计算结果是 `(528, 383)`
- Template Matching 的计算结果是 `(475, 344)`

你还可以打开专业模式用于更加全面的数据：

```text
{'data': {'logo': {'FeatureEngine': {'raw': [(478.89141845703125,
                                              401.2875671386719),
                                             ...
                                             (538.511962890625,
                                              419.835693359375)],
                                     'target_point': (514.9602440728081,
                                                      378.0506947835286)},
                   'TemplateEngine': {'raw': {'max_loc': (475.0,
                                                          344.0),
                                              'max_val': 0.998754620552063,
                                              'min_loc': (39.0,
                                                          30.0),
                                              'min_val': 0.8025140762329102},
                                      'target_point': (475.0,
                                                       344.0),
                                      'target_sim': 0.998754620552063}},
 'target_name': 'screen',
 'target_path': 'wechat_screen.png'}
```

更多丰富用法请参考 [demo.py](sample/demo.py)。

## 安装

python3.6+

```bash
pip install findit
```

## 相关参考

- [feature matching](sample/how_feature_matching_works.py)
- [template matching](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html)

## 旧版本

稳定（旧）版本会存在于 [stable 分支](https://github.com/williamfzc/findit/tree/stable) 并在重要节点同步。

## LICENSE

[MIT](LICENSE)
