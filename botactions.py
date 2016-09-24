import discord
from discord.ext import commands
import urllib.request
from bot import checkOp, nonAsyncRun, getShelfSlot, getPrefix
import bot

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
    
    
    @commands.command(aliases = ["sp"])
    async def setplaying(self, *, game : str):
       """Change what the bot is playing"""
       
       gameObj = discord.Game()
       gameObj.name = game
       
       await self.client.change_status(game=gameObj,idle=False)
       
       await self.client.say("The bot is now playing " + game)
    
    @commands.command(pass_context = True, aliases = ["cl"])
    async def clear(self, ctx, count : int = 500, deleteUserMessages : bool = False):
        """Clears messages since last boot"""
        prefix = getPrefix(self.client, ctx.message)
        
        async for message in self.client.logs_from(ctx.message.channel, limit=count):
            if message.author == self.client.user:
                await self.client.delete_message(message)
            if deleteUserMessages and message.content.startswith(prefix):
                await self.client.delete_message(message)
    
    @commands.command(pass_context = True, aliases = ["sa"])
    async def setavatar(self, ctx, *, url : str):
        """Change the bots avatar"""
        
        request = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        file = open("avatar.jpg","wb")
        file.write(response.read())
        
        await self.client.edit_profile(avatar = open('avatar.jpg','rb').read())
        
        await self.client.say("Avatar set!")
        
    @commands.command(pass_context = True, aliases = ["sn"])
    async def setnick(self, ctx, *, name : str):
        """Change the bots nickname"""
        await self.client.change_nickname(ctx.message.server.me, name)
        
        await self.client.say("Nickname set to: " + name)
       
    @commands.command(aliases = ["inv"])
    async def invite(self):
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
    
    @commands.command(aliases = ["rldext"])
    async def reloadextension(self, *, ext : str = None):
        """Reload bot extension"""
        
        if (ext == None):
            await self.client.say("Please choose an extension, currently available to be reloaded are:\n```" + "\n".join(bot.cogs) + "```")
            return
        
        await self.client.say("Reloading extension!")
        
        try:
            self.client.unload_extension(ext)
        except:
            pass
        self.client.load_extension(ext)
        
        await self.client.say("Done!")
        
    @commands.command(aliases = ["dsblext"])
    async def disableextension(self, *, ext : str = None):
        """Reload bot extension"""
        
        if (ext == None):
            await self.client.say("Please choose an extension, currently available to be disabled are:\n```" + "\n".join(bot.cogs) + "```")
            return
        
        await self.client.say("Disabling extension!")
        
        try:
            self.client.unload_extension(ext)
        except:
            pass
        
        await self.client.say("Done!")
        
def setup(client):
    client.add_cog(BotActions(client))
