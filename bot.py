import discord
import asyncio
import wolframalpha
import math
import codecs
import brainfuck
import pickle
import sys
import youtube_dl
import random
import time
import subprocess
import os
import urbandict
import configparser
import xmltodict
import html
import urllib.request
import signal
from ctypes.util import find_library
from discord.ext import commands
from unidecode import unidecode
import re
import markovify
from translate import translate
import threading
import shelve
import atexit
import execjs
import js2py
import json
import multiprocessing
import builtins

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
    
    if id == None:
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

def getShelfSlot(serverID, name):
    try:
        os.makedirs(os.path.join("ServerData/" + serverID))
    except:
        pass
    return shelve.open(os.path.join("ServerData/" + serverID + "/", name), writeback=True)
        
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

#Wolfram Alpha Client
waClient = wolframalpha.Client(getToken("wolframalpha"))

#Load Discord Opus
discord.opus.load_opus(find_library("opus"))

#Cogs to load
cogs = ["voting","ranks","pastebin","customcommands","customanimations","botactions","musicactions","imageactions","cards","spreadsheets","rss","weather","useractions","serverpage"]

#Load settings
opCommands = ["sn", "sa", "skp", "setrank", "setrankbyname", "op", "deop", "rldext"]

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

@client.event
async def on_message(message):
    if message.author.bot == True:
        return

    try:
        print(message.author.name + "@" + message.server.name + "~" + message.channel.name + ": " + message.content)
    except:
        pass
    
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

@client.command(pass_context = True)
async def sac(ctx, channel : discord.Channel = None):
    """Set a channel to announce bans and unbans! Run this command with no channel to reset the channel"""
    
    announceChannel = getShelfSlot(ctx.message.server.id, "AnnounceChannel")
    
    announceChannel["channel"] = channel
    
    announceChannel.close()
    
    await client.say("The bot's announcement channel is now set to **{}**".format(channel.name))
    
@client.command(pass_context = True)
async def setprefix(ctx, *, prefix : str = "$"):
    slot = getShelfSlot(ctx.message.server.id, "Prefix")
    slot["Prefix"] = prefix
    prefixDict.update({ctx.message.server.id:slot["Prefix"]})
    slot.close()
    
    await client.say("Prefix set!")
    
async def bot(message):
    """Commune with the bot!"""
    mitsukuResponse = subprocess.run(["node","mitsuku.js",message.content.split(" ",1)[1]], stdout=subprocess.PIPE).stdout
    if message.server.me.nick != None:
        mitsukuResponse = re.compile(re.escape('mitsuku'), re.IGNORECASE).sub(message.server.me.nick,str(mitsukuResponse))
    else:
        mitsukuResponse = re.compile(re.escape('mitsuku'), re.IGNORECASE).sub(message.server.me.name,str(mitsukuResponse))
    await client.send_message(message.channel, "<@{0}".format(message.author.id) + "> " + str(mitsukuResponse)[2:][:-3])

@client.command(pass_context = True)
async def ev(ctx, *, code : str):
    """Evaluates a python statement"""
    #context = js2py.EvalJs({"message":ctx.message})
    await client.say(safeEval("return " + code, {"message": ctx.message, "list": getattr(builtins, "list")}))
    
#Eval Funcs
    
def safeEval(code, args = {}, pyimports = []):
    manager = multiprocessing.Manager()
    ret = manager.dict()

    p = multiprocessing.Process(target=doEval, name="doEval", args = (code, ret, args, pyimports))
    p.start()
    
    p.join(1)
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

    print("Evaluating: {}".format(codeToRun))
    
    context = js2py.EvalJs(args)
    context.execute(codeToRun)
    
    ret["result"] = str(context.cc())

#End of eval funcs
    
@client.command(pass_context = True)
async def rep(ctx, user : discord.User = None):
    repDict = getShelfSlot(ctx.message.server.id, "Rep")
    
    if (user == ctx.message.author):
        await client.say("You can't give yourself rep!")
        return
    
    if (user == None):
        try:
            await client.say("You have `{}` rep!".format(repDict[ctx.message.author.id]))
        except:
            await client.say("You have no rep!")
    else:
        try:
            repDict[user.id] += 1
        except:
            repDict[user.id] = 1
            
        await client.say("1 rep given to {}, they currently have `{}` rep.".format(user.mention, repDict[user.id]))
    
    repDict.close()
    
@client.command()
async def df(word : str, defNum : int = 1):
    """Defines a word"""
    
    await client.say(urbandict.define(word)[defNum-1]['def'])
        
@client.command()
async def bf(bfsrc : str, bfinput : str = ""):
    """Executes brainfuck code"""
    
    bftext = ""

    bftext += "**--- Brainfuck result ---**\n"
        
    bftext += "```" + brainfuck.bf(bfsrc, 0, len(bfsrc) - 1, bfinput, 0, 1000000)
    await client.say(bftext[:1500] + " ```")

