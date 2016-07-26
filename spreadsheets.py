import discord
from discord.ext import commands
import pickle
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Spreadsheets():
    
    def __init__(self, client):
        self.client = client
        
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_id_spreadsheets.json', scope)
        self.gc = gspread.authorize(credentials)
        
        self.sheet = None
        self.workSheet = None
    
    @commands.group(pass_context = True)
    async def sheets(self, ctx):
        """Sheets parent command"""
    
        if ctx.invoked_subcommand is None:
            await self.client.say('Sheets itself is not a command, please invoke a subcommand.')
            
    @sheets.command()
    async def open(self, *, url : str):
        """Open sheet from url"""
        
        self.sheet = self.gc.open_by_url(url)
        self.workSheet = self.sheet.sheet1
        
    @sheets.command()
    async def select(self, *, num : int):
        """Select worksheet by number"""
    
        self.workSheet = self.sheet.get_worksheet(num-1)
        
    @sheets.command()
    async def getval(self, *, pos : str):
        """Gets value at position"""
    
        await self.client.say(self.workSheet.acell(pos).value)
        
    @commands.command()
    async def gettime(self, level : int, place : int = 0):
        sheet = self.gc.open_by_url("https://docs.google.com/spreadsheets/d/1JYW-mxu1w2oo7w93z6-duOGPj2tgrlQLDX7SqpCsl34/edit#gid=0").sheet1

        if place > 0:
            place -= 1

        await self.client.say(sheet.cell(level+2,4+(place*2)).value + ": " + sheet.cell(level+2,5+(place*2)).value)
        
def setup(client):
    client.add_cog(Spreadsheets(client))