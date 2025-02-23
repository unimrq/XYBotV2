import asyncio
import logging
import tomllib  # 确保导入tomllib以读取配置文件
import aiohttp
from aiohttp import web
from utils.plugin_base import PluginBase

from WechatAPI import WechatAPIClient


class ExposeApiServer():
    def __init__(self, bot: WechatAPIClient):
        super().__init__()
        # 从外部传入配置参数
        self.app = web.Application()
        self.bot = bot
        self.to_wxid = "wxid_surnho6dn28822"

        # 在这里注册路由和处理函数
        self.app.router.add_post('/send_text_server', self.send_text_server)
        self.app.router.add_post('/send_image_server', self.send_image_server)

    async def send_text_server(self, request):
        try:
            data = await request.json()
        except Exception as e:
            return web.json_response({"error": "Invalid JSON data"}, status=400)

        if not data:
            return web.json_response({"error": "No data provided"}, status=400)

        text = data.get("text")
        to_wxid = data.get("to_wxid")
        if text is None:
            return web.json_response({"error": "没有文本信息用于发送"}, status=400)

        await self.bot.send_text_message(to_wxid, text)

        return web.json_response({"status": "200", "data": "文本信息发送成功"})

    async def send_image_server(self, request):
        try:
            data = await request.json()
        except Exception as e:
            return web.json_response({"error": "Invalid JSON data"}, status=400)

        if not data:
            return web.json_response({"error": "No data provided"}, status=400)

        image_path = data.get("image_path")
        to_wxid = data.get("to_wxid")
        if image_path is None:
            return web.json_response({"error": "没有图片信息用于发送"}, status=400)

        try:
            conn_ssl = aiohttp.TCPConnector(ssl=False)

            async with aiohttp.request("GET", url=image_path, connector=conn_ssl) as req:
                content = await req.read()

            await conn_ssl.close()

            pic = self.bot.byte_to_base64(content)
            await self.bot.send_image_message(to_wxid, image_base64=pic)
            return web.json_response({"status": "200", "data": "图片信息发送成功"})
        except Exception as error:
            out_message = f"-----XYBot-----\n图片解析错误❌！\n{error}"

            await self.bot.send_text_message(self.to_wxid, out_message)
            return web.json_response({"status": "500", "data": "图片信息发送失败"})

    def run(self):
        # 获取当前的事件循环
        loop = asyncio.get_event_loop()
        # 手动运行 app，而不是使用 web.run_app()
        loop.create_task(web._run_app(self.app, host='0.0.0.0', port=5000, print=None))
