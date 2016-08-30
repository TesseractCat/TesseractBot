import discord
from discord.ext import commands
import os
import sys
import urllib.request
import pickle
from bot import nonAsyncRun, checkOp, getShelfSlot

class BotActions():
    
    def __init__(self, client):
        self.client = client
    
    #@commands.command(pass_context = True)
    #async def setprefix(self, ctx, prefix : str = "$"):
    #    """Changes the command prefix default '$'"""
    #    
    #    saveServerData(ctx.message.server.id, "prefix", prefix)
    #    
    #   await self.client.say("Prefix set to **{}**!".format(prefix))
    #    
    #@commands.command(pass_context = True)
    #async def getprefix(self, ctx):
    #    """Changes the command prefix default '$'"""
    #    
    #    await self.client.say("Prefix set to **{}**!".format(loadServerData(ctx.message.server.id, "prefix", "$")))
    
    
    @commands.command()
    async def sp(self, *, game : str):
       """Change what the bot is playing"""
       
       gameObj = discord.Game()
       gameObj.name = game
       
       await self.client.change_status(game=gameObj,idle=False)
       
       await self.client.say("The bot is now playing " + game)
    
    @commands.command(pass_context = True)
    async def cl(self, ctx, count : int = 500):
        """Clears messages since last boot"""
        async for message in self.client.logs_from(ctx.message.channel, limit=count):
            if message.author == self.client.user:
                await self.client.delete_message(message)
    
    @commands.command(pass_context = True)
    async def sa(self, ctx, *, url : str):
        """Change the bots avatar"""
        
        request = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        file = open("avatar.jpg","wb")
        file.write(response.read())
        
        await self.client.edit_profile(avatar = open('avatar.jpg','rb').read())
        
        await self.client.say("Avatar set!")
        
    @commands.command(pass_context = True)
    async def sn(self, ctx, *, name : str):
        """Change the bots nickname"""
        await self.client.change_nickname(ctx.message.server.me, name)
        
        await self.client.say("Nickname set to: " + name)
       
    @commands.command()
    async def inv(self):
       """Add the best bot on discord to your own server!"""
       
       await self.client.say("Here you go, I know you're going to be amazed: " + "https://discordapp.com/oauth2/authorize?client_id=168158801231347713&scope=bot&permissions=0")  
    
    #@commands.command()
    #async def stp(self):
    #    await self.client.say("Stopping!")
    #    self.client.close()
        
    
    #@commands.command(pass_context = True)
    #async def rs(self,ctx):
    #    """Restarts the bot"""
    #    
    #    await self.client.say("Restarting...")
        
def setup(client):
    client.add_cog(BotActions(client))
