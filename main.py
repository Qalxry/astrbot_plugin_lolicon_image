from astrbot.api.all import *
import aiohttp
import json
import time
import os

@register("setu", "rikka", "一个lolicon api的涩图插件", "1.0.0")
class setuPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config
        self.r18 = self.config.get("r18", 0) # 是否r18
        self.num = self.config.get("num", 1)    # 获取图片数量
        self.size = self.config.get("size", "regular")  # 图片大小

    @command("setu")  # 注册一个指令
    async def setu(self, event: AstrMessageEvent):
        # 获取图片
        url = f"https://api.lolicon.app/setu/v2?r18={self.r18}&num={self.num}&size={self.size}"
        # 关闭SSL验证
        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=ssl_context) as session:
            try:
                # URL发送GET请求
                async with session.get(url) as response:
                    data = await response.json()

                    if data["error"]:
                        yield event.plain_result(f"\n获取图片失败：{data['error']}")
                        return

                    if not data["data"]:
                        yield event.plain_result(f"\n未获取到图片{url}")
                        return

                    # 获取图片信息
                    image_data = data["data"][0]
                    img_pid = image_data["pid"]
                    img_title = image_data["title"]
                    image_url = image_data["urls"][self.size]

                    chain = [
                        At(qq=event.get_sender_id()),  # At 消息发送者
                        Plain("你要的涩图来咯"),  # 发送文字
                        Plain(f"\npid: {img_pid},\ntitle: {img_title}"),  # 使用换行
                        Image.fromURL(image_url),  # 发送图片
                    ]
                    yield event.chain_result(chain)
            except Exception as e:
                yield event.plain_result(f"\n获取图片失败：{e}")