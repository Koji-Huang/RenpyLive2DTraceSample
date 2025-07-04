# RenpyLive2DTraceSample

---

>   这个项目里包含了通过  Pymouth 脚本, OpenSeeFace 软件来实现 Renpy 动作追踪的示例, 实现的思路是在 Pymouth, OpenSeeFace 处理好动作数据后通过端口通信将数据重新映射到 Renpy 的 Live2D 组件上
>
>   如果你不明白为什么这些代码能让动作作用在模型上生效的话, 可以去看看我写的一篇 Markdown - 自定义 Live2D 组件动作的一些思路. 这个 Markdown 在我的另一个仓库 KojiRenpyBox 的 Markdown 文件夹里

---

## 使用:

>   给你的 Renpy 安装好 Live2D SDK 后, 将此工程复制到一个文件夹里并通过 Renpy 打开它, 此外因为这个工程需要使用端口通信, 所以可能会因为一些奇奇怪怪的网络问题而无法正常运行, 如果出现数据无法传出传入的问题请自行排查问题

### Pymouth

>   pymouth 是一个 python 第三方库, 作用是将声音数据转换为 Live2D 模型通用的日语口型参数, 即使我认为 pymouth 的口型追踪并没有达到完美无缺的地步, 但作为一个示例项目来说绝对够用了, 项目地址: https://github.com/organics2016/pymouth
>
>   如何调用 pymouth 并发送到端口上:
>
>   >   在通过 pip 给 python 安装好 pymouth 后, 可以使用一个简单的脚本来调用这个库并把数据通过 UDP 端口发送 ( 注意, `output_device`参数是各个设备不一样的, 请参照 pymouth 仓库文档的内容进行配置 ), 这个脚本我扔在项目的根目录下了
>   >
>   >   ```python
>   >   import pymouth
>   >   import time
>   >   import socket
>   >   import struct
>   >   
>   >   FILE = 'test.flac'
>   >   HOST = '127.0.0.1'
>   >   PORT = 8000
>   >   
>   >   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
>   >   
>   >   def callback(md: dict[str, float], data):
>   >      data = bytes()
>   >      for key, value in md.items():
>   >          print(key, "%.4f" % value)
>   >          data += struct.pack('f', value)
>   >      s.sendto(data, (HOST, PORT))
>   >   
>   >   
>   >   with pymouth.VowelAnalyser() as a:
>   >      a.action_noblock(FILE, 44100, output_device=6, callback=callback, auto_play=True)  # no block
>   >      print("end")
>   >      time.sleep(1000000)
>   >   ```
>   >
>   >   如果配置得当的话, 在命令行出现 `end`  后不久, 系统会播放 `test.flac` 文件 (这个文件自行准备吧,当然其他格式的音频文件大概也是支持的) 并且会在命令行上打印出对应的口型数据, 此时相关的参数会以 UDP 协议发送到 `127.0.0.1:8000` 端口上
>   >
>   >   另外, 我没有验证过 pymouth 是否可以直接在 Renpy 环境下运行, 如果可以的话就不需要端口通信了, 还可以直接通过字节流将数据发送给 pymouth 处理, 实现不需要原始音频文件都可以自动对口型 ( 虽然我认为提前生成好口型再调用更好一点, 反正占不了多少存储 )
>
>   1.   打开项目下的 `game/script/pymouth_ren.py` 文件, 将最后一行的 `mouth_thread.start()` 取消注释
>   2.   打开 `game/script.rpy` 启用 `Pymouth 追踪` 的 `image mao` 代码
>   3.   注释掉 `game/script.rpy` 其他的 `image mao`
>   4.   打开游戏, 配置正常的情况下此时游戏内的 Live2D 模型会根据接收到的  Pymouth 数据改变口型
>   5.   运行上面的脚本, 一切正常的情况下, 当脚本有数据输出时, 游戏内的模型就会根据数据改变口型

### OpenSeeFace

>   OpenSeeFace 是一个脸型追踪工具, 我们需要借用这个库来帮我们生成脸型追踪数据, 项目地址: https://github.com/emilianavt/OpenSeeFace
>
>   我已经在项目里塞进了一整个 OpenSeeFace 包, 为的是确保 OpenSeeFace 的版本与我写的代码兼容, 如何使用 OpenSeeFace 就请参照 OpenSeeFace 的文档了
>
>   1.   打开项目下的 `game/script/pymouth_ren.py` 文件, 将最后一行的 `osf_thread.start()` 取消注释
>   2.   打开 `game/script.rpy`, 找到并启用 `OSF 追踪` 的 `image mao` 代码
>   3.   注释掉 `game/script.rpy` 其他的 `image mao`
>   4.   打开游戏, 配置正常的情况下此时游戏内的 Live2D 模型会根据接收到的  OpenSeeFace 数据改变口型
>   5.   运行 OpenSeeFace, 一切正常的情况下, 当 OpenSeeFace 有数据输出时, 游戏内的模型会根据 OpenSeeFace 的参数改变头部的摆动和眼睛的开合 (其他的适配懒得写了, 我这里重点是实现传递而不是效果本身的质量)

---

## 实现手段

### 获取模型所有可用的参数

