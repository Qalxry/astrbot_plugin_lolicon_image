from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import random
import httpx

@register("random_image", "随机图片发送器", "一个发送随机图片的插件", "1.0.0")
class RandomImagePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("image")
    async def random_image(self, event: AstrMessageEvent):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://api.lolicon.app/setu/v2")
                response.raise_for_status()
                data = response.json()
                if data and data['data']:
                    image_url = data['data'][0]['urls']['original']
                    yield event.image_result(image_url)
                else:
                    yield event.plain_result("没有找到图片。")
            except httpx.HTTPError as e:
                yield event.plain_result(f"获取图片时发生错误: {e}")