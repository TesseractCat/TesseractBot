import discord
from discord.ext import commands
import pickle
import asyncio
from urllib.request import urlopen
from bot import nonAsyncRun, printToDiscord, checkOp, safeEval, getShelfSlot, doUrlopen, getToken
import atexit
import random
import markovify
import wolframalpha
import threading
import xmltodict
import urllib.request
import urllib
import brainfuck
import urbandict
from translate import translate
import html
import re

class CustomUtilities():
    
    def __init__(self, client):
        self.client = client
        
        #Wolfram Alpha Client
        self.waClient = wolframalpha.Client(getToken("wolframalpha"))
    
    # Quotes
    
    @commands.group(pass_context = True, aliases = ["qt"])
    async def quote(self, ctx):
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
                await self.client.say("**Quote #{}**\n{}".format(quotes["quotes"].index(quoteRand)+1,quoteRand))
                return
                
            try:
                await self.client.say(quotes["quotes"][quote-1])
            except:
                await self.client.say("That's not a quote!")
        quotes.close()
        
    @quote.command(pass_context = True)
    async def add(self, ctx, *, quote : str = None):
        """Add a quote"""
        quotes = getShelfSlot(ctx.message.server.id, "Quotes")
        quotes["quotes"].append("{} - **{}** in **{}** at **{}**".format(quote,ctx.message.author.name,ctx.message.channel.name,time.strftime("%d/%m/%Y")))
        await self.client.say("Quote added as #{}!".format(len(quotes["quotes"])))
        quotes.close()

    @quote.command(pass_context = True, aliases = ["del"])
    async def delete(self, ctx, num : int):
        """Delete a quote"""
        quotes = getShelfSlot(ctx.message.server.id, "Quotes")
        quotes["quotes"][num-1] = "Deleted!"
        await self.client.say("Quote deleted!")
        quotes.close()
        
    # Quotes done
    
    # Reminders
    
    @commands.command(pass_context = True, aliases = ["rem"])
    async def remind(self, ctx, time : int, unit : str, *, text : str):
        thread = threading.Thread(target=doRemind,args=(ctx, time, unit.lower(), text, asyncio.get_event_loop()))
        thread.start()

    def doRemind(self, ctx, timeToSleep, unit, text, loop):
        if "second" in unit:
            sleepTime = (timeToSleep)
        elif "minute" in unit:
            sleepTime = (timeToSleep*60)
        elif "hour" in unit:
            sleepTime = (timeToSleep*60*60)
        elif "day" in unit:
            sleepTime = (timeToSleep*60*60*24)
        else:
           loop.call_soon_threadsafe(asyncio.async, self.client.send_message(ctx.message.channel,"That is not a valid time unit, the available units are: seconds, minutes, hours, days"))
           return
        
        loop.call_soon_threadsafe(asyncio.async, self.client.send_message(ctx.message.channel,"Ok! I will remind you in `{}` {}".format(timeToSleep, unit)))
        
        time.sleep(sleepTime)
        
        loop.call_soon_threadsafe(asyncio.async, self.client.send_message(ctx.message.author, "Hello! `{}` {} ago you asked me to remind you of:\n\n{}".format(timeToSleep, unit, text)))
    
    # Reminders done
    
    @commands.command(pass_context = True, aliases = ["mal"])
    async def myanimelist(self, ctx, *, searchQuery : str):
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
        
        await self.client.say("**--- Result for search: {} ---**\nTitle: **{}**\nEpisodes: **{}**\nScore: **{}**\nType: **{}**\nStatus: **{}**\n\nSynopsis: *{}*\n\nImage: {}".format(searchQuery, result["title"],result["episodes"],result["score"],result["type"],result["status"],html.unescape(re.sub(re.compile('<.*?>'), '', result["synopsis"])),result["image"]))
    
    
    @commands.command(pass_context = True, aliases = ["wa"])
    async def wolframalpha(self, ctx,*, search : str):
        """Gets Wolfram Alpha result for [search] put a 'true' at the beginning of your search to enable images."""
        
        watext = "**--- Wolfram Alpha result for: " + search + " ---**\n"
        await self.client.send_typing(ctx.message.channel)
        
        if search.split(" ")[0].lower() == "true":
            waresult = self.waClient.query(search.split(" ",1)[1])
        else:
            waresult = self.waClient.query(search)
        
        for pod in waresult.pods:
            watext+="**"+pod.title+"**\n"
            if pod.text == None and search.split(" ")[0].lower() == "true":
                watext+=pod.img + "\n"
                await client.say(watext)
                watext = ""
            elif pod.text != None:
                watext+=pod.text.replace("\\:","\\u") + "\n"
        if len(waresult.pods) < 1:
            watext += "*No results, please rephrase your query.*"
        await self.client.say(watext)
    
    @commands.command(aliases = ["bf"])
    async def brainfuck(self, bfsrc : str, bfinput : str = ""):
        """Executes brainfuck code"""
        
        bftext = ""

        bftext += "**--- Brainfuck result ---**\n"
            
        bftext += "```" + brainfuck.bf(bfsrc, 0, len(bfsrc) - 1, bfinput, 0, 1000000)
        await self.client.say(bftext[:1500] + " ```")
    
    @commands.command(aliases = ["df"])
    async def define(self, word : str, defNum : int = 1):
        """Defines a word"""
        
        await self.client.say(urbandict.define(word)[defNum-1]['def'])
    
    @commands.command(pass_context = True, aliases = ["ev"])
    async def evaluate(self, ctx, *, code : str):
        """Evaluates a python statement"""
        await self.client.say(safeEval("return " + code, {"message": ctx.message, "urlopen": doUrlopen, "client": {"servers":self.client.servers, "user":self.client.user}, "list": lambda x: [obj for obj in x]})[:1000])
    
    @commands.command(pass_context = True, aliases = ["rep"])
    async def reputation(self, ctx, user : discord.User = None):
        repDict = getShelfSlot(ctx.message.server.id, "Rep")
        
        if (user == ctx.message.author):
            await self.client.say("You can't give yourself rep!")
            return
        
        if (user == None):
            try:
                await self.client.say("You have `{}` rep!".format(repDict[ctx.message.author.id]))
            except:
                await self.client.say("You have no rep!")
        else:
            try:
                repDict[user.id] += 1
            except:
                repDict[user.id] = 1
                
            await self.client.say("1 rep given to {}, they currently have `{}` rep.".format(user.mention, repDict[user.id]))
        
        repDict.close()
        
    @commands.command(pass_context = True, aliases = ["mkv"])
    async def markov(self, ctx, channel : discord.Channel, messages : int = 500, stateSize : int = 1):
        """Make a markov chain of a channel"""
        text = ""
        async for message in client.logs_from(channel, limit=messages):
            text += message.content.replace("<@","@") + "\n"
        text_model = markovify.Text(text, state_size=stateSize)
        await self.client.say(text_model.make_sentence(max_overlap_ratio = 0.9,max_overlap_total=30,tries=1000))
        
    @commands.command(pass_context = True, aliases = ["trans"])
    async def translate(self, ctx, *, text : str):
        """Translate text to english (this function is very finnicky)"""
        #if len(ctx.message.content.rsplit(" ",1)[1]) == 2:
        #    await self.client.say(translate(ctx.message.content.rsplit(" ",1)[0].split(" ",1)[1],ctx.message.content.rsplit(" ",1)[1]))
        #else:
        await self.client.say("**Translated text:** " + translate(text,"en"))
    
def setup(client):
    client.add_cog(CustomUtilities(client))