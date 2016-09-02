import discord
from discord.ext import commands
from bot import nonAsyncRun, printToDiscord, checkOp, safeEval, getShelfSlot
import pickle
import threading
import atexit
import js2py
import jsonpickle
from urllib.request import urlopen

class CustomCommands():
    
    def __init__(self, client):
        self.client = client
        self.tempCommands = {}
        
        self.update_cc_arr()
        
    def update_cc_arr(self):
        for server in self.client.servers:
            self.tempCommands[server.id] = getShelfSlot(server.id, "CustomCommands")
    
    async def on_message(self, message):
        for key in self.tempCommands[message.server.id]:
            if message.content.split(" ")[0] == key and message.author != self.client.user:
                await self.client.send_message(message.channel, safeEval(self.tempCommands[message.server.id][key], {"message": message}, ["urllib"]))
    
    
    @commands.command(pass_context = True)
    async def ccs(self, ctx, commandName : str, *, commandCode : str):
        """Simple version of custom command"""
        print(commandCode)
        
        slot = getShelfSlot(ctx.message.server.id, "CustomCommands")
        
        slot.update({commandName:'return {}'.format(commandCode.replace("'","\\'"))})
        
        slot.close()
        
        await self.client.say("Command '{}' defined!".format(commandName))
        
        self.update_cc_arr()
    
    @commands.command(pass_context = True)
    async def cc(self, ctx, commandName : str, *, commandCode : str):
        """Evaluates javascript [commandCode] when [command trigger] is called. Return a value to be sent as a message"""
        
        slot = getShelfSlot(ctx.message.server.id, "CustomCommands")
        
        slot.update({commandName:commandCode})
        
        slot.close()
        
        await self.client.say("Command '{}' defined!".format(commandName))
        
        self.update_cc_arr()

    @commands.command(pass_context = True)
    async def rcc(self, ctx, *, commandName : str):
        """Removes custom command [commandName]"""
        
        slot = getShelfSlot(ctx.message.server.id, "CustomCommands")
        
        del slot[commandName]
        
        slot.close()
        
        await self.client.say("Command '{}' deleted!".format(commandName))
        
        self.update_cc_arr()
            
    @commands.command(pass_context = True)
    async def lcc(self, ctx, *, commandName : str = None):
        """Lists custom commands, or provide a command name and get more detail on it [commandName]"""
        
        slot = getShelfSlot(ctx.message.server.id, "CustomCommands")
        
        if commandName == None:
            commandListText = "**Defined custom commands**:\n"
            for key in slot:
                commandListText += key + "\n"
        else:
            try:
                commandListText = commandName + "'s code: ```" + slot[commandName] + "```"
            except:
                commandListText = commandName + " is not a currently defined command"
        
        slot.close()
        
        await self.client.say(commandListText)
        
def setup(client):
    client.add_cog(CustomCommands(client))