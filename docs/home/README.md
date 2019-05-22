<h1 align="center">findit</h1>
<p align="center">
    <em>Find target icon on your picture, and get its position. Painlessly, privately, standardly.</em>
</p>

---

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/findit.svg)](https://badge.fury.io/py/findit)
![Travis (.org)](https://img.shields.io/travis/williamfzc/findit.svg?label=Travis%20CI)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/williamfzc/findit.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/d824d06146383ef721c8/maintainability)](https://codeclimate.com/github/williamfzc/findit/maintainability)

---

# 简介

![cs_service](../pics/client+server.svg)

旨在提供：

- 为你、你的团队、你的自动化系统
- 规范化、安全、高效
- 跨平台与多语言
- 目标图片识别与图片管理服务

# 工作形态

findit主要以两种形态出现：

- [C/S模式](usage/client+server.md) 更加适用于正式环境，完善的部署与工作流程，同时涵盖了模板图片管理等一系列强大特性，为你的团队带来更大规模的图像识别服务。
- [python包模式](usage/normal.md) 下，findit能够直接以常规第三方库的形式嵌入到你的工作框架中，为你的框架提供原生的图像识别能力。

# 相关参考

![](../pics/feature_matching_sample.png)

findit 主要用到了 feature matching 与 template matching 。

- [feature matching](https://docs.opencv.org/3.4/dc/dc3/tutorial_py_matcher.html)
- [template matching](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html)

# 旧版本

稳定（旧）版本会存在于 [stable 分支](https://github.com/williamfzc/findit/tree/stable) 并在重要节点同步。

# LICENSE

[MIT](LICENSE)