>   简单的来说就是在显示模型时输入一串代码: 
>
>   `tuple(renpy.gl2.live2d.states.get(('mao', )).new.common.model.parameters)`
>
>   这里的 ('mao', ) 为正在显示的 Live2D 模型 Tag, 详细的说明如下:
>
>   1.   首先, Live2D 模型在被显示后的时候会被存入 `renpy.gl2.live2d.states` 里, 这个项目里我们用的模型叫做 `'mao'`, 那么在显示 Live2D 模型时, 我们可以通过 `renpy.gl2.live2d.states[('mao',)]` 来获取到那个显示着的 `Live2DState` 对象 ( 注意, `renpy.gl2.live2d.states['mao']` 获取到的东西和 `renpy.gl2.live2d.states[('mao',)]` 是不一样的 )
>   2.   Live2DState 对象下有一个 `new` 参数, 这个参数对应着显示着的 Live2D 对象, 这个对象是显示在屏幕上最新的 Live2D 对象, 与之相对的有一个 `old` 参数, 这个参数储存着上一个 Live2D 对象, 用于过渡动画
>   3.   Live2D 对象有一个 common 参数, 这个参数为一个 Live2DCommon 对象, 这个对象是储存参数与应用模型的对象
>   4.   Live2DCommon 对象的 model 参数为此 Live2D 对象渲染的模型对象, 为一个 Live2DModel 对象, 这个对象储存了模型的相关参数
>   5.   Live2DModel 对象的 parameters 参数就是这个 Live2D 文件读取到的所有参数(为一个字典对象), 我们可以用 tuple 将这个参数转换并打印出来供我们参考, 此时我们就获取到了这个模型所有可用的参数

### 值映射

>   请看文档: https://doc.renpy.cn/zh-CN/live2d.html#blend_parameter
>
>   上面我们获取到的参数就是在这里用的, 如果你看过 `game/script/osf_ren.py`, `game/scripy/pymouth_ren.py` 文件的话你可以看到里面的 `xxx_update_function` 里全是在用 `blend_parameter` 函数来对值进行映射

### 对 OpenSeeFace 的兼容

>   对 OpenSeeFace 使用 --help 命令我们可以看到这样的内容:
>
>   >   ```
>   >     -i IP, --ip IP        Set IP address for sending tracking data (default:
>   >                           127.0.0.1)
>   >     -p PORT, --port PORT  Set port for sending tracking data (default: 11573)
>   >   ```
>
>   由此可知 OpenSeeFace 的默认发送端口为 `127.0.0.1:11573`, 使用 Wireshark 监听这个端口可以找到所有的信息包, 但是这里面的信息全是未编码的信息流, OpenSeeFace 文档里也完全没有提到要怎么解包这些信息流, 再阅读 OpenSeeFace 的文档, 你可以看到他对于参数传出的内容为:
>
>   >   The script will perform the tracking on webcam input or video file and send the tracking data over UDP. This design also allows tracking to be done on a separate PC from the one who uses the tracking information. This can be useful to enhance performance and to avoid accidentially revealing camera footage.
>   >
>   >   The provided `OpenSee` Unity component can receive these UDP packets and provides the received information through a public field called `trackingData`. The `OpenSeeShowPoints` component can visualize the landmark points of a detected face. It also serves as an example. Please look at it to see how to properly make use of the `OpenSee` component. Further examples are included in the `Examples` folder. The UDP packets are received in a separate thread, so any components using the `trackingData` field of the `OpenSee` component should first copy the field and access this copy, because otherwise the information may get overwritten during processing. This design also means that the field will keep updating, even if the `OpenSee` component is disabled.
>
>   拿翻译器翻译一下:
>
>   >   该脚本将对网络摄像头输入或视频文件执行跟踪，并通过 UDP 发送跟踪数据。这种设计还允许在与使用跟踪信息的电脑不同的电脑上进行跟踪。这有助于提高性能并避免意外泄露摄像头素材。
>   >
>   >   提供的 OpenSee Unity 组件可以接收这些 UDP 数据包，并通过名为 TrackingData 的公共字段提供接收到的信息。OpenSeeShowPoints 组件可以可视化检测到的人脸的界标点。它也可以作为一个示例。请查看该示例以了解如何正确使用 OpenSee 组件。更多示例包含在“示例”文件夹中。UDP 数据包在单独的线程中接收，因此任何使用 OpenSee 组件的 TrackingData 字段的组件都应首先复制该字段并访问此副本，否则信息可能会在处理过程中被覆盖。这种设计还意味着即使 OpenSee 组件被禁用，该字段也会持续更新。
>
>   所以在使用 Wireshark 监听了半天端口看那毫无厘头的数据后, 我打开了 OpenSeeFace Unity 文件夹下的第一个文件 OpenSee.cs 看了起来
>
>   然后看到了 `public void readFromPacket` 函数....
>
>   然后发现这个函数就是处理信息流的函数, 
>
>   然后继续看下去, 得知了所有参数位于数据包的位置, 格式....
>
>   然后写了一个 Python 脚本, 确认了这些数据的格式是正确的
>
>   然后在对 OpenSee.cs 一番 Ctrl CV 与修改后, 这个兼容就完成了
>
>   需要注意的是, OpenSee.cs 里有两个参数 rightGaze 和 leftGaze 是算出来的, 他们并不是通过 UDP 发送出来的, 这两个参数的算法涉及到一些我无法解决的数学知识, 所以我也就没写了, 其他的所有参数我都写好了兼容, 在 `osf_update_socket` 函数里
