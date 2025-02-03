from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import httpx
import json

# 注册插件的装饰器
@register("setu", "Setu Plugin", "一个发送随机涩图的插件", "1.0.0")
class SetuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 注册指令的装饰器。指令名为 setu。注册成功后，发送 `/setu` 就会触发这个指令
    @filter.command("setu")
    async def setu(self, event: AstrMessageEvent):
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
                        Image.fromURL(image_url),
                    ]
                    yield event.chain_result(chain)
                else:
                    yield event.plain_result("没有找到涩图。")
        except httpx.HTTPError as e:
            yield event.plain_result(f"获取涩图时发生错误: {e}")
        except json.JSONDecodeError as e:
            yield event.plain_result(f"解析JSON时发生错误: {e}")