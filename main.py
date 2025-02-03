from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import httpx
import asyncio

@register("random_image", "随机图片发送器", "一个发送随机图片的插件", "1.0.0")
class RandomImagePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.last_image_data = None
        self.r18_enabled = False  # 默认关闭 R18

    async def _get_image(self, event: AstrMessageEvent, size: str, r18=None, num=1, tags=None):
        if r18 is None:
            r18 = 1 if self.r18_enabled else 0 # 根据开关设置r18参数
        
        async with httpx.AsyncClient() as client:
            try:
                image_results = []
                for _ in range(num):
                     params = {"r18": r18, "size": size}
                     if tags:
                         params["tag"] = tags
                     response = await client.get("https://api.lolicon.app/setu/v2", params=params)
                     response.raise_for_status()
                     data = response.json()
                     if data and data['data']:
                        image_data = data['data'][0]
                        image_url = image_data['urls'].get(size)
                        if not image_url:
                            image_url = image_data['urls']['original'] # 如果指定尺寸没有，使用原图
                        tags_list = image_data.get('tags', [])
                        uid = image_data.get('uid', 'N/A')
                        aspect_ratio = image_data.get('aspectRatio', 'N/A')
                    
                        tag_string = ", ".join(tags_list) if tags_list else "N/A"
                    
                        message = f"图片链接: {image_url}\n" \
                                  f"标签: {tag_string}\n" \
                                  f"用户ID: {uid}\n" \
                                  f"宽高比: {aspect_ratio}"

                        self.last_image_data = {"url": image_url, "message": message} # 存储图片信息
                        image_results.append(event.image_result(image_url, message))
                     else:
                        image_results.append(event.plain_result("没有找到图片。"))
                for result in image_results:
                    yield result


            except httpx.HTTPError as e:
                yield event.plain_result(f"获取图片时发生错误: {e}")

    async def _resend_image(self, event: AstrMessageEvent, size: str):
        if not self.last_image_data:
             yield event.plain_result("没有找到之前发送的图片。")
             return
        
        image_url = self.last_image_data['url']
        message = self.last_image_data['message']
        
        if size == 'original':
           if 'original' in image_url:
             yield event.image_result(image_url,message)
           else:
              async with httpx.AsyncClient() as client:
                try:
                  response = await client.get("https://api.lolicon.app/setu/v2",params={"r18": 1 if self.r18_enabled else 0})
                  response.raise_for_status()
                  data = response.json()
                  if data and data['data']:
                        image_data = data['data'][0]
                        image_url = image_data['urls']['original']
                        tags_list = image_data.get('tags', [])
                        uid = image_data.get('uid', 'N/A')
                        aspect_ratio = image_data.get('aspectRatio', 'N/A')
                    
                        tag_string = ", ".join(tags_list) if tags_list else "N/A"
                    
                        message = f"图片链接: {image_url}\n" \
                                  f"标签: {tag_string}\n" \
                                  f"用户ID: {uid}\n" \
                                  f"宽高比: {aspect_ratio}"
                        yield event.image_result(image_url,message)
                except httpx.HTTPError as e:
                    yield event.plain_result(f"获取图片时发生错误: {e}")
        else:
          async with httpx.AsyncClient() as client:
            try:
                  response = await client.get("https://api.lolicon.app/setu/v2",params={"r18": 1 if self.r18_enabled else 0})
                  response.raise_for_status()
                  data = response.json()
                  if data and data['data']:
                        image_data = data['data'][0]
                        image_url = image_data['urls'].get(size)
                        if not image_url:
                            image_url = image_data['urls']['original'] # 如果指定尺寸没有，使用原图
                        tags_list = image_data.get('tags', [])
                        uid = image_data.get('uid', 'N/A')
                        aspect_ratio = image_data.get('aspectRatio', 'N/A')
                    
                        tag_string = ", ".join(tags_list) if tags_list else "N/A"
                    
                        message = f"图片链接: {image_url}\n" \
                                  f"标签: {tag_string}\n" \
                                  f"用户ID: {uid}\n" \
                                  f"宽高比: {aspect_ratio}"
                        yield event.image_result(image_url,message)

            except httpx.HTTPError as e:
                    yield event.plain_result(f"获取图片时发生错误: {e}")
    
    @filter.command("r18")
    async def toggle_r18(self, event: AstrMessageEvent):
        self.r18_enabled = not self.r18_enabled
        yield event.plain_result(f"R18 模式已 {'启用' if self.r18_enabled else '禁用'}。")

    @filter.command("image")
    async def random_image(self, event: AstrMessageEvent):
        args = event.__dict__.get('raw_message',"").split(" ")[1:]  # 获取命令后的所有参数
        tags = None
        num = 1
        if len(args) >= 2:
            tags = [args[0]]
            try:
                num = int(args[1])
            except ValueError:
                yield event.plain_result("数量参数无效，请输入一个整数。")
                return
        elif len(args) == 1:
            tags = [args[0]]

        await self._get_image(event, 'regular', num=num, tags=tags)

    @filter.command("original")
    async def original_image(self, event: AstrMessageEvent):
        await self._resend_image(event, 'original')

    @filter.command("small")
    async def small_image(self, event: AstrMessageEvent):
        await self._resend_image(event, 'small')

    @filter.command("thumb")
    async def thumb_image(self, event: AstrMessageEvent):
         await self._resend_image(event, 'thumb')
    
    @filter.command("mini")
    async def mini_image(self, event: AstrMessageEvent):
        await self._resend_image(event, 'thumb')
    
    @filter.command("regular")
    async def regular_image(self, event: AstrMessageEvent):
        await self._resend_image(event, 'regular')