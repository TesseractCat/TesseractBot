import discord
from discord.ext import commands
import pickle
import asyncio

class CustomAnimations():
    
    def __init__(self, client):
        self.client = client
        
        try:
            self.tempAnimations = pickle.load(open("tempAnimations.p","rb"))
        except:
            self.tempAnimations = {}
    
    @commands.command()
    async def ca(self, animName : str, *frames : str):
        """Custom animation, put each frame in quotes"""
        
        self.tempAnimations.update({animName: frames})
        
        pickle.dump(self.tempAnimations, open("tempAnimations.p", "wb"))
        
        await self.client.say("Animation **{}** created!".format(animName))


    @commands.command()
    async def pa(self, delay : int, animName : str):
        """Play custom animation, it will loop 10 times"""

        await self.client.say( "**--- Playing: " + animName + " ---**")
        animpost = await self.client.say( "*Loading...*")
        for i in range(0,10):
            for frame in self.tempAnimations[animName]:
                await asyncio.sleep(delay)
                await self.client.edit_message(animpost, "```\n" + frame + "```")
        
def setup(client):
    client.add_cog(CustomAnimations(client))