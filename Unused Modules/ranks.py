import discord
from discord.ext import commands
import math
from bot import checkOp
from bot import getShelfSlot
import threading
import atexit

class Ranks():
    
    def __init__(self, client):
        self.client = client
        
        self.tempMessageList = []
        
        self.ranks = {}
        
        for server in self.client.servers:
            self.ranks[server.id] = getShelfSlot(server.id, "Ranks")
            
        self.do_sync()
    
    def do_sync(self):
        threading.Timer(60.0, self.do_sync).start()
        
        for server, data in self.ranks.items():
            data.close()
        
        for server in self.client.servers:
            self.ranks[server.id] = getShelfSlot(server.id, "Ranks")
    
    async def on_message(self, message):
        await self.parseMessage(message)
    
    async def parseMessage(self, message):
    
        self.tempMessageList.extend(message.content.split(" "))
        self.tempMessageList = self.tempMessageList[-200:]
        
        if message.author == self.client.user:
            return
        
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
            self.ranks[message.server.id][message.author.name] += max(min(xpToAdd, 10), 0)
        except:
            self.ranks[message.server.id][message.author.name] = 0
            
        try:
            for rank, level in self.ranks[message.server.id]["rolesAtRankDict"].items():
                if self.ranks[message.server.id][message.author.name] > level:
                    await self.client.add_roles(message.author, discord.utils.get(message.server.roles, name=rank))
        except:
            pass

    @commands.command(pass_context = True, aliases = ["grar"])
    async def giveroleatrank(self, ctx, roleName : str, level : int):
        if "rolesAtRankDict" not in self.ranks[ctx.message.server.id]:
            self.ranks[ctx.message.server.id]["rolesAtRankDict"] = {}
    
        self.ranks[ctx.message.server.id]["rolesAtRankDict"].update({roleName: level})
        
        await self.client.say("That role will be given once people recieve that rank!")
            
    @commands.command(pass_context = True, aliases = ["rnk"])
    async def rank(self, ctx, member : discord.Member = None):
        """Get rank of poster or other user"""
        
        if member == None:
            await self.client.say("{}, you are level `{}` with `{}` xp. Overall you are rank `{}`".format(ctx.message.author.mention, math.floor(self.ranks[ctx.message.server.id][ctx.message.author.name]/300), self.ranks[ctx.message.server.id][ctx.message.author.name], [y[0] for y in reversed(sorted(self.ranks[ctx.message.server.id].items(), key=lambda x:x[1]))].index(ctx.message.author.name)+1))
        else:
            try:
                await self.client.say("{} is level `{}` with `{}` xp. Overall they are rank `{}`".format(member.mention, math.floor(self.ranks[ctx.message.server.id][member.name]/300), self.ranks[ctx.message.server.id][member.name], [y[0] for y in reversed(sorted(self.ranks[ctx.message.server.id].items(), key=lambda x:x[1]))].index(member.name)+1))
            except:
                await self.client.say("{} is level 0 with 0 xp".format(member.mention))
    
    @commands.command(pass_context = True, aliases = ["strnk"])
    async def setrank(self, ctx, member : discord.Member, rank : int):
        self.ranks[ctx.message.server.id][member.name] = rank
        
    @commands.command(pass_context = True, aliases = ["strnkbn"])
    async def setrankbyname(self, ctx, member : str, rank : int):
        self.ranks[ctx.message.server.id][member] = rank
    
    @commands.command(pass_context = True, aliases = ["lvls"])
    async def levels(self, ctx):
        """Get levels"""
        
        lvlText = "**--- Levels ---**\n\n"
        
        topNum = 0
        
        for user, rank in reversed(sorted(self.ranks[ctx.message.server.id].items(), key=lambda x:x[1])):
            topNum += 1
            if topNum > 45:
                break
            lvlText += str([y[0] for y in reversed(sorted(self.ranks[ctx.message.server.id].items(), key=lambda x:x[1]))].index(user)+1) + ". " + str(user) + ": `" + str(rank).replace("`","").replace("*","").replace("_","") + "` xp | `" + str(math.floor(rank/300)) + "` lvl(s)\n\n"
        
        def chunks(s, n):
            """Produce n-character chunks from s."""
            for start in range(0, len(s), n):
                yield s[start:start+n]
        
        for chunk in chunks(lvlText, 1999):
            await self.client.send_message(ctx.message.author, chunk)
            
        
def setup(client):
    client.add_cog(Ranks(client))
