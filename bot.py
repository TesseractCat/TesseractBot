import discord
import asyncio
import wolframalpha
import brainfuck
import youtube_dl
import subprocess
import os
import urbandict
import xmltodict
import urllib.request
from ctypes.util import find_library
from discord.ext import commands
from unidecode import unidecode
import re
import markovify
from translate import translate
import threading
from shelve import DbfilenameShelf
import atexit
import execjs
import js2py
import json
import multiprocessing
import builtins
import pickle
import shelve

def nonAsyncRun(function, args):
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(asyncio.async, function(*args))

def printToDiscord(clientObj, channel, text):
    nonAsyncRun(clientObj.send_message,(channel,text))
    
async def checkOp(message):
    operators = getShelfSlot(message.server.id, "Operators")
    userPerms = message.author.permissions_in(message.channel)
    
    if "ids" not in operators:
        operators["ids"] = []
        
    if message.author.id in operators["ids"] or userPerms.administrator == True or userPerms.manage_server == True or message.author.id == "129757604506370048":
        return True
    else:
        await client.send_message(message.channel,"You are not a bot operator, so you cannot use this command.")
        return False
    operators.close()
    
def getToken(service, id = None):
    #Make a JSON file containing your tokens, like:
    #{
    #"discord":"[TOKEN]",
    #"wolframalpha":"[TOKEN]",
    #"googleimages":"[TOKEN]"
    #}

    tokenFile = open('botconfig', 'r')
    tokenJSON = json.loads(tokenFile.read())
    
    if id == None or service == "discord":
        return tokenJSON[service]
    else:
        slot = getShelfSlot(id, "Tokens")
        
        try:
            tokenReturn = slot[service]
            slot.close()
            return slot[service]
        except:
            slot.close()
            return tokenJSON[service]

class AutoSyncShelf(DbfilenameShelf):
    def __init__(self, filename, protocol=2, writeback=True):
        DbfilenameShelf.__init__(self, filename, protocol=protocol, writeback=writeback)
    def __setitem__(self, key, value):
        DbfilenameShelf.__setitem__(self, key, value)
        self.sync()
    def __delitem__(self, key):
        DbfilenameShelf.__delitem__(self, key)
        self.sync()

