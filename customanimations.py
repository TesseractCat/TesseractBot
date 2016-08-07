import discord
from discord.ext import commands
import pickle
import asyncio
from urllib.request import urlopen
from bot import getShelfSlot
import atexit

class CustomAnimations():
    
    def __init__(self, client):
        self.client = client
        self.tempAnimations = {}
        
        for server in self.client.servers:
            self.tempAnimations[server.id] = getShelfSlot(server.id, "CustomAnimations")
            
        atexit.register(self.do_sync)
        
    def do_sync(self):
        for server, data in self.tempAnimations.items():
            data.close()
    
    @commands.command(pass_context = True)
    async def ca(self, ctx, animName : str, *frames : str):
        """Custom animation, put each frame in quotes"""
        
        self.tempAnimations[ctx.message.server.id].update({animName: frames})
        
        await self.client.say("Animation **{}** created!".format(animName))


    @commands.command(pass_context = True)
    async def pa(self, ctx, delay : int, animName : str):
        """Play custom animation, it will loop 10 times"""
        
        await self.client.say( "**--- Playing: " + animName + " ---**")
        animpost = await self.client.say( "*Loading...*")
        for i in range(0,10):
            for frame in self.tempAnimations[ctx.message.server.id][animName]:
                await asyncio.sleep(delay)
                await self.client.edit_message(animpost, "```\n" + frame + "```")
        
def setup(client):
    client.add_cog(CustomAnimations(client))