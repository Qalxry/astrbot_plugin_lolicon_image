from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import httpx
import random

@register("image_sender", "Image Sender", "一个发送图片的插件", "1.0.0")
class ImageSenderPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @filter.command("image")
    async def send_image(self, event: AstrMessageEvent):
        args = event.text.split()
        if len(args) < 2:
            yield event.plain_result("使用方法: /image <tag> <num>")
            return
        
        tag = args[1]
        num = 1
        if len(args) > 2:
            try:
                num = int(args[2])
                if num <= 0 or num > 10:
                   yield event.plain_result("数量必须是1到10之间的整数")
                   return
            except ValueError:
                yield event.plain_result("数量必须是整数")
                return
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "tag": tag,
                    "num": num
                }
                response = await client.get("https://api.lolicon.app/setu/v2", params=params)
                response.raise_for_status()
                data = response.json()
                if data and data['data']:
                    for item in data['data']:
                        image_url = item['urls']['original']
                        yield event.image_result(image_url)
                else:
                    yield event.plain_result("未能获取到图片")
        except httpx.HTTPError as e:
            yield event.plain_result(f"获取图片失败: {e}")
        except Exception as e:
            yield event.plain_result(f"发生错误: {e}")