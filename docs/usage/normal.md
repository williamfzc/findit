# 常规模式

## 在开始前

比起直接接入 findit包，对于大多数开发者而言，更为推荐的是接入 findit-client 。

- 更为清晰且丰富的API，支持相同甚至更多的功能
- 更加简单易用，无需自己进行数据处理
- 依赖少，兼容性强
- 灵活（client能够连接本地或远程的服务。如果你并不希望把server部署到远程，你可以非常方便地在本地启动服务器并接入它）
- 与代码库分离的规范化图片管理

你可以看看再决定：[python client 传送门](https://github.com/williamfzc/findit-client)

当然，我们肯定不会阻止你直接使用它。如果你决定不用client，请继续往下阅读：）

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

或者直接[通过docker使用](https://williamfzc.github.io/findit/#/usage/client+server?id=%e7%94%a8-docker-%e9%83%a8%e7%bd%b2)，docker镜像默认使用最新的代码进行构建。

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

## 配置

findit提供的配置方式保证了它能够灵活地响应参数。

- 在 findit 初始化时会对 engine 进行初始化，在此处传入的参数将会传入 engine 的 `__init__` 方法，进而影响初始化 engine 的默认行为。传入的具体参数名称可以参考对应 engine 的 `__init__` 方法

    ```python
    # 例如，将ocr语言设定为 chi_sim+eng
    fi = FindIt(engine=['ocr'], engine_ocr_lang='chi_sim+eng')
    ```

- 在 find 方法被调用时，此处传入的参数将会传入 engine 的 `execute` 方法，进而影响 engine 的单次行为。传入的具体参数名称可以参考对应 engine 的 `execute` 方法
- 所有的引擎参数均以 `engine_引擎类型_参数名` 的形式存在。例如，ocr引擎中的语言设置即对应 `engine_ocr_lang` 
