import discord
from discord.ext import commands
import os
import sys
import urllib.request
import pickle
from bot import nonAsyncRun, checkOp

class BotActions():
    
    def __init__(self, client):
        self.client = client
        
        lastMessage = pickle.load(open("lastMessage.p","rb"))
        
        if lastMessage != None:
            nonAsyncRun(self.client.send_message,(lastMessage.channel, "Done!"))
            pickle.dump(None, open("lastMessage.p","wb"))
    
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
    
    @commands.command()
    async def sa(self, *, url : str):
        """Change the bots avatar"""
        
        if await checkOp(ctx.message):
            request = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request)
            file = open("avatar.jpg","wb")
            file.write(response.read())
            
            await self.client.edit_profile(avatar = open('avatar.jpg','rb').read())
            
            await self.client.say("Avatar set!")
        
    @commands.command(pass_context = True)
    async def sn(self, ctx, *, name : str):
        """Change the bots nickname"""
        if await checkOp(ctx.message):
            await self.client.change_nickname(ctx.message.server.me, name)
            
            await self.client.say("Nickname set to: " + name)
       
    @commands.command()
    async def inv(self):
       """Add the best bot on discord to your own server!"""
       
       await self.client.say("Here you go, I know you're going to be amazed: " + "https://discordapp.com/oauth2/authorize?client_id=168158801231347713&scope=bot&permissions=0")  

    @commands.command(pass_context = True)
    async def rs(self,ctx):
        """Restarts the bot"""
        if await checkOp(ctx.message):
            lastMessage = await self.client.say("Restarting...")
        
            pickle.dump(lastMessage, open("lastMessage.p","wb"))
        
            os.execl(sys.executable, sys.executable, *sys.argv)
        
def setup(client):
    client.add_cog(BotActions(client))