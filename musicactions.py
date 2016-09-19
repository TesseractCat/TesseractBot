import discord
from discord.ext import commands
from gtts import gTTS
import urllib.request
import youtube_dl
import urllib.parse
import json
from bot import checkOp
from bot import getShelfSlot
from bot import nonAsyncRun
import asyncio

class MusicActions():
    
    def __init__(self, client):
        self.client = client
        self.instances = {}
        
    @commands.command(pass_context=True, aliases = ["vfskp"])
    async def voteforskip(self, ctx):
        """Votes to stop current music or text to speech"""
        
        if ctx.message.author.id in self.instances[ctx.message.server.id].voted:
             await self.client.say("You have already voted")
        else:
            self.instances[ctx.message.server.id].votes += 1
            await self.client.say("You have voted to skip the currently playing song, there are current **{}** votes to skip this. You need **3** votes to skip a song".format(self.instances[ctx.message.server.id].votes))
            self.instances[ctx.message.server.id].voted.append(ctx.message.author.id)
    
    @commands.command(pass_context=True, aliases = ["clrqueue"])
    async def clearqueue(self, ctx):
        try:
            if len(self.instances[ctx.message.server.id].queue) > 0:
                self.instances[ctx.message.server.id].queue[0].stop()
                self.instances[ctx.message.server.id].queue = []
        except:
            pass
    
    @commands.command(pass_context=True, aliases = ["skp"])
    async def skip(self, ctx):
        """Stops music or text to speech"""
        try:
            if len(self.instances[ctx.message.server.id].queue) > 0:
                self.instances[ctx.message.server.id].queue[0].stop()
        except:
            pass
    
    @commands.command(pass_context=True, aliases = ["cp"])
    async def currentlyplaying(self, ctx):
        """Plays information about what's currently playing"""
        try:
            await self.client.say("Currently playing **{}**".format(self.instances[ctx.message.server.id].queue[0].title))
        except:
             await self.client.say("Currently playing text to speech and or not playing anything")
    
    @commands.command(pass_context=True, aliases = ["res"])
    async def resume(self, ctx):
        """Resume what's currently playing"""
        self.instances[ctx.message.server.id].queue[0].resume()
        await self.client.say("Resumed!")
        
    @commands.command(pass_context=True, aliases = ["pau"])
    async def pause(self, ctx):
        """Pause what's currently playing"""
        self.instances[ctx.message.server.id].queue[0].pause()
        await self.client.say("Paused!")
    
    @commands.command(pass_context=True, aliases = ["vol"])
    async def volume(self, ctx, volume : float):
        """Sets the volume"""
        self.instances[ctx.message.server.id].queue[0].pause()
        self.instances[ctx.message.server.id].queue[0].volume = volume
        self.instances[ctx.message.server.id].queue[0].resume()
        await self.client.say("Volume set!")
    
    @commands.command(pass_context=True, aliases = ["ptts"])
    async def playtexttospeach(self, ctx, *, text : str = None):
        """Plays tts in the voice channel you are currently in"""
        
        voiceClient = await self.getVoiceClient(ctx)
        
        if len(ctx.message.content.rsplit(" ",1)[1]) == 2:
            try:
                tts = gTTS(text=text.rsplit(" ",1)[0], lang=ctx.message.content.rsplit(" ",1)[1])
            except:
                tts = gTTS(text=text, lang='en')
        else:
            tts = gTTS(text=text, lang='en')
        tts.save("tts.mp3")
        
        mInstance = self.getMusicInstance(ctx.message.server)
        
        try:
            mInstance.player.stop()
        except:
            pass
        
        if voiceClient != None:
            mInstance.addToQueue(voiceClient.create_ffmpeg_player('tts.mp3', after=mInstance.playNext), ctx.message.channel)
        
    @commands.command(pass_context=True, aliases = ["pyv"])
    async def playyoutubevideo(self, ctx, *, url : str = None):
        """Plays youtube (and some other services) video in the voice channel you are currently in, provide either a url or youtube video name"""
        if bool(urllib.parse.urlparse(url).scheme) == False:
            response = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/search?part=id&q={}&key=AIzaSyCWey9JEsqeQiUimSQ1o5SlYr1slTRMlUM".format(url.replace(" ","%20")))
            response = response.read().decode("utf-8")
            response = json.loads(response.replace('\\"', "").replace("\\",r"\\").replace('""','"'))
            url = "https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId']
        
        voiceClient = await self.getVoiceClient(ctx)
        
        mInstance = self.getMusicInstance(ctx.message.server)
        
        try:
            mInstance.player.stop()
        except:
            pass
        
        if voiceClient != None:
            mInstance.addToQueue(await voiceClient.create_ytdl_player(url, after=mInstance.playNext), ctx.message.channel)

    def getMusicInstance(self, server):
        if server.id not in self.instances:
            self.instances[server.id] = MusicInstance(self.client, asyncio.get_event_loop())
        return self.instances[server.id]
            
    async def getVoiceClient(self, ctx):
        try:
            if self.client.voice_client_in(ctx.message.server) == None:
                voiceClient = await self.client.join_voice_channel(ctx.message.author.voice_channel)
            else:
                if self.client.voice_client_in(ctx.message.server).channel.id == ctx.message.author.voice_channel.id:
                    voiceClient = self.client.voice_client_in(ctx.message.server)
                elif self.client.voice_client_in(ctx.message.server).channel.id != ctx.message.author.voice_channel.id:
                    await self.client.voice_client_in(ctx.message.server).disconnect()
                    voiceClient = await self.client.join_voice_channel(ctx.message.author.voice_channel)
        except:
            return
                
        return voiceClient
        
    @commands.command(aliases = ["syv"])
    async def searchyoutubevideos(self, *, searchQuery : str):
        """Finds the first result for a youtube search"""
        response = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/search?part=id&q={}&key=AIzaSyCWey9JEsqeQiUimSQ1o5SlYr1slTRMlUM".format(searchQuery.replace(" ","%20")))
        response = response.read().decode("utf-8")
        response = json.loads(response.replace('\\"', "").replace("\\",r"\\").replace('""','"'))
        await self.client.say("https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId'])
    
        
class MusicInstance():
    def __init__(self, client, loop):
        self.player = None
        self.serverId = None
        self.queue = []
        self.votes = 0
        self.voted = []
        self.client = client
        self.loop = loop
        self.channel = None
    
    def addToQueue(self, player, channel):
        self.channel = channel
        try:
            nonAsyncRun(self.client.send_message, (channel, "**{}** added to queue, you are currently **#{}** in the queue".format(player.title, len(self.queue)+1)))
        except:
            nonAsyncRun(self.client.send_message, (channel, "Added to queue, you are currently **#{}** in the queue".format(len(self.queue)+1)))
        self.queue.append(player)
        
        if len(self.queue) == 1:
            self.queue[0].start()
    
    def playNext(self):
        print("Playing next song!")
        
        #try:
        #    self.queue[0].stop()
        #except:
        #    pass
        
        self.queue.pop(0)
        self.votes = 0
        self.voted = []
        #print("Now playing **{}**...".format(self.queue[0].title))
        try:
            #await self.client.send_message(self.channel, "Now playing **{}**...".format(self.queue[0].title))
            nonAsyncRun(self.client.send_message, (self.channel, "Now playing **{}**...".format(self.queue[0].title)))
            self.queue[0].start()
            print("Done playing next song!")
        except:
            if len(self.queue) > 0:
                #await self.client.send_message(self.channel, "Now playing next item in queue...")
                nonAsyncRun(self.client.send_message, (self.channel, "Now playing next item in queue..."))
                self.queue[0].start()
            else:
                #await self.client.send_message(self.channel, "Done playing music!")
                nonAsyncRun(self.client.send_message, (self.channel, "Done playing!"))
                #await self.client.voice_client_in(self.channel.server).disconnect()
        
def setup(client):
    client.add_cog(MusicActions(client))
