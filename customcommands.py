import discord
from discord.ext import commands
from bot import checkOp
from bot import getShelfSlot
from bot import nonAsyncRun
from bot import printToDiscord
from bot import safeEval
import atexit
import js2py
import jsonpickle
import asyncio
import threading

class CustomCommands():
    
    def __init__(self, client):
        self.client = client
        self.tempCommands = {}
        self.tempEvents = {}
        self.loop = asyncio.get_event_loop()
        
        self.update_cc_arr()
        self.update_ce_arr()
        
    def update_cc_arr(self):
        for server in self.client.servers:
            self.tempCommands[server.id] = getShelfSlot(server.id, "CustomCommands")
            
    def update_ce_arr(self):
        for server in self.client.servers:
            self.tempEvents[server.id] = getShelfSlot(server.id, "CustomEvents")
    
    async def on_server_join(server):
        self.update_cc_arr()
        self.update_ce_arr()
    
    async def on_message_edit(self, prev, message):
        await self.procNewMessageEvent(message)
    
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        
        t = threading.Thread(target=self.runPNME, args=(message,))
        t.start()
        
        for key in self.tempCommands[message.server.id]:
            if message.content.split(" ")[0] == key and message.author != self.client.user:
                await self.client.send_message(message.channel, safeEval(self.tempCommands[message.server.id][key], {"client": {"servers":self.client.servers, "user":self.client.user}, "message": message}, ["urllib"], 1))
    
    def runPNME(self, message):
        self.loop.call_soon_threadsafe(asyncio.async, self.procNewMessageEvent(message))
    
    async def procNewMessageEvent(self, message):
        if message.author == self.client.user:
            return
    
        if "onmessage" in self.tempEvents[message.server.id]:
            #"post": (lambda x: self.loop.call_soon_threadsafe(asyncio.async, self.client.send_message(message.channel, x))),
            messageResult = safeEval(self.tempEvents[message.server.id]["onmessage"], {"client": {"servers":self.client.servers, "user":self.client.user}, "message": message}, [], 1)
            
            #print("RESULT OF EVENT: " + str(actionArr))
            
            if messageResult == None:
                return
            
            if messageResult.lower() == "delete":
                print("Deleting message, triggered by event.")
                await self.client.delete_message(message)
            elif messageResult.split(" ")[0].lower() == "post":
                await self.client.send_message(message.channel, messageResult.split(" ",1)[1])
            elif messageResult.split(" ")[0].lower() == "pm":
                await self.client.send_message(message.author, messageResult.split(" ",1)[1])
    
    @commands.command(pass_context = True)
    async def setevent(self, ctx, event : str, *, eventCode : str):
        """Set event (onmessage, onjoin) and evaluate eventCode. Have eventcode return 'delete' to delete the message."""
        
        slot = self.tempEvents[ctx.message.server.id]
        
        slot.update({event.lower():eventCode})
        
        await self.client.say("On event code created!")
        
    @commands.command(pass_context = True)
    async def getevent(self, ctx, event : str):
        """Set event (onmessage, onjoin) and evaluate eventCode. Have eventcode return 'delete' to delete the message."""
        
        slot = self.tempEvents[ctx.message.server.id]
        
        try:
            await self.client.say("Event code:\n```javascript\n{}```".format(slot[event.lower()]))
        except:
            await self.client.say("Event code has not been defined!")
    
    @commands.command(pass_context = True, aliases = ["ccs"])
    async def customcommandsimple(self, ctx, commandName : str, *, commandCode : str):
        """Simple version of custom command"""
        print(commandCode)
        
        slot = self.tempCommands[ctx.message.server.id]
        
        slot.update({commandName:'return {}'.format(commandCode.replace("'","\\'"))})
        
        await self.client.say("Command '{}' defined!".format(commandName))
    
    @commands.command(pass_context = True, aliases = ["cc"])
    async def customcommand(self, ctx, commandName : str, *, commandCode : str):
        """Evaluates javascript [commandCode] when [command trigger] is called. Return a value to be sent as a message"""
        
        slot = self.tempCommands[ctx.message.server.id]
        
        slot.update({commandName:commandCode})
        
        await self.client.say("Command '{}' defined!".format(commandName))

    @commands.command(pass_context = True, aliases = ["rcc"])
    async def removecustomcommand(self, ctx, *, commandName : str):
        """Removes custom command [commandName]"""
        
        slot = self.tempCommands[ctx.message.server.id]
        
        del slot[commandName]
        
        await self.client.say("Command '{}' deleted!".format(commandName))
            
    @commands.command(pass_context = True, aliases = ["lcc"])
    async def listcustomcommands(self, ctx, *, commandName : str = None):
        """Lists custom commands, or provide a command name and get more detail on it [commandName]"""
        
        slot = self.tempCommands[ctx.message.server.id]
        
        if commandName == None:
            commandListText = "**Defined custom commands**:\n"
            for key in slot:
                commandListText += key + "\n"
        else:
            try:
                commandListText = commandName + "'s code: ```" + slot[commandName] + "```"
            except:
                commandListText = commandName + " is not a currently defined command"
        
        await self.client.say(commandListText)
        
def setup(client):
    client.add_cog(CustomCommands(client))