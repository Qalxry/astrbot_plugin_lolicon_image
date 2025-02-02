from astrbot.api.all import *

@register("一个1-100的随机数", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
@command("Number")  # 修改命令触发词为"Number"
async def number_command(self, event: AstrMessageEvent):  # 建议重命名函数
    random_number = random.randint(1, 100)  # 生成随机数
    yield event.plain_result(f"你的随机数是：{random_number}")  # 返回结果