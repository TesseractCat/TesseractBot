import discord
from discord.ext import commands
from bot import nonAsyncRun, printToDiscord, checkOp, safeEval, getShelfSlot
import pickle
import threading
import atexit
import js2py
import jsonpickle

class CustomCommands():
    
    def __init__(self, client):
        self.client = client
        self.tempCommands = {}
        
        
        for server in self.client.servers:
            self.tempCommands[server.id] = getShelfSlot(server.id, "CustomCommands")
            
        atexit.register(self.do_sync)
        
    def do_sync(self):
        for server, data in self.tempCommands.items():
            data.close()
    
    async def on_message(self, message):
        for key in self.tempCommands[message.server.id]:
            if message.content.startswith(key) and message.author != self.client.user:
                #context = js2py.EvalJs({"message":message})
                #context.execute("function cc() {" + self.tempCommands[message.server.id][key].replace("pyimport","") + "}")
                #await self.client.send_message(message.channel, context.cc())
                await self.client.send_message(message.channel, safeEval(self.tempCommands[message.server.id][key], {"message": message}))
                #context = execjs.compile("message = '{}'".format(message.content.replace("'","\\'")))
                #await self.client.send_message(message.channel, context.exec_(self.tempCommands[message.server.id][key]))
    
    
    @commands.command(pass_context = True)
    async def ccs(self, ctx, commandName : str, *, commandCode : str):
        """Simple version of custom command"""
        print(commandCode)
        
        self.tempCommands[ctx.message.server.id].update({commandName:'return {}'.format(commandCode.replace("'","\\'"))})
        #,{'message':self.lastMessage}
        
        await self.client.say("Command '{}' defined!".format(commandName))
    
    @commands.command(pass_context = True)
    async def cc(self, ctx, commandName : str, *, commandCode : str):
        """Evaluates javascript [commandCode] when [command trigger] is called. Return a value to be sent as a message"""
        
        self.tempCommands[ctx.message.server.id].update({commandName:commandCode})
        
        await self.client.say("Command '{}' defined!".format(commandName))

    @commands.command(pass_context = True)
    async def rcc(self, ctx, *, commandName : str):
        """Removes custom command [commandName]"""
        
        del self.tempCommands[ctx.message.server.id][commandName]
        
        await self.client.say("Command '{}' deleted!".format(commandName))
            
    @commands.command(pass_context = True)
    async def lcc(self, ctx, *, commandName : str = None):
        """Lists custom commands, or provide a command name and get more detail on it [commandName]"""
        
        if commandName == None:
            commandListText = "**Defined custom commands**:\n"
            for key in self.tempCommands[ctx.message.server.id]:
                commandListText += key + "\n"
        else:
            try:
                commandListText = commandName + "'s code: ```" + self.tempCommands[ctx.message.server.id][commandName] + "```"
            except:
                commandListText = commandName + " is not a currently defined command"
        
        await self.client.say(commandListText)
        
def setup(client):
    client.add_cog(CustomCommands(client))