class CustomDict(dict):
    def __init__(self, name, newData = None):
        self._name = name
        self._dict = {}
        
        if newData != None:
            self._dict = newData
            self.sync()
            return
        
        try:
            with open(self._name + ".dat",'rb') as f:
                self._dict = pickle.load(f)
        except:
            pass
    
    def close(self):
        return
    
    def sync(self):
        with open(self._name + ".dat",'wb') as f:
            pickle.dump(self._dict, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def __setitem__(self, key, item): 
        self._dict[key] = item
        self.sync()

    def __getitem__(self, key): 
        return self._dict[key]

    def __repr__(self): 
        return repr(self._dict)

    def __len__(self): 
        return len(self._dict)

    def __delitem__(self, key): 
        del self._dict[key]
        self.sync()

    def clear(self):
        return self._dict.clear()

    def copy(self):
        return self._dict.copy()

    def has_key(self, k):
        return self._dict.has_key(k)

    def pop(self, k, d=None):
        self._dict.pop(k, d)
        self.sync()
        return self._dict

    def update(self, *args, **kwargs):
        self._dict.update(*args, **kwargs)
        self.sync()
        return self._dict

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def pop(self, *args):
        self._dict.pop(*args)
        self.sync()
        return self._dict

    def __cmp__(self, dict):
        return cmp(self._dict, dict)

    def __contains__(self, item):
        return item in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __unicode__(self):
        return unicode(repr(self._dict))
            
def getShelfSlot(serverID, name):
    try:
        os.makedirs(os.path.join("ServerData/" + serverID))
    except:
        pass
    #return shelve.open(os.path.join("ServerData/" + serverID + "/", name), writeback=True)
    #return AutoSyncShelf(os.path.join("ServerData/" + serverID + "/", name))
    
    #with shelve.open(os.path.join("ServerData/" + serverID + "/", name), writeback=True) as newData:
    #    dataToApply = {}
    #    for key, value in newData.items():
    #        dataToApply[key] = value
    #    newDict = CustomDict(os.path.join("ServerData/" + serverID + "/", name), dataToApply)
    #    return newDict
    return CustomDict(os.path.join("ServerData/" + serverID + "/", name))
        
def getPrefix(bot, message):
    try:
        if message.server.id not in prefixDict:
            slot = getShelfSlot(message.server.id, "Prefix")
            prefixDict.update({message.server.id:slot["Prefix"]})
            slot.close()
        return prefixDict[message.server.id]
    except:
        return "$"

#Discord Client
client = commands.Bot(command_prefix=getPrefix, description='Tesseract Multipurpose Bot', pm_help = True)
loop = asyncio.get_event_loop()

#Load Discord Opus
discord.opus.load_opus(find_library("opus"))

#Cogs to load
cogs = ["utilities", "stalk","voting","pastebin","customcommands","customanimations","botactions","musicactions","imageactions","cards","rss","weather","useractions"]#, "ranks"]

#Load settings
opCommands = ["sn", "sa", "skp", "setrank", "setrankbyname", "op", "deop", "rldext", "gr", "giveroleatrank", "setevent"]

#Prefix dict
prefixDict = {}
 
@client.event
async def on_ready():
    print('Logged in!')
    print(client.user.name)
    print(client.user.id)
    print('---')
    
    print('\nLoading extensions: ')
    
    for cog in cogs:
        print(cog)
        client.load_extension(cog)
    
    print('\n\nChanging username...')
    await client.edit_profile(username="Doggo Bot")
    print('\nDone!')
    
@client.event
async def on_message(message):
    if message.author.bot == True:
        return

    try:
        print(message.author.name + "@" + message.server.name + "~" + message.channel.name + ": " + message.content)
    except:
        pass
    
    if bool(re.search("^\\{}[a-zA-Z0-9]+\\b".format(client.command_prefix(client, message)),message.content)):
        print("Sending typing...")
        await client.send_typing(message.channel)
    
    for command in opCommands:
        if message.content.startswith(client.command_prefix(client, message) + command + " "):
            if await checkOp(message) == False:
                return
        
    
    if client.user.id in message.content:
        await bot(message)
    
    await client.process_commands(message)

#@client.event
#async def on_error(event,*args,**kwargs):
#    print("ERROR " + str(event) + " WITH ARGS: " + args)
#    await client.send_message(args[0].channel,"Error in: " + str(event))
    
@client.event
async def on_channel_update(oldChannel, channel):
    if oldChannel.topic != channel.topic:
        await client.send_message(channel, "**{}**'s channel topic changed from **{}** to **{}**".format(channel.name,oldChannel.topic, channel.topic))
    if oldChannel.name != channel.name:
        await client.send_message(channel, "**{}**'s channel name changed to **{}**".format(oldChannel.name,channel.name))

@client.event
async def on_member_ban(member):
    announceChannel = getShelfSlot(member.server.id, "AnnounceChannel")
    await client.send_message(announceChannel["channel"],"User **{}** has been banned!".format(member.name))
    announceChannel.close()

@client.event
async def on_member_unban(server, member):
    announceChannel = getShelfSlot(server.id, "AnnounceChannel")
    await client.send_message(announceChannel["channel"],"User **{}** has been unbanned!".format(member.name))     
    announceChannel.close()

@client.command(pass_context = True, aliases = ["sac"])
async def setannouncementchannel(ctx, channel : discord.Channel = None):
    """Set a channel to announce bans and unbans! Run this command with no channel to reset the channel"""
    
    announceChannel = getShelfSlot(ctx.message.server.id, "AnnounceChannel")
    
    announceChannel["channel"] = channel
    
    announceChannel.close()
    
    await client.say("The bot's announcement channel is now set to **{}**".format(channel.name))

@client.command(pass_context = True, aliases = ["stfs"])
async def settokenforservice(ctx, service : str = None, *, token : str = None):
    """Set a token for apis, run without any parameters for a list"""
    
    if service == None and token == None:
        await client.say("**--- API Keys/Tokens to set ---**\nDiscord\nWolframAlpha\nImgurId and ImgurSecret\nYoutubeSearch\nGoogleImageSearch")
        return

    slot = getShelfSlot(id, "Tokens")
    slot[service.lower()] = token
    slot.close()

@client.command(pass_context = True, aliases = ["spr"])
async def setprefix(ctx, *, prefix : str = "$"):
    slot = getShelfSlot(ctx.message.server.id, "Prefix")
    slot["Prefix"] = prefix
    prefixDict.update({ctx.message.server.id:slot["Prefix"]})
    slot.close()
    
    await client.say("Prefix set!")
    
async def bot(message):
    """Commune with the bot!"""
    
    await client.send_typing(message.channel)
    
    mitsukuResponse = subprocess.run(["node","mitsuku.js",message.content.split(" ",1)[1]], stdout=subprocess.PIPE).stdout
    if message.server.me.nick != None:
        mitsukuResponse = re.compile(re.escape('mitsuku'), re.IGNORECASE).sub(message.server.me.nick,str(mitsukuResponse))
    else:
        mitsukuResponse = re.compile(re.escape('mitsuku'), re.IGNORECASE).sub(message.server.me.name,str(mitsukuResponse))
    await client.send_message(message.channel, "<@{0}".format(message.author.id) + "> " + str(mitsukuResponse)[2:][:-3])
    
#Eval Funcs
    
def safeEval(code, args = {}, pyimports = [], acceptableWaitTime = 1):
    manager = multiprocessing.Manager()
    ret = manager.dict()

    #print("Evaluation code with wait time: {}".format(acceptableWaitTime))
    
    p = multiprocessing.Process(target=doEval, name="doEval", args = (code, ret, args, pyimports))
    p.start()
    
    p.join(acceptableWaitTime)
    if p.is_alive():
        p.terminate()
        p.join()
    
    return ret["result"]
    
def doEval(code, ret, args = {}, pyimports = []):
    if pyimports != []:
        pyimportcode = "pyimport " + ";\npyimport ".join(pyimports) + ";\n"
    else:
        pyimportcode = "";
    
    codeToRun = pyimportcode + "function cc() {" + code.replace("pyimport","").replace("__class__","") + "}"

    #print("Evaluating: {}".format(codeToRun))
    
    context = js2py.EvalJs(args)
    context.execute(codeToRun)
    
    ret["result"] = str(context.cc())

def doUrlopen(url):
    return str(urllib.request.urlopen(urllib.request.Request(str(url)[1:-1],data=None,headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})).read())
    
#End of eval funcs

def run_discord():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start(getToken("discord")))
    loop.close()
    
if __name__ == "__main__":
    print("Booting up...")
    #loop = asyncio.get_event_loop()
    #thread = threading.Thread(target=run_discord)
    #thread.start()
    
    client.run(getToken("discord"))
    
    #while True:
    #    user_input = input("> ")
    
