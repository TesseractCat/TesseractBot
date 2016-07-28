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
import subprocess
import os
import urbandict
import configparser
import urllib.request
from ctypes.util import find_library
from discord.ext import commands
import re

#Discord Client
client = commands.Bot(command_prefix='$', description='Tesseract Multipurpose Bot')

#Wolfram Alpha Client
waClient = wolframalpha.Client("2J69RV-TGJ5RGLKPA")

#Load Discord Opus
discord.opus.load_opus(find_library("opus"))

#Cogs to load
cogs = ["customcommands","customanimations","botactions","musicactions","imageactions","cards","spreadsheets","rss","ranks","weather","voting"]

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
    try:
        print(message.author.name + "@" + message.server.name + "~" + message.channel.name + ": " + message.content)
    except:
        pass
    
    for command in opCommands:
        if (client.command_prefix + command + " ") in message.content:
            if await checkOp(message) == False:
                return
    
    if message.author.id in banned:
        return
    
    if message.author.id == client.user.id:
        return
    
    if client.user.id in message.content:
        await bot(message)
    
    await client.process_commands(message)
    
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
    await client.say(str(safeEval(code)))

def safeEval(code, args = None):
    safe_dict = {"abs":abs,"all":all,"any":any,"ascii":ascii,"bin":bin,"bool":bool,"dict":dict,"filter":filter,"float":float,"hex":hex,"int":int,"len":len,"range":range,"max":max,"min":min,"pow":pow,"reversed":reversed,"list":list,"sum":sum,"slice":slice,"str":str,"tuple":tuple,"ord":ord,"chr":chr}
    if args != None:
        safe_dict = dict(safe_dict.items() | args.items())
    return eval(code,{"__builtins__":None,"math":math},safe_dict)
    
#@client.command(pass_context = True)
#async def ex(ctx, *, code : str):
#    """Executes python code"""
#    if await checkOp(ctx.message):
#        exec(code,globals(),locals())

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
    """Gets Wolfram Alpha result for [search]"""
    
    watext = ""
    watext += "**--- Wolfram Alpha result for: " + search + " ---**\n"
    await client.send_typing(ctx.message.channel)
    waresult = waClient.query(search)
    for pod in waresult.pods:
        watext+="**"+pod.title+"**\n"
        if pod.text == None:
            watext+=pod.img + "\n"
            await client.say(watext)
            watext = ""
        else:
            watext+=bytes(pod.text.replace("\\:","\\u"),'utf-8').decode("unicode_escape") + "\n"
    if len(waresult.pods) < 1:
        watext += "*No results, please rephrase your query.*"
    await client.say(watext)
    
if __name__ == "__main__":
    client.run(token)


