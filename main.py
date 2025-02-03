from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import httpx
import random

# 注册插件的装饰器
@register("image_sender", "Image Sender", "一个发送图片的插件", "1.0.0")
class ImageSenderPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 注册指令的装饰器。指令名为 image。注册成功后，发送 `/image` 就会触发这个指令，并发送图片
    @filter.command("image")
    async def send_image(self, event: AstrMessageEvent):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.lolicon.app/setu/v2")
                response.raise_for_status()  # Raise an exception for bad status codes
                data = response.json()
                if data and data['data']:
                    image_url = data['data'][0]['urls']['original']
                    yield event.image_result(image_url)
                else:
                    yield event.plain_result("未能获取到图片")
        except httpx.HTTPError as e:
            yield event.plain_result(f"获取图片失败: {e}")
        except Exception as e:
            yield event.plain_result(f"发生错误: {e}")