@client.command(pass_context = True)
async def wa(ctx,*, search : str):
    """Gets Wolfram Alpha result for [search] put a 'true' at the beginning of your search to enable images."""
    
    watext = ""
    watext += "**--- Wolfram Alpha result for: " + search + " ---**\n"
    await client.send_typing(ctx.message.channel)
    
    if search.split(" ")[0].lower() == "true":
        waresult = waClient.query(search.split(" ",1)[1])
    else:
        waresult = waClient.query(search)
    
    for pod in waresult.pods:
        watext+="**"+pod.title+"**\n"
        if pod.text == None and search.split(" ")[0].lower() == "true":
            watext+=pod.img + "\n"
            await client.say(watext)
            watext = ""
        elif pod.text != None:
            #watext+=bytes(pod.text.replace("\\:","\\u"),'utf-8').decode("unicode_escape") + "\n"
            watext+=pod.text.replace("\\:","\\u") + "\n"
    if len(waresult.pods) < 1:
        watext += "*No results, please rephrase your query.*"
    await client.say(watext)

@client.group(pass_context = True)
async def quote(ctx):
    """Manage quotes, run this command with no subcommands to get a random quote"""
    quotes = getShelfSlot(ctx.message.server.id, "Quotes")
    if "quotes" not in quotes:
        quotes["quotes"] = []
    if ctx.invoked_subcommand == None:
        if len(ctx.message.content.split(" "))>1:
            quote = int(ctx.message.content.split(" ")[1])
        else:
            quote = None
    
        if quote == None:
            quoteRand = random.choice(quotes["quotes"])
            await client.say("**Quote #{}**\n{}".format(quotes["quotes"].index(quoteRand)+1,quoteRand))
            return
            
        try:
            await client.say(quotes["quotes"][quote-1])
        except:
            await client.say("That's not a quote!")
    quotes.close()
    
    
@quote.command(pass_context = True)
async def add(ctx, *, quote : str = None):
    """Add a quote"""
    quotes = getShelfSlot(ctx.message.server.id, "Quotes")
    quotes["quotes"].append("{} - **{}** in **{}** at **{}**".format(quote,ctx.message.author.name,ctx.message.channel.name,time.strftime("%d/%m/%Y")))
    await client.say("Quote added as #{}!".format(len(quotes["quotes"])))
    quotes.close()

@quote.command(pass_context = True)
async def delete(ctx, num : int):
    """Delete a quote"""
    quotes = getShelfSlot(ctx.message.server.id, "Quotes")
    quotes["quotes"][num-1] = "Deleted!"
    await client.say("Quote deleted!")
    quotes.close()
        
@client.command(pass_context = True)
async def mal(ctx, *, searchQuery : str):
    """Search myanimelist"""
    url = "http://myanimelist.net/api/anime/search.xml?q={}".format(searchQuery.replace(" ","%20"))
        
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, "discorddoggobot", "discordbotmal")
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    
    response = opener.open(url)
    response = response.read().decode("utf-8")
    doc = xmltodict.parse(response)
    result = doc["anime"]["entry"][0]
    
    await client.say("**--- Result for search: {} ---**\nTitle: **{}**\nEpisodes: **{}**\nScore: **{}**\nType: **{}**\nStatus: **{}**\n\nSynopsis: *{}*\n\nImage: {}".format(searchQuery, result["title"],result["episodes"],result["score"],result["type"],result["status"],html.unescape(re.sub(re.compile('<.*?>'), '', result["synopsis"])),result["image"]))
    
@client.command(pass_context = True)
async def mkv(ctx, channel : discord.Channel, messages : int = 500, stateSize : int = 1):
    """Make a markov chain of a channel"""
    text = ""
    async for message in client.logs_from(channel, limit=messages):
        text += message.content.replace("<@","@") + "\n"
    text_model = markovify.Text(text, state_size=stateSize)
    await client.say(text_model.make_sentence(max_overlap_ratio = 0.9,max_overlap_total=30,tries=1000))
    
@client.command(pass_context = True)
async def trans(ctx, *, text : str):
    """Translate text to english (this function is very finnicky)"""
    if len(ctx.message.content.rsplit(" ",1)[1]) == 2:
        await client.say(translate(ctx.message.content.rsplit(" ",1)[0].split(" ",1)[1],ctx.message.content.rsplit(" ",1)[1]))
    else:
        await client.say(translate(text,"en"))

@client.command(pass_context = True)
async def remind(ctx, time : int, unit : str, *, text : str):
    thread = threading.Thread(target=doRemind,args=(ctx, time, unit.lower(), text, asyncio.get_event_loop()))
    thread.start()

def doRemind(ctx, timeToSleep, unit, text, loop):
    if "second" in unit:
        sleepTime = (timeToSleep)
    elif "minute" in unit:
        sleepTime = (timeToSleep*60)
    elif "hour" in unit:
        sleepTime = (timeToSleep*60*60)
    elif "day" in unit:
        sleepTime = (timeToSleep*60*60*24)
    else:
       loop.call_soon_threadsafe(asyncio.async, client.send_message(ctx.message.channel,"That is not a valid time unit, the available units are: seconds, minutes, hours, days"))
       return
    
    loop.call_soon_threadsafe(asyncio.async, client.send_message(ctx.message.channel,"Ok! I will remind you in `{}` {}".format(timeToSleep, unit)))
    
    time.sleep(sleepTime)
    
    loop.call_soon_threadsafe(asyncio.async, client.send_message(ctx.message.author, "Hello! `{}` {} ago you asked me to remind you of:\n\n{}".format(timeToSleep, unit, text)))

def get_input():
    while True:
        try:
            user_input = input("> ")
        except KeyboardInterrupt:
            pass
    
if __name__ == "__main__":
    print("Booting up...")
    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    
    try:
        client.run(getToken("discord"))
    except:
        sys.exit()
    
