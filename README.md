# findit

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/findit.svg)](https://badge.fury.io/py/findit)
[![Build Status](https://travis-ci.org/williamfzc/findit.svg?branch=master)](https://travis-ci.org/williamfzc/findit)

利用opencv，对图像进行模板匹配，并得到模板在图片中出现与否及其位置。

## 用途

该工具主要作为基础组件出现。

例如你有两张图片，分别是微信图标：

![wechat_icon](sample/wechat_logo.png)

与包含微信图标的手机截图：

![wechat_screen](sample/wechat_screen.png)

那么，通过这个工具，你可以得到：

```text
{'cv_method': 'cv2.TM_CCORR_NORMED',
 'data': [{'max_loc': (475.0, 344.0),
           'max_val': 0.9987547993659973,
           'min_loc': (39.0, 30.0),
           'min_val': 0.8024401664733887,
           'path': 'wechat_logo1'}],
 'target_path': 'wechat_screen.png'}
```

通过上述数据可以知道，微信图标出现在`(475.0, 344.0)`的概率超过了0.99。

## 使用

可以浏览[demo.py](sample/demo.py)。

## LICENSE

[MIT](LICENSE)
