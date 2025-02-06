import json
import time
import tomllib

import aiohttp
from loguru import logger

from WechatAPI import WechatAPIClient
from utils.decorators import *
from utils.plugin_base import PluginBase


class MessageForward(PluginBase):
    description = "message forward"
    author = "unimrq"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        with open("plugins/all_in_one_config.toml", "rb") as f:
            plugin_config = tomllib.load(f)

        config = plugin_config["MessageForward"]

        self.enable = config["enable"]
        self.base_url = config["base_url"]
        self.command = config["command"]

    @on_text_message
    async def handle_text(self, bot: WechatAPIClient, message: dict):
        if not self.enable:
            return

        content = str(message["Content"]).strip()
        command = content.split(" ")

        if not len(command) or command[0] not in self.command:
            return

        url = self.base_url + "send_text_client"

        # 要发送的数据
        data = {
            "content": content,
            "from_wxid": message["SenderWxid"],
            "MsgId": message["MsgId"],
            "ToWxid": message["ToWxid"],
            "timestamp": time.time()
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                logger.info("发送文本信息到客户端: {}".format(result))

    @on_image_message
    async def handle_image(self, bot: WechatAPIClient, message: dict):
        if not self.enable:
            return

        if message["IsGroup"]:
            return

        url = self.base_url + "send_image_client"
        content = str(message["Content"])
        # 要发送的数据
        data = {
            "content": content,
            "from_wxid": message["SenderWxid"],
            "MsgId": message["MsgId"],
            "ToWxid": message["ToWxid"],
            "timestamp": time.time()
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                logger.info("发送图片信息到客户端: {}".format(result))
