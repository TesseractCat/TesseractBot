import discord
from discord.ext import commands
import pickle
import asyncio
import math
from bot import checkOp
import threading

class Ranks():
    
    def __init__(self, client):
        self.client = client
        
        self.tempMessageList = []
        
        try:
            self.ranks = pickle.load(open("ranks.p","rb"))
        except:
            self.ranks = {}
            
        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(asyncio.async, self.saveRanks())
    
    async def saveRanks(self):
        while True:
            pickle.dump(self.ranks,open("ranks.p","rb+"))
            await asyncio.sleep(300)
     
    async def on_message(self, message):
        self.parseMessage(message)
    
    def parseMessage(self, message):
        self.tempMessageList.extend(message.content.split(" "))
        self.tempMessageList = self.tempMessageList[-200:]
        
        if len(message.content) > 500:
            return
    
        try:
            xpToAdd = 0
            for word in message.content.split(" "):
                if word in self.tempMessageList:
                    if self.tempMessageList.count(word) > 4:
                        xpToAdd += 0
                    else:
                        xpToAdd += 1
                else:
                    xpToAdd += 2
            self.ranks[message.author] += max(min(xpToAdd, 10), 0)
        except:
            self.ranks[message.author] = 0
        
        try:
            del self.ranks[self.client.user]
        except:
            pass
            
        #pickle.dump(self.ranks,open("ranks.p","rb+"))

    @commands.command(pass_context = True)
    async def rank(self, ctx, member : discord.Member = None):
        """Get rank of poster or other user"""
        
        if member == None:
            await self.client.say("{}, you are level `{}` with `{}` xp. Overall you are rank `{}`".format(ctx.message.author.mention, math.floor(self.ranks[ctx.message.author]/300), self.ranks[ctx.message.author], [y[0] for y in reversed(sorted(self.ranks.items(), key=lambda x:x[1]))].index(ctx.message.author)+1))
        else:
            try:
                await self.client.say("{} is level `{}` with `{}` xp. Overall they are rank `{}`".format(member.mention, math.floor(self.ranks[member]/300), self.ranks[member], [y[0] for y in reversed(sorted(self.ranks.items(), key=lambda x:x[1]))].index(member)+1))
            except:
                await self.client.say("{} is level 0 with 0 xp".format(member.mention))
    
    @commands.command(pass_context = True)
    async def setrank(self, ctx, member : discord.Member, rank : int):
        if await checkOp(ctx.message):
            self.ranks[member] = rank
    
    @commands.command(pass_context = True)
    async def levels(self, ctx):
        """Get levels"""
        
        lvlText = "**--- Levels ---**\n\n"
        
        for user, rank in reversed(sorted(self.ranks.items(), key=lambda x:x[1])):
            lvlText += str([y[0] for y in reversed(sorted(self.ranks.items(), key=lambda x:x[1]))].index(user)+1) + ". " + str(user) + ": `" + str(rank) + "` xp | `" + str(math.floor(rank/300)) + "` lvl(s)\n\n"
        
        def chunks(s, n):
            """Produce n-character chunks from s."""
            for start in range(0, len(s), n):
                yield s[start:start+n]
        
        for chunk in chunks(lvlText, 1999):
            await self.client.send_message(ctx.message.author, chunk)
            
        
def setup(client):
    client.add_cog(Ranks(client))
