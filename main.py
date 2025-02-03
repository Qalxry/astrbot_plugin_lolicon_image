from astrbot.api.message_components import *
import aiohttp
import json

@command("setu")
async def send_setu(self, event: AstrMessageEvent):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.lolicon.app/setu/v2?size=regular") as response:
            if response.status == 200:
                data = await response.text()
                try:
                    json_data = json.loads(data)
                    image_url = json_data['data'][0]['urls']['regular']
                    chain = [
                        At(qq=event.get_sender_id()),
                        Plain("给你一张涩图："),
                        Image.fromURL(image_url),
                    ]
                    yield event.chain_result(chain)
                except (json.JSONDecodeError, KeyError) as e:
                    chain = [
                        At(qq=event.get_sender_id()),
                        Plain("获取图片失败了，请稍后再试。"),
                    ]
                    yield event.chain_result(chain)
            else:
                chain = [
                    At(qq=event.get_sender_id()),
                    Plain("获取图片失败了，请稍后再试。"),
                ]
                yield event.chain_result(chain)