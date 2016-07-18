import discord
from discord.ext import commands
from bot import nonAsyncRun, printToDiscord, checkOp
import pickle

class CustomCommands():
    
    def __init__(self, client):
        self.client = client
        
        self.tempCommands = pickle.load(open("tempCommands.p","rb"))
    
    async def on_message(self, message):
        self.lastMessage = message
        
        for key in self.tempCommands:
            if message.content.startswith(key) and message.author != self.client.user:
                exec(self.tempCommands[key])
    
    @commands.command(pass_context = True)
    async def cc(self, ctx, commandName : str, *, commandCode : str):
        """Evaluates python [commandCode] when [command trigger] is called. """
        
        if await checkOp(ctx.message):
            self.tempCommands.update({commandName:commandCode})
            pickle.dump(self.tempCommands, open("tempCommands.p", "wb"))
            
            await self.client.say("Command '{}' defined!".format(commandName))

    @commands.command(pass_context = True)
    async def rcc(self, ctx, *, commandName : str):
        """Removes custom command [commandName]"""
        if await checkOp(ctx.message):
            del self.tempCommands[commandName]
            pickle.dump(self.tempCommands, open("tempCommands.p", "wb"))
            
            await self.client.say("Command '{}' deleted!".format(commandName))
            
    @commands.command()
    async def lcc(self, *, commandName : str = None):
        """Lists custom commands, or provide a command name and get more detail on it [commandName]"""
        
        if commandName == None:
            commandListText = "**Defined custom commands**:\n"
            for key in self.tempCommands:
                commandListText += key + "\n"
        else:
            try:
                commandListText = commandName + "'s code: `" + self.tempCommands[commandName] + "`"
            except:
                commandListText = commandName + " is not a currently defined command"
        
        await self.client.say(commandListText)
        
def setup(client):
    client.add_cog(CustomCommands(client))