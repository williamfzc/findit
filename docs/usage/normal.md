# 常规模式

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

## 使用

例如你有两张图片，分别是微信图标：

![wechat_icon](../pics/wechat_logo.png)

与包含微信图标的手机截图：

![wechat_screen](../pics/screen.png)

那么，你只需要：

```python
import pprint
from findit import FindIt

fi = FindIt()
fi.load_template('wechat_logo', pic_path='pics/wechat_logo.png')

result = fi.find(
    target_pic_name='screen',
    target_pic_path='pics/screen.png',
)

pprint.pprint(result)
```

就可以得到：

```text
{'data': { 'wechat_logo': {'FeatureEngine': (524.6688232421875, 364.54248046875),
                           'TemplateEngine': (505.5, 374.5)}},
 'target_name': 'screen',
 'target_path': 'pics/screen.png'}
```

通过上述数据可以知道，微信图标最可能出现的点位：

- Feature Matching 的计算结果是 `(524, 364)`
- Template Matching 的计算结果是 `(505, 374)`

上述完整例子与图片在[sample](https://github.com/williamfzc/findit/tree/master/sample)中。更多进阶用法请参考 [sample/demo.py](https://github.com/williamfzc/findit/tree/master/sample/demo.py)。
