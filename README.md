<h1 align="center">findit</h1>
<p align="center">
    <em>利用opencv，对图像进行模板匹配，并得到模板在图片中出现与否及其位置。</em>
</p>

---

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/findit.svg)](https://badge.fury.io/py/findit)
[![Build Status](https://travis-ci.org/williamfzc/findit.svg?branch=master)](https://travis-ci.org/williamfzc/findit)
[![Maintainability](https://api.codeclimate.com/v1/badges/d824d06146383ef721c8/maintainability)](https://codeclimate.com/github/williamfzc/findit/maintainability)

---

# 定位

该工具主要作为基础组件出现，用于在目标图像中寻找模板图片的位置。

![feature_matching](sample/pics/feature_matching_sample.png)

目前，[stagesep2](https://github.com/williamfzc/stagesep2) 与 [fitch](https://github.com/williamfzc/fitch) 均使用该工具作为图像处理引擎。

# 使用

请参见 [官方wiki](https://github.com/williamfzc/findit/wiki)

# 相关参考

findit 主要用到了 feature matching 与 template matching 。

- [feature matching](sample/how_feature_matching_works.py)
- [template matching](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html)

# 旧版本

稳定（旧）版本会存在于 [stable 分支](https://github.com/williamfzc/findit/tree/stable) 并在重要节点同步。

# LICENSE

[MIT](LICENSE)
