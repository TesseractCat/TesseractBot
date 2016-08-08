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

#Wolfram Alpha Client
waClient = wolframalpha.Client("2J69RV-TGJ5RGLKPA")

#Load Discord Opus
discord.opus.load_opus(find_library("opus"))

#Cogs to load
cogs = ["serverpage","voting","ranks","pastebin","customcommands","customanimations","botactions","musicactions","imageactions","cards","spreadsheets","rss","weather"]

#Load settings
config = configparser.ConfigParser()
config.read('botconfig.ini')
operators = config['Settings']['Operators'].replace(' ','').split(',')
opCommands = config['Settings']['OpCommands'].replace(' ','').split(',')
banned = config['Settings']['Banned'].replace(' ','').split(',')
token = config['Settings']['Token'].replace(' ','')

#Load announcement settings
try:
    announceChannel = pickle.load(open("announceChannel.p","rb"))
except:
    announceChannel = {}
    
#Load quotes
try:
    quotes = pickle.load(open("quotes.p","rb"))
except:
    quotes = []

def nonAsyncRun(function, args):
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(asyncio.async, function(*args))

def printToDiscord(clientObj, channel, text):
    nonAsyncRun(clientObj.send_message,(channel,text))
    
async def checkOp(message):
    if message.author.id in operators:
        return True
    else:
        await client.send_message(message.channel,"You are not a bot operator, so you cannot use this command.")
        return False

def getShelfSlot(serverID, name):
    try:
        os.makedirs(os.path.join("ServerData/" + serverID))
    except:
        pass
    return shelve.open(os.path.join("ServerData/" + serverID + "/", name), writeback=True)
        
def getPrefix(bot, message):
    try:
        return loadServerData(message.server.id, "prefix", "$")
    except:
        return "$"

#Discord Client
client = commands.Bot(command_prefix=getPrefix, description='Tesseract Multipurpose Bot', pm_help = True)
        
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
    if message.author.bot == True or message.author.id in banned:
        return

    try:
        print(message.author.name + "@" + message.server.name + "~" + message.channel.name + ": " + message.content)
    except:
        pass
    
    for command in opCommands:
        if (client.command_prefix(client, message) + command) in message.content:
            if await checkOp(message) == False:
                return
    
    if client.user.id in message.content:
        await bot(message)
    
    await client.process_commands(message)

#@client.event
#async def on_error(event,*args,**kwargs):
    #await client.send_message(args[0].channel,"Error in: " + str(event))
    
@client.event
async def on_channel_update(oldChannel, channel):
    if oldChannel.topic != channel.topic:
        await client.send_message(channel, "**{}**'s channel topic changed from **{}** to **{}**".format(channel.name,oldChannel.topic, channel.topic))
    if oldChannel.name != channel.name:
        await client.send_message(channel, "**{}**'s channel name changed to **{}**".format(oldChannel.name,channel.name))

@client.event
async def on_member_ban(member):
    await client.send_message(announceChannel[member.server.id],"User **{}** has been banned!".format(member.name))

@client.event
async def on_member_unban(server, member):
    await client.send_message(announceChannel[server.id],"User **{}** has been unbanned!".format(member.name))        

@client.command(pass_context = True)
async def sac(ctx, channel : discord.Channel = None):
    """Set a channel to announce bans and unbans! Run this command with no channel to reset the channel"""

    announceChannel[ctx.message.server.id] = channel
    
    pickle.dump(announceChannel, open("announceChannel.p","wb"))
    
    await client.say("The bot's announcement channel is now set to **{}**".format(channel.name))
    
async def bot(message):
    """Commune with the bot!"""
    
    data = urllib.request.urlopen("http://pastebin.com/raw/ARqAhaTU")
    cm = data.read().decode('utf-8').split("\n")
    random_index = random.randrange(0,len(cm)-1)
    text = cm[random_index].replace("  "," ")
    if len(message.content.split(" ")) > 1 and message.content.split(" ")[1].startswith("<@"):
        await client.send_message(message.channel, message.content.split(" ")[1] + text)
    elif len(message.content.split(" ")) > 1 and not message.content.split(" ")[1].startswith("<@"):
        #await client.send_message(message.channel, "<@{0}".format(message.author.id) + "> " + cbClient.ask(message.content.split(" ",1)[1]))
        mitsukuResponse = subprocess.run(["node","mitsuku.js",message.content.split(" ",1)[1]], stdout=subprocess.PIPE).stdout
        mitsukuResponse = re.compile(re.escape('mitsuku'), re.IGNORECASE).sub("Tess Bot",str(mitsukuResponse))
        await client.send_message(message.channel, "<@{0}".format(message.author.id) + "> " + str(mitsukuResponse)[2:][:-3])
    else:
        await client.send_message(message.channel, "<@{0}".format(message.author.id) + ">" + text)

@client.command(pass_context = True)
async def ev(ctx, *, code : str):
    """Evaluates a python statement"""
    context = js2py.EvalJs({"message":ctx.message})
    await client.say(context.eval(code))

def safeEval(code, args = None):
    safe_dict = {"abs":abs,"all":all,"any":any,"ascii":ascii,"bin":bin,"bool":bool,"dict":dict,"filter":filter,"float":float,"hex":hex,"int":int,"len":len,"range":range,"max":max,"min":min,"pow":pow,"reversed":reversed,"list":list,"sum":sum,"slice":slice,"str":str,"tuple":tuple,"ord":ord,"chr":chr}
    if args != None:
        safe_dict = dict(safe_dict.items() | args.items())
    return eval(code,{"__builtins__":None,"math":math},safe_dict)
    #return execjs.eval(code)

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
    if ctx.invoked_subcommand == None:
        if len(ctx.message.content.split(" "))>1:
            quote = int(ctx.message.content.split(" ")[1])
        else:
            quote = None
    
        if quote == None:
            quoteRand = random.choice(quotes)
            await client.say("**Quote #{}**\n{}".format(quotes.index(quoteRand)+1,quoteRand))
            return
            
        try:
            await client.say(quotes[quote-1])
        except:
            await client.say("That's not a quote!")
    
    
@quote.command(pass_context = True)
async def add(ctx, *, quote : str = None):
    """Add a quote"""
    quotes.append("{} - **{}** in **{}** at **{}**".format(quote,ctx.message.author.name,ctx.message.channel.name,time.strftime("%d/%m/%Y")))
    await client.say("Quote added as #{}!".format(len(quotes)))
    pickle.dump(quotes,open("quotes.p","wb"))

@quote.command(pass_context = True)
async def delete(ctx, num : int):
    """Delete a quote"""
    quotes[num-1] = "Deleted!"
    await client.say("Quote deleted!")
    pickle.dump(quotes,open("quotes.p","wb"))
        
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
    
@client.command()
async def trans(*, text : str):
    """Translate text to english (this function is very finnicky)"""
    await client.say(translate(text,"en"))

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
    
    client.run(token)
    
