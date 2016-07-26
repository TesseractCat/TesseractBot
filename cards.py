import discord
from discord.ext import commands
import pickle
import asyncio
from cardAscii import Card
import pydealer

class Cards():
    
    def __init__(self, client):
        self.client = client
        
        self.games = {}
    
    @commands.group(pass_context = True)
    async def cards(self, ctx):
        """Cards parent command"""
    
        if ctx.invoked_subcommand is None:
            await self.client.say('Cards itself is not a command, please invoke a subcommand.')
            
    @cards.command(pass_context = True)
    async def start(self, ctx):
        """Starts a card game"""
    
        if ctx.message.server.id in self.games:
            await self.client.say('A card game is already running, please finish that and then run this command')
        else:
            self.games[ctx.message.server.id] = CardGame(ctx.message.author)
            await self.client.say('Card game started! You are the dealer!')
            
    @cards.command(pass_context = True)
    async def stop(self, ctx):
        """Stops a card game"""
    
        if ctx.message.server.id in self.games:
            del self.games[ctx.message.server.id]
            await self.client.say('Card game stopped!')
        else:
            await self.client.say('You cannot stop a nonexistent card game. If you are not the dealer you cannot stop a card game.')
    
    @cards.command(pass_context = True)
    async def shuffle(self, ctx):
        """Shuffles the deck"""
    
        if self.games[ctx.message.server.id].dealer == ctx.message.author:
            self.games[ctx.message.server.id].deck.shuffle()
            await self.client.say('Deck shuffled!')
        else:
            await self.client.say('You are not the dealer!')
    
    @cards.command(pass_context = True)
    async def deal(self, ctx, member : discord.Member, cardNum : int):
        """Deals card from the deck, you must be the dealer."""
        
        if self.games[ctx.message.server.id].dealer == ctx.message.author:
            if member in self.games[ctx.message.server.id].hands:
                self.games[ctx.message.server.id].hands[member] += self.games[ctx.message.server.id].deck.deal(cardNum)
            else:
                self.games[ctx.message.server.id].hands[member] = pydealer.Stack()
                self.games[ctx.message.server.id].hands[member] += self.games[ctx.message.server.id].deck.deal(cardNum)
            await self.client.say('**{}** cards dealt to **{}**!'.format(cardNum,member.name))
        else:
            await self.client.say('You are not the dealer!')
    
    @cards.command(pass_context = True)
    async def take(self, ctx, cardNum : int):
        """Takes card from the deck."""
        
        if ctx.message.author in self.games[ctx.message.server.id].hands:
            self.games[ctx.message.server.id].hands[ctx.message.author] += self.games[ctx.message.server.id].deck.deal(cardNum)
        else:
            self.games[ctx.message.server.id].hands[ctx.message.author] = pydealer.Stack()
            self.games[ctx.message.server.id].hands[ctx.message.author] += self.games[ctx.message.server.id].deck.deal(cardNum)
        await self.client.say('**{}** cards given to **{}**!'.format(cardNum,ctx.message.author.name))
    
    @cards.command(pass_context = True)
    async def give(self, ctx, member : discord.Member, *, cardType : str):
        """Gives a card from your deck to anothers. ex. $cards give @user ace of spades."""
    
        if ctx.message.author in self.games[ctx.message.server.id].hands:
            cardToAdd = self.games[ctx.message.server.id].hands[ctx.message.author].get(cardType)
            if member in self.games[ctx.message.server.id].hands:
                self.games[ctx.message.server.id].hands[member] += cardToAdd
                self.games[ctx.message.server.id].hands[ctx.message.author].cards.remove(cardToAdd)
            else:
                self.games[ctx.message.server.id].hands[member] = pydealer.Stack()
                self.games[ctx.message.server.id].hands[member] += cardToAdd
                self.games[ctx.message.server.id].hands[ctx.message.author].cards.remove(cardToAdd)
        else:
            await self.client.say('You have not been dealt to!')
    
    @cards.command(pass_context = True)
    async def hand(self, ctx):
        """Pm's you your hand"""
    
        if ctx.message.author in self.games[ctx.message.server.id].hands:
            cardText = ""
            for card in self.games[ctx.message.server.id].hands[ctx.message.author].cards:
                cardText += Card(card.suit,card.value).getText() + "\n"
                
            await self.client.send_message(ctx.message.author, "```" + cardText + "```")
        else:
            await self.client.say('You have not been dealt to!')
        
    @cards.command()
    async def card(self, suit, rank):
        """Posts a card"""
    
        await self.client.say("```" + Card(suit,rank).getText() + "```")
        
def setup(client):
    client.add_cog(Cards(client))
    
    
class CardGame():
    
    def __init__(self, dealer):
        self.dealer = dealer
        self.deck = pydealer.Deck()
        self.hands = {}