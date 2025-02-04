from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import httpx
import json
import asyncio

# 注册插件的装饰器
@register("setu", "rikka", "一个发送随机涩图的插件", "1.0.3")
class SetuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.cd = 10  # 默认冷却时间为 10 秒
        self.last_usage = {} # 存储每个用户上次使用指令的时间

    # 注册指令的装饰器。指令名为 setu。注册成功后，发送 `/setu` 就会触发这个指令
    @filter.command("setu")
    async def setu(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        now = asyncio.get_event_loop().time()

        if user_id in self.last_usage and (now - self.last_usage[user_id]) < self.cd:
            remaining_time = self.cd - (now - self.last_usage[user_id])
            yield event.plain_result(f"冷却中，请等待 {remaining_time:.1f} 秒后重试。")
            return

        try:
             async with httpx.AsyncClient() as client:
                resp = await client.get("https://api.lolicon.app/setu/v2?r18=0")
                resp.raise_for_status()
                data = resp.json()
                if data['data']:
                    image_url = data['data'][0]['urls']['original']
                    chain = [
                        At(qq=event.get_sender_id()),
                        Plain("给你一张涩图："),
                        Image.fromURL(image_url, size='small'),
                    ]
                    yield event.chain_result(chain)
                    self.last_usage[user_id] = now
                else:
                    yield event.plain_result("没有找到涩图。")
        except httpx.HTTPError as e:
            yield event.plain_result(f"获取涩图时发生错误: {e}")
        except json.JSONDecodeError as e:
            yield event.plain_result(f"解析JSON时发生错误: {e}")

    @filter.command("setucd")
    async def set_setu_cd(self, event: AstrMessageEvent, cd: int):
        if cd <= 0:
            yield event.plain_result("冷却时间必须大于 0。")
            return
        self.cd = cd
        yield event.plain_result(f"涩图指令冷却时间已设置为 {cd} 秒。")

    @filter.command("setu_help")
    async def setu_help(self, event: AstrMessageEvent):
        help_text = """
        **涩图插件帮助**

        **可用命令:**
        - `/setu`: 发送一张随机涩图。
        - `/setucd <冷却时间>`: 设置涩图指令的冷却时间（秒）。
        - `/setu_help`: 显示此帮助信息。

        **使用方法:**
        - 直接发送 `/setu` 即可获取一张随机涩图。
        - 使用 `/setucd 15` 将冷却时间设置为 15 秒。

        **注意:**
        - 涩图图片大小为 small。
        - 冷却时间默认为 10 秒。
        """
        yield event.plain_result(help_text)
