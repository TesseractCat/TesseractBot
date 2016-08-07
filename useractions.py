import discord
from discord.ext import commands
import pickle
import asyncio
from urllib.request import urlopen

class UserActions():
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(pass_context = True)
    async def gr(self, ctx, member : discord.Member, *, role : str):
        """Gives role"""
        
        if ctx.message.author.permissions_in(ctx.message.channel).manage_channels:
            await self.client.add_roles(member, discord.utils.get(ctx.message.server.roles, name=role))
    
    @commands.command(pass_context = True)
    async def rr(self, ctx, member : discord.Member, *, role : str):
        """Remove role"""
        
        if ctx.message.author.permissions_in(ctx.message.channel).manage_channels:
            await self.client.remove_roles(member, discord.utils.get(ctx.message.server.roles, name=role))
        
    @commands.command(pass_context = True, aliases = ["whoami"])
    async def whois(self, ctx, member : discord.Member = None):
        if member == None:
            user = ctx.message.author
        else:
            user = member
        readable_roles = []
        for role in user.roles:
            readable_roles.append(role.name)
        whoText = "{}\nRoles: `{}`\nJoin date: `{}`\nAccount created: `{}`\nUser ID: `{}`\nAvatar: {}".format(user.mention,"`, `".join(readable_roles),user.joined_at.strftime('%Y-%m-%d'),user.created_at,user.id,user.avatar_url)
        await self.client.say(whoText)
        
def setup(client):
    client.add_cog(UserActions(client))