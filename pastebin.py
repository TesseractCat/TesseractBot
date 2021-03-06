import discord
from discord.ext import commands
from urllib.request import urlopen
import json, requests, sys
from urllib.parse import urlencode

class Pastebin():
    
    def __init__(self, client):
        self.client = client
        self.pastebin_vars = {'api_dev_key':'c84d0208a681cb7777e23dd610917f4e','api_user_key':'3420da161a360d7042e81dfe31cfb753','api_option':'paste'}
    
    @commands.command(pass_context = True, aliases = ["cpfl"])
    async def createpastefromlogs(self, ctx, messages : int = 50):
        """Create paste from log files"""
        text = ""
        async for message in self.client.logs_from(ctx.message.channel, limit=messages):
            text += message.author.name + " (" + '{:%Y-%m-%d %H:%M}'.format(message.timestamp) + "): " + message.clean_content + "\n"
    
        self.pastebin_vars.update({'api_paste_code':text})
        response = urlopen('http://pastebin.com/api/api_post.php', urlencode(self.pastebin_vars).encode('utf-8'))
        url = response.read().decode('utf-8')
        await self.client.say("<" + url + ">")
        
    @commands.command(aliases = ["cpft"])
    async def createpastefromtext(self, *, text : str):
        """Create paste from text"""
        
        self.pastebin_vars.update({'api_paste_code':text})
        response = urlopen('http://pastebin.com/api/api_post.php', urlencode(self.pastebin_vars).encode('utf-8'))
        url = response.read().decode('utf-8')
        await self.client.say("<" + url + ">")
        
    @commands.command(pass_context = True, aliases = ["chfl"])
    async def createhastefromlogs(self, ctx, messages : int = 50):
        """Create paste from log files"""
        text = ""
        async for message in self.client.logs_from(ctx.message.channel, limit=messages):
            text += message.author.name + " (" + '{:%Y-%m-%d %H:%M}'.format(message.timestamp) + "): " + message.clean_content + "\n"
        
        data = text
        response = requests.post("http://hastebin.com/documents", data.encode('utf-8'))
        await self.client.say("<" + "http://hastebin.com/" + json.loads(response.text)['key'] + ".hs" + ">")
        
    @commands.command(aliases = ["chft"])
    async def createhastefromtext(self, *, text : str):
        """Create paste from text"""
        
        data = text
        response = requests.post("http://hastebin.com/documents", data.encode('utf-8'))
        await self.client.say("<" + "http://hastebin.com/" + json.loads(response.text)['key'] + ">")
        
def setup(client):
    client.add_cog(Pastebin(client))