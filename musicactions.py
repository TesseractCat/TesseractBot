import discord
from discord.ext import commands
import pickle
from gtts import gTTS
from urllib.request import urlopen
import urllib.request
import youtube_dl
import urllib.parse
import json
from bot import nonAsyncRun, checkOp
import asyncio

class MusicActions():
    
    def __init__(self, client):
        self.client = client
        self.instances = {}
        
    @commands.command(pass_context=True)
    async def vfskp(self, ctx):
        """Votes to stop current music or text to speech"""
        
        if ctx.message.author.id in self.instances[ctx.message.server.id].voted:
             await self.client.say("You have already voted")
        else:
            self.instances[ctx.message.server.id].votes += 1
            await self.client.say("You have voted to skip the currently playing song, there are current **{}** votes to skip this. You need **3** votes to skip a song".format(self.instances[ctx.message.server.id].votes))
            self.instances[ctx.message.server.id].voted.append(ctx.message.author.id)
     
    @commands.command(pass_context=True)
    async def skp(self, ctx):
        """Stops music or text to speech"""
        if await checkOp(ctx.message):
            try:
                self.instances[ctx.message.server.id].queue[0].stop()
            except:
                pass
    
    @commands.command(pass_context=True)
    async def cp(self, ctx):
        """Plays information about what's currently playing"""
        await self.client.say("Currently playing **{}**".format(self.instances[ctx.message.server.id].queue[0].title))
    
    @commands.command(pass_context=True)
    async def res(self, ctx):
        """Resume what's currently playing"""
        self.instances[ctx.message.server.id].queue[0].resume()
        await self.client.say("Resumed!")
        
    @commands.command(pass_context=True)
    async def pau(self, ctx):
        """Pause what's currently playing"""
        self.instances[ctx.message.server.id].queue[0].pause()
        await self.client.say("Paused!")
    
    @commands.command(pass_context=True)
    async def vol(self, ctx, volume : float):
        """Sets the volume"""
        self.instances[ctx.message.server.id].queue[0].pause()
        self.instances[ctx.message.server.id].queue[0].volume = volume
        self.instances[ctx.message.server.id].queue[0].resume()
        await self.client.say("Volume set!")
    
    @commands.command(pass_context=True)
    async def ptts(self, ctx, *, text : str = None):
        """Plays tts in the voice channel you are currently in"""
        #if await checkOp(ctx.message):
        if self.client.voice_client_in(ctx.message.server) == None:
            voiceClient = await self.client.join_voice_channel(ctx.message.author.voice_channel)
        else:
            if self.client.voice_client_in(ctx.message.server).channel.id == ctx.message.author.voice_channel.id:
                voiceClient = self.client.voice_client_in(ctx.message.server)
            elif self.client.voice_client_in(ctx.message.server).channel.id != ctx.message.author.voice_channel.id:
                await self.client.voice_client_in(ctx.message.server).disconnect()
                voiceClient = await self.client.join_voice_channel(ctx.message.author.voice_channel)
        
        if len(ctx.message.content.rsplit(" ",1)[1]) == 2:
            try:
                tts = gTTS(text=text.rsplit(" ",1)[0], lang=ctx.message.content.rsplit(" ",1)[1])
            except:
                tts = gTTS(text=text, lang='en')
        else:
            tts = gTTS(text=text, lang='en')
        tts.save("tts.mp3")
        
        if ctx.message.server.id not in self.instances:
            self.instances[ctx.message.server.id] = MusicInstance(self.client)
        
        try:
            self.instances[ctx.message.server.id].player.stop()
        except:
            pass
        
        if len(self.instances[ctx.message.server.id].queue) > 0:
            self.instances[ctx.message.server.id].queue[0].pause()
        
        player = voiceClient.create_ffmpeg_player('tts.mp3')
        player.start()
        
        while True:
            await asyncio.sleep(1)
            if player.is_done():
                break
                
        if len(self.instances[ctx.message.server.id].queue) > 0:
            self.instances[ctx.message.server.id].queue[0].resume()
        
        #self.instances[ctx.message.server.id].addToQueue(voiceClient.create_ffmpeg_player('tts.mp3'), ctx.message.channel)
        
        #await self.client.say("Added to queue, you are currently **#{}** in the queue".format(len(self.instances[ctx.message.server.id].queue)))
        #self.instances[ctx.message.server.id].player = voiceClient.create_ffmpeg_player('tts.mp3')
        #self.instances[ctx.message.server.id].player.start()
        
    @commands.command(pass_context=True)
    async def pyv(self, ctx, *, url : str = None):
        """Plays youtube (and some other services) video in the voice channel you are currently in, provide either a url or youtube video name"""
        if bool(urllib.parse.urlparse(url).scheme) == False:
            response = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/search?part=id&q={}&key=AIzaSyCWey9JEsqeQiUimSQ1o5SlYr1slTRMlUM".format(url.replace(" ","%20")))
            response = response.read().decode("utf-8")
            response = json.loads(response.replace('\\"', "").replace("\\",r"\\").replace('""','"'))
            url = "https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId']
        
        if self.client.voice_client_in(ctx.message.server) == None:
            voiceClient = await self.client.join_voice_channel(ctx.message.author.voice_channel)
        else:
            if self.client.voice_client_in(ctx.message.server).channel.id == ctx.message.author.voice_channel.id:
                voiceClient = self.client.voice_client_in(ctx.message.server)
            elif self.client.voice_client_in(ctx.message.server).channel.id != ctx.message.author.voice_channel.id:
                await self.client.voice_client_in(ctx.message.server).disconnect()
                voiceClient = await self.client.join_voice_channel(ctx.message.author.voice_channel)
        
        if ctx.message.server.id not in self.instances:
            self.instances[ctx.message.server.id] = MusicInstance(self.client)
        
        try:
            self.instances[ctx.message.server.id].player.stop()
        except:
            pass
        
        #self.instances[ctx.message.server.id].player = await voiceClient.create_ytdl_player(url)
        self.instances[ctx.message.server.id].addToQueue(await voiceClient.create_ytdl_player(url), ctx.message.channel)        
        #self.instances[ctx.message.server.id].player.start()

    @commands.command()
    async def syv(self, *, searchQuery : str):
        """Finds the first result for a youtube search"""
        response = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/search?part=id&q={}&key=AIzaSyCWey9JEsqeQiUimSQ1o5SlYr1slTRMlUM".format(searchQuery.replace(" ","%20")))
        response = response.read().decode("utf-8")
        response = json.loads(response.replace('\\"', "").replace("\\",r"\\").replace('""','"'))
        await self.client.say("https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId'])
        
class MusicInstance():
    def __init__(self, client):
        self.player = None
        self.serverId = None
        self.queue = []
        self.votes = 0
        self.voted = []
        self.client = client
    
    def addToQueue(self, player, channel):
        print(self.queue)
        nonAsyncRun(self.client.send_message, (channel, "Added to queue, you are currently **#{}** in the queue".format(len(self.queue)+1)))
        self.queue.append(player)
        if len(self.queue) == 1:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.async, self.playQueue(channel))
            
    async def playQueue(self, channel):
        while True:
            if len(self.queue) > 0:
                if self.queue[0].is_done():
                    self.queue.pop(0)
                    self.votes = 0
                    self.voted = []
                    try:
                        await self.client.send_message(channel, "Now playing **{}**...".format(self.queue[0].title))
                    except:
                        await self.client.send_message(channel, "Now playing next item in queue...")
                elif self.votes > 2:
                    self.queue[0].stop()
                else:
                    try:
                        self.queue[0].start()
                    except:
                        pass
            else:
                break
            await asyncio.sleep(1.0)
        
def setup(client):
    client.add_cog(MusicActions(client))