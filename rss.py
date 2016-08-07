import discord
from discord.ext import commands
import pickle
import asyncio
import feedparser
from bot import nonAsyncRun
import datetime
from pytz import timezone
import re
import html
import threading
from bot import nonAsyncRun, getShelfSlot
import atexit

class RSS():
    
    def __init__(self, client):
        self.client = client
        self.loop = asyncio.get_event_loop()
        self.lastChecked = datetime.datetime.now(timezone('UTC')).astimezone(timezone('US/Pacific'))
        
        self.tempRSS = {}
        
        for server in self.client.servers:
            self.tempRSS[server.id] = getShelfSlot(server.id, "RSS")
        
        self.checkrss()
        atexit.register(self.do_sync)
    
    def do_sync(self):
        for server, data in self.tempRSS.items():
            data.close()
    
    def checkrss(self):
        threading.Timer(20.0, self.checkrss).start()
        
            
        for tempkey, tempval in self.tempRSS.items():
            for key, val in tempval.items():
                for post in feedparser.parse(key).entries:
                    if post not in val["posted"]:
                        self.loop.call_soon_threadsafe(asyncio.async, self.client.send_message(val["channel"],"**{}**, *{}*: {}\n".format(post.title,html.unescape(re.sub(re.compile('<.*?>'), '', post.description)), post.link)))
                        val["posted"].append(post)
    
    @commands.command(pass_context = True)
    async def addrss(self, ctx, *, url : str):
        """Adds an rss feed to this channel"""
        
        self.tempRSS[ctx.message.server.id][url] = {"channel":ctx.message.channel,"posted":[]}
        
        for post in feedparser.parse(url).entries:
            self.tempRSS[ctx.message.server.id][url]["posted"].append(post)
        
        await self.client.say("**{}** set as RSS for this channel!".format(url))
        
    @commands.command(pass_context = True)
    async def stoprss(self, ctx, url : str):
        """Stops all rss feeds in this channel"""
        
        del self.tempRSS[ctx.message.server.id][url]
        
        await self.client.say("RSS Stopped for this channel!")
        
    @commands.command(pass_context = True)
    async def listrss(self, ctx):
        """Lists all rss feeds in this channel"""
        await self.client.say("**--- RSS ---**")
        
        for key, val in self.tempRSS[ctx.message.server.id].items():
            if val["channel"] == ctx.message.channel:
                await self.client.say(key)
        
        
        
def setup(client):
    client.add_cog(RSS(client))