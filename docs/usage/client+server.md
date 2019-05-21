# Client/Server 模式

为了后续更好的应用，findit的理论形态应该是配置在服务器上。主要有两个问题：

- 图像识别效果更精确势必需要更高的算力。服务化之后，计算部分可以使用局域网内更高配置的机器来执行。
- 顺带解决大量模板图片的管理问题。

![](https://user-images.githubusercontent.com/13421694/57979135-c6ebf880-7a4b-11e9-87bc-5b80e0756d35.png)

通过配置，findit-client 能够连接到本地或者远程的 findit-server，以适应不同的需求。换言之，你可以在其他设备上使用client直接调用远程的findit，而本地无需opencv环境。这种做法使得你能够在更低配置的客户机（例如树莓派等）上使用findit服务。

## 服务端部署

服务端需求 python3.6+，**强烈推荐**用 docker 与 docker-compose 部署。

完整服务包括三个部分：

- 文件管理UI（端口29410）
- nginx文件服务器（端口29411）
- findit服务（端口29412）

你只需要执行下列命令就可以部署上述服务：

```bash
git clone https://github.com/williamfzc/findit.git
cd findit

# docker-compose.yml 可以根据实际需要修改
docker-compose up -d
```

简而言之，你可以在文件管理器上直接管理你的资源，并让它被findit使用。文件管理器来自 [filebrowser](https://github.com/filebrowser/filebrowser)。

## 客户端配置

客户端通过http请求与服务端进行通信，并以此获取findit的能力。也就是说：

- 它并不需要很高的性能，因为计算都是在服务端进行的，所以你大可以在低端机器（例如树莓派）上使用客户端
- 依赖非常少，甚至可以无需opencv
- 多语言支持！

客户端项目：https://github.com/williamfzc/findit-client

## 一个完整例子

以下例子以本地为例，远程部署同理。

例如你有两张图片，分别是微信图标：

![wechat_icon](../pics/wechat_logo.png)

与包含微信图标的手机截图：

![wechat_screen](../pics/screen.png)

我们希望找到微信图标在手机截图出现的位置。

1. 首先通过浏览器进入文件管理器 `127.0.0.1:29410`，账号密码`admin`。

2. 创建一个文件夹 `desktop`，上传微信图标 `wechat_logo.png`。

![filebrowser](https://user-images.githubusercontent.com/13421694/57979536-ab83ec00-7a51-11e9-9260-be06e5820683.png)

3. 服务端配置就完成了！可以在 `127.0.0.1:29411` 上看到你的图片。接下来你就可以直接在 client 中根据路径来使用。

4. 新建一个python脚本，用client进行操作：

```bash
from findit_client import FindItClient

# 初始化
cli = FindItClient(port=29412)
assert cli.heartbeat()

# 假设你的手机截图路径是 screen.png
# wechat_logo刚才被我们放在desktop目录下了，按照实际写就可以
result = cli.analyse_with_path('screen.png', 'desktop/wechat_logo.png')

print(result)
```

你可以获得跟本地一样的识别效果。

```text
{'data': {'temp_template': {'FeatureEngine': [524.6688232421875,
                                              364.54248046875],
                            'TemplateEngine': [505.5, 374.5]}},
 'target_name': 'temp_target',
 'target_path': '/tmp/tmprh4m59_x.png'}
```
