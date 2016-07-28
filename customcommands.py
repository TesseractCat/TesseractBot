import discord
from discord.ext import commands
from bot import nonAsyncRun, printToDiscord, checkOp, safeEval
import pickle

class CustomCommands():
    
    def __init__(self, client):
        self.client = client
        
        try:
            self.tempCommands = pickle.load(open("tempCommands.p","rb"))
        except:
            self.tempCommands = {}
    
    async def on_message(self, message):
        self.lastMessage = message
        
        for key in self.tempCommands:
            if message.content.startswith(key) and message.author != self.client.user:
                exec(self.tempCommands[key])
    
    @commands.command(pass_context = True)
    async def ccs(self, ctx, commandName : str, *, commandCode : str):
        """Simple version of custom command"""
        
        self.tempCommands.update({commandName:"printToDiscord(self.client,self.lastMessage.channel,safeEval('" + commandCode.replace("'","\\'") + "',{\"message\":self.lastMessage}))"})
        pickle.dump(self.tempCommands, open("tempCommands.p", "wb"))
        #,{'message':self.lastMessage}
        
        await self.client.say("Command '{}' defined!".format(commandName))
    
    @commands.command(pass_context = True)
    async def cc(self, ctx, commandName : str, *, commandCode : str):
        """Evaluates python [commandCode] when [command trigger] is called. """
        
        self.tempCommands.update({commandName:commandCode})
        pickle.dump(self.tempCommands, open("tempCommands.p", "wb"))
        
        await self.client.say("Command '{}' defined!".format(commandName))

    @commands.command(pass_context = True)
    async def rcc(self, ctx, *, commandName : str):
        """Removes custom command [commandName]"""
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