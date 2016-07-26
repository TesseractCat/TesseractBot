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

class RSS():
    
    def __init__(self, client):
        self.client = client
        
        self.lastChecked = datetime.datetime.now(timezone('UTC')).astimezone(timezone('US/Pacific'))
        
        try:
            self.tempRSS = pickle.load(open("tempRSS.p","rb"))
        except:
            self.tempRSS = {}
        
        if "posted" not in self.tempRSS:
            self.tempRSS["posted"] = []
        
        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(asyncio.async, self.checkrss())
    
    async def checkrss(self):
        while True:
            #test = feedparser.parse("http://lorem-rss.herokuapp.com/feed?unit=second&interval=1")
            try:
                for key, val in self.tempRSS.items():
                    for post in feedparser.parse(key).entries:
                        if post.updated_parsed > self.lastChecked.timetuple() and post not in self.tempRSS["posted"]:
                            await self.client.send_message(val,"**{}**, *{}*: {}\n".format(post.title,html.unescape(re.sub(re.compile('<.*?>'), '', post.description)), post.link))
                            self.tempRSS["posted"].append(post)
                            pickle.dump(self.tempRSS,open("tempRSS.p","wb"))
                self.lastChecked = datetime.datetime.now(timezone('UTC')).astimezone(timezone('US/Pacific'))
            except Exception as e:
                print(str(e))
            await asyncio.sleep(5)
    
    @commands.command(pass_context = True)
    async def addrss(self, ctx, *, url : str):
        """Adds an rss feed to this channel"""
        
        self.tempRSS[url] = ctx.message.channel
        
        pickle.dump(self.tempRSS,open("tempRSS.p","wb"))
        
        await self.client.say("**{}** set as RSS for this channel!".format(url))
        
    @commands.command(pass_context = True)
    async def stoprss(self, ctx):
        """Stops all rss feeds in this channel"""
        
        tempTempRSS = self.tempRSS.copy()
        for key, val in self.tempRSS.items():
            if val == ctx.message.channel:
                del tempTempRSS[key]
        self.tempRSS = tempTempRSS
                
        pickle.dump(self.tempRSS,open("tempRSS.p","wb"))
        
        await self.client.say("All RSS Stopped for this channel!")
        
def setup(client):
    client.add_cog(RSS(client))