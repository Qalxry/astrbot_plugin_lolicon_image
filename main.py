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
                parts = event.message.content.split()
                if len(parts) == 3 and parts[0] == "/image":
                    tag = parts[1]
                    num = parts[2]
                    if tag == "cat":
                        response = await client.get("https://api.thecatapi.com/v1/images/search")
                        response.raise_for_status()
                        data = response.json()
                        if data:
                             image_url = data[0]['url']
                             yield event.image_result(image_url)
                        else:
                             yield event.plain_result("未能获取到猫图片")
                    else:
                        response = await client.get(f"https://api.lolicon.app/setu/v2?tag={tag}")
                        response.raise_for_status()
                        data = response.json()
                        if data and data['data'] and len(data['data']) >= int(num):
                            image_url = data['data'][int(num)-1]['urls']['original']
                            yield event.image_result(image_url)
                        else:
                            yield event.plain_result(f"未能获取到{tag}图片")
                else:
                    yield event.plain_result("命令格式错误，请使用/image <tag> <num>")
        except httpx.HTTPError as e:
            yield event.plain_result(f"获取图片失败: {e}")
        except Exception as e:
            yield event.plain_result(f"发生错误: {e}")