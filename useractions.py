import discord
from discord.ext import commands
from bot import getShelfSlot

class UserActions():
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(pass_context = True)
    async def op(self, ctx, member : discord.Member):
        operators = getShelfSlot(ctx.message.server.id, "Operators")
        try:
            operators["ids"].append(member.id)
        except:
            operators["ids"] = [member.id]
        operators.close()
        
        await self.client.say("**{}** opped!".format(member.name))
        
    @commands.command(pass_context = True)
    async def deop(self, ctx, member : discord.Member):
        operators = getShelfSlot(ctx.message.server.id, "Operators")
        try:
            operators["ids"].remove(member.id)
            await self.client.say("**{}** deopped!".format(member.name))
        except:
            await self.client.say("**{}** is not an operator!".format(member.name))
        operators.close()
    
    @commands.command(pass_context = True, aliases = ["gr"])
    async def giverole(self, ctx, member : discord.Member, *, role : str):
        """Gives role"""
        
        await self.client.add_roles(member, discord.utils.get(ctx.message.server.roles, name=role))
    
    @commands.command(pass_context = True, aliases = ["rr"])
    async def removerole(self, ctx, member : discord.Member, *, role : str):
        """Remove role"""
        
        await self.client.remove_roles(member, discord.utils.get(ctx.message.server.roles, name=role))
    
    @commands.command(pass_context = True, aliases = ["giurl"])
    async def getimageurl(self, ctx, name : str):
        """Get image url by name"""
        
        await self.client.say(discord.utils.find(lambda m: m.name.lower() == name.lower(), ctx.message.server.members).avatar_url)
    
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