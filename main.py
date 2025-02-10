from astrbot.api.all import *
import aiohttp
import time
import json


@register("setu", "rikka", "一个lolicon api的涩图插件", "1.0.0")
class SetuPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        self.r18 = self.config.get("r18", 0)  # 是否R18
        self.num = self.config.get("num", 1)  # 获取图片数量
        self.size = self.config.get("size", "regular")  # 图片大小
        self.cooldown_duration = self.config.get("time", 0)  # 默认冷却时间为30秒
        self.cooldowns = {}

    @command("setu")  # 注册一个指令
    async def setu(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())  # 获取用户ID并转为字符串
        current_time = int(time.time())

        # 检查冷却状态
        user_cooldown = self.cooldowns.get(user_id, 0)  # 获取用户的冷却时间，如果没有则默认为0

        if user_cooldown > current_time:  # 如果用户的冷却时间大于当前时间
            remaining_time = user_cooldown - current_time
            yield event.plain_result(f"涩图冷却中，请等待 {remaining_time} 秒后再试。")
            return

        # 更新用户的冷却时间
        self.cooldowns[user_id] = current_time + self.cooldown_duration
        print(f"用户{user_id} 剩余冷却时间: {self.cooldowns[user_id] - current_time}, 冷却持续时间: {self.cooldown_duration}")

        # 从用户消息中获取tag（假设用户输入格式为 "setu tag1 tag2"）
        tags = event.get_message_str().split()[1:]  # 获取所有tag
        tag_param = '&tag='.join(tags)  # 将tag合并为字符串

        # 获取图片
        url = f"https://api.lolicon.app/setu/v2?r18={self.r18}&num={self.num}&size={self.size}&tag={tag_param}"
        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=ssl_context) as session:
            try:
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
                    img_tag = image_data["tags"]
                    img_title = image_data["title"]
                    image_url = image_data["urls"][self.size]

                    chain = [
                        At(qq=event.get_sender_id()),  # At 消息发送者
                        Plain("主人，这是香草找到的涩图：\n"),  # 发送文字
                        # Plain(f"tag: {img_tag},\n"),
                        Plain(f"pid: {img_pid},\ntitle: {img_title}"),  # 使用换行
                        Image.fromURL(image_url),  # 发送图片
                    ]
                    yield event.chain_result(chain)

            except Exception as e:
                yield event.plain_result(f"\n获取图片失败：{e}")
