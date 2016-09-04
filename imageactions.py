import discord
from discord.ext import commands
from urllib.request import urlopen
from imgurpython import ImgurClient
import urllib.request
import urllib.parse
import json
import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class ImageActions():
    
    def __init__(self, client):
        self.client = client
        
        #Imgur Client
        self.client_id = '0df455c1dad9968'
        self.client_secret = 'e18b989f6d222e0bb792763d57623c1ac766d6aa'
        self.imgurClient = ImgurClient(self.client_id, self.client_secret)
        
    @commands.command()
    async def si(self, *, search : str):
        """Searches imgur"""
        
        items = self.imgurClient.gallery_search(search,sort="score")
        
        try:
            randomItem = random.randrange(0,len(items)-1)
        except:
            await self.client.say("No results, please try to rephrase your search.")
        
        try:
            await self.client.say("http://i.imgur.com/{}.png".format(items[randomItem].cover))
        except:
            await self.client.say(items[randomItem].link)

    @commands.command()
    async def sbi(self, *, searchQuery : str):
        """Searches bing images"""
        
        key = "TDZZ6YVo7aiuZu890EjYxZltaspM1oBAJkU7DCyy1i8"
        url = "https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27{}%27&$format=json".format(searchQuery.replace(" ","%20"))
        
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, key, key)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        
        response = opener.open(url)
        response = response.read().decode("utf-8")
        response = json.loads(response)["d"]["results"][0]["MediaUrl"]
        
        
        await self.client.say(response)
        
    @commands.command()
    async def sgi(self, *, searchQuery : str):
        """Searches google images"""
        
        try:
            response = urllib.request.urlopen("https://www.googleapis.com/customsearch/v1?safe=high&q={}&key=AIzaSyCWey9JEsqeQiUimSQ1o5SlYr1slTRMlUM&cx=013069748485055050082:lrdbh42tc-o&searchType=image".format(searchQuery.replace(" ","%20")))
        except:
            await self.client.say("*Google api quota exceeded, please try $sbi to search bing images.*")
            return
        response = response.read().decode("utf-8")
        
        response = json.loads(response.replace('\\"', "").replace("\\",r"\\").replace('""','"'))["items"][0]["link"]
        if len(response.split(":")) > 2:
            response = response.rsplit(":",1)[0]
        
        await self.client.say(response)

    @commands.command()
    async def cap(self, url : str, fontSize : int, *, caption : str):
        """Add [caption] in impact font to the bottom of [image url]"""
        
        request = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request)
        file = open("image.jpg","wb")
        file.write(response.read())
        
        pilimage = Image.open("image.jpg")
        pildraw = ImageDraw.Draw(pilimage)
        pilfont = ImageFont.truetype("Impact.ttf", fontSize)
        piltextsize = pildraw.textsize(caption,font=pilfont)
        
        #Border
        pildraw.text((pilimage.size[0]/2 - piltextsize[0]/2 + 3, pilimage.size[1] - piltextsize[1] * 1.5),caption,(0,0,0),font=pilfont)
        pildraw.text((pilimage.size[0]/2 - piltextsize[0]/2 - 3, pilimage.size[1] - piltextsize[1] * 1.5),caption,(0,0,0),font=pilfont)
        pildraw.text((pilimage.size[0]/2 - piltextsize[0]/2, pilimage.size[1] - piltextsize[1] * 1.5 + 3),caption,(0,0,0),font=pilfont)
        pildraw.text((pilimage.size[0]/2 - piltextsize[0]/2, pilimage.size[1] - piltextsize[1] * 1.5 - 3),caption,(0,0,0),font=pilfont)

        pildraw.text((pilimage.size[0]/2 - piltextsize[0]/2, pilimage.size[1] - piltextsize[1] * 1.5),caption,(255,255,255),font=pilfont)
        pilimage.save('outimage.jpg')
        await self.client.upload(open("outimage.jpg","rb"))
        
def setup(client):
    client.add_cog(ImageActions(client))
