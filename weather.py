import discord
from discord.ext import commands
import pickle
import asyncio
import json
from urllib.request import urlopen

class Weather():
    
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def gw(self, *, searchQuery : str):
        """Gets the weather"""
        
        response = urlopen("http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=6237b97deb8130b2f11042e9fe0c1297".format(searchQuery.replace(" ",",")))
        response = response.read().decode("utf-8", "ignore")
        response = json.loads(response)
        wtr = response
        
        await self.client.say("The weather in **{}** is **{} ({})**. The wind speed is **{} mph ({} deg)**. The humidity is **{}%**. The temperature is **{}F**.".format(wtr['name'],wtr['weather'][0]['main'],wtr['weather'][0]['description'],wtr['wind']['speed'],wtr['wind']['deg'],str(wtr['main']['humidity']),str(wtr['main']['temp'])))
        
def setup(client):
    client.add_cog(Weather(client))