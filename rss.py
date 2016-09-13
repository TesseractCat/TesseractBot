import discord
from discord.ext import commands
import asyncio
import feedparser
from bot import nonAsyncRun
import datetime
from pytz import timezone
import re
import html
import threading
from bot import getShelfSlot
from bot import nonAsyncRun
import atexit

class RSS():
    
    def __init__(self, client):
        self.client = client
        self.loop = asyncio.get_event_loop()
        self.lastChecked = datetime.datetime.now(timezone('UTC')).astimezone(timezone('US/Pacific'))
        
        self.checkrss()
    
    def checkrss(self):
        threading.Timer(15.0, self.checkrss).start()
        
        #print("Updating RSS!")
        
        for server in self.client.servers:
            
            try:
                tempRSS = getShelfSlot(server.id, "RSS")
                
                for key, val in tempRSS.items():
                    for post in feedparser.parse(key).entries:
                        if post not in val["posted"]:
                            print("New RSS feed post: " + post.title)
                            self.loop.call_soon_threadsafe(asyncio.async, self.client.send_message(val["channel"],"**{}**, *{}*: {}\n".format(post.title,html.unescape(re.sub(re.compile('<.*?>'), '', post.description)), post.link)))
                            val["posted"].append(post)
                tempRSS.close()
                
                #print(server.id)
            except Exception as e:
                print("RSS Had a problem, " + str(type(e)))
    
    @commands.command(pass_context = True)
    async def addrss(self, ctx, *, url : str):
        """Adds an rss feed to this channel"""
        
        slot = getShelfSlot(ctx.message.server.id, "RSS")
        
        slot[url] = {"channel":ctx.message.channel,"posted":[]}
        
        for post in feedparser.parse(url).entries:
            slot[url]["posted"].append(post)
        
        await self.client.say("**{}** set as RSS for this channel!".format(url))
        
        slot.close()
        
    @commands.command(pass_context = True)
    async def stoprss(self, ctx, url : str):
        """Stops all rss feeds in this channel"""
        
        slot = getShelfSlot(ctx.message.server.id, "RSS")
        
        del slot[url]
        
        slot.close()
        
        await self.client.say("RSS Stopped for this channel!")
        
    @commands.command(pass_context = True)
    async def listrss(self, ctx):
        """Lists all rss feeds in this channel"""
        slot = getShelfSlot(ctx.message.server.id, "RSS")
        
        tempText = ""
        
        for key, val in slot.items():
            if val["channel"] == ctx.message.channel:
                tempText += key + "\n"
                
        await self.client.say("**--- RSS ---**\n" + tempText)
                
        slot.close()
        
        
        
def setup(client):
    client.add_cog(RSS(client))
