# 太空窗 / Space Window — 家用 Wi-Fi 版

把电子胸牌变成一扇望向地球的窗口：观看 NASA 国际空间站直播，翻页查看空间站位置、高度、速度、日照状态和 UTC 时间。

**这款玩法需要 Mac 中转，并非刷入即用。** Mac 和胸牌需连接同一个可互通的家庭 Wi-Fi；Mac 必须保持运行。此版不支持仅靠手机热点在外独立播放。

## 运行中转程序

准备好依赖后，可在 Mac 上双击根目录的 `Start Relay.command`。首次会建立独立环境并安装依赖；如果系统阻止运行，请改用下面的终端步骤，不需要关闭系统安全保护。启动窗口必须保持打开。

准备 Python 3.12、Deno 及能够访问 NASA YouTube 直播的网络。Deno 请从 https://deno.com/ 获取。无需 NASA API 密钥；轨道信息来自 https://wheretheiss.at/w/developer。

```sh
cd relay
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python space_relay.py --bind 0.0.0.0
```

运行目录下会生成短期转码日志。若命令行需要使用你已配置的本地代理，可在最后加 `--proxy http://127.0.0.1:实际端口`；不要照抄别人的端口。浏览器能播放并不保证命令行能访问视频服务器。防火墙弹窗应只允许家庭局域网所需连接，不要将本程序端口转发到公网。

程序默认端口 8765。用 Mac 系统设置查看当前 Wi-Fi 的局域网 IP，胸牌中转地址填写 `http://你的Mac局域网IP:8765`。不要照抄示例 IP。`/status` 中 live=true 表示近期收到直播帧；这不证明 NASA 此时一定提供地球实景，直播可能显示通信中断提示或夜间黑画面。

NASA 直播 ID 可能变更。需要更新时，用 `--source https://www.youtube.com/watch?v=新的官方直播ID` 指定新入口。来源服务及提取方式可能变化，不承诺永久可用。

## 首次配网

1. 开机后按屏幕提示，用手机连接 SpaceWindow 热点，密码以设备屏幕显示为准。没有出现配置页时长按 OK 进入配网。
2. 手机浏览器打开 http://192.168.4.1，填写家里的 **2.4 GHz Wi-Fi** 名称和密码，以及 Mac 中转地址。
3. 点击 Save and restart，手机恢复家庭 Wi-Fi，等待胸牌自动连接。
4. 看到视频及 LIVE / DELAYED 表示已读到中转画面。SIGNAL LOST / reconnecting 表示未能继续取帧；检查 Mac、中转地址、网络隔离和来源状态。更新后的提示也可能显示 RECONNECTING。

Mac 地址变化、换 Wi-Fi 或更换中转电脑时，长按 OK 重新配置。秘密只在本地输入，不要将 Wi-Fi 密码、设备配网密码、代理凭据或日志上传到 GitHub。

## 控制与三页信息

- 上 / 下：切换 LIVE、ORBIT、LINK。
- OK 短按：暂停 / 继续视频。
- OK 双击：切换亮度。
- OK 长按：重新配网。
- LIVE：视频、高度、速度、经纬度、UTC 时间与电量。
- ORBIT：经纬度位置网格、日照区状态、轨道采样年龄。
- LINK：连接状态、Wi-Fi 信号、来源和按键说明。

轨道信息是模型估算，与视频并不同步；超过有效期的数值会隐藏。视频目标每秒约 4 帧，实际帧率、延迟取决于网络和设备。暂停画面不代表暂停真实空间站。请勿将录播当作实时备用源。

## 已验证与限制

当前发布固件已在实际设备上观察到直播、三页切换、数字、位置、时间与连接状态。断流和轨道数据过期等逻辑通过软件测试。没有测定电池续航，也不提供跨网络、移动版或云服务。

平台固件是从 0x0 刷写的完整镜像，刷入可能清除旧配置。不要将应用单镜像写入 0x0。release.json 标识经过实测的确切固件。

## English quick start

This home Wi-Fi edition requires a running Mac relay. Install Python 3.12 and Deno, install relay/requirements.txt in a virtual environment, and start `space_relay.py --bind 0.0.0.0` from relay/. An existing local proxy can be supplied with --proxy if needed. Keep the Mac and receiver on the same mutually reachable LAN; never expose the unauthenticated local relay to the public Internet.

Join the password-protected SpaceWindow hotspot using the device screen, open http://192.168.4.1, enter a 2.4 GHz home network and `http://YOUR-MAC-LAN-IP:8765`, then save. Up/down changes pages, OK pauses, double OK changes brightness, hold OK reopens setup. Video and model-based orbital estimates are not synchronized. NASA can show darkness or communications-loss notices. Battery life is unmeasured; phone-only outdoor playback is not supported.
