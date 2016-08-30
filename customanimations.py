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
    
    @commands.command(pass_context = True)
    async def ca(self, ctx, animName : str, *frames : str):
        """Custom animation, put each frame in quotes"""
        
        slot = getShelfSlot(ctx.message.server.id, "CustomAnimations")
        
        slot.update({animName: frames})
        
        slot.close()
        
        await self.client.say("Animation **{}** created!".format(animName))


    @commands.command(pass_context = True)
    async def pa(self, ctx, delay : int, animName : str):
        """Play custom animation, it will loop 10 times"""
        
        slot = getShelfSlot(ctx.message.server.id, "CustomAnimations")
        
        await self.client.say( "**--- Playing: " + animName + " ---**")
        animpost = await self.client.say( "*Loading...*")
        for i in range(0,10):
            for frame in slot[animName]:
                await asyncio.sleep(delay)
                await self.client.edit_message(animpost, "```\n" + frame + "```")
        slot.close()
        
def setup(client):
    client.add_cog(CustomAnimations(client))