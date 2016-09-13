import discord
from discord.ext import commands

class Voting():
    
    def __init__(self, client):
        self.client = client
        
        self.polls = {}
    
    @commands.command()
    async def createpoll(self, name, *options : str):
        self.polls[name] = {}
        self.polls[name]["voted"] = []
        
        for option in options:
            self.polls[name][option] = 0
            
        await self.client.say("Poll created!")
            
    @commands.command()
    async def cancelpoll(self, *, name):
        del self.polls[name]
        await self.client.say("Poll canceled!")
    
    @commands.command(pass_context = True)
    async def vote(self, ctx, name, *, option):
        if ctx.message.author.id not in self.polls[name]["voted"]:
            self.polls[name][option] += 1
            self.polls[name]["voted"].append(ctx.message.author.id)
            await self.client.say("You have voted for {}, there now **{}** votes.".format(option,self.polls[name][option]))
        else:
            await self.client.say("You have already voted, if you want to stop a poll, do $cancelpoll.")
    
    @commands.command()
    async def poll(self, *, name):
        pollText = "**--- Results for poll: " + name + " ---**"
        for option, votes in self.polls[name].items():
            if option != "voted":
                pollText += "\n**{}**: **{}** votes".format(option, votes)
        
        await self.client.say(pollText)
        
def setup(client):
    client.add_cog(Voting(client))