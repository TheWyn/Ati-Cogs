import discord
from discord.ext import commands
import requests

class BTC:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def currency(self, ctx, currency:str):
        """fetches the price of btc in a currency."""
        url = 'https://blockchain.info/ticker'
        resp = requests.get(url)
        btc = resp.json()[currency]
        await self.bot.say(btc['symbol'] + '' + str(btc['last']))

    @commands.command(pass_context=True)
    async def unconf(self, ctx):
        """Shows the amount of unconfirmed transactions."""
        url = 'https://blockchain.info/q/unconfirmedcount'
        resp = requests.get(url)
        await self.bot.say(resp.text + '')
        
    @commands.command(pass_context=True)
    async def totalbtc(self, ctx):
        """Shows the total amount of Bitcoin."""
        url = 'https://blockchain.info/q/totalbc'
        resp = requests.get(url)
        await self.bot.say(resp.text + '')

    @commands.command(pass_context=True)
    async def hrprice(self, ctx):
        """Shows the 24 hour price."""
        url = 'https://blockchain.info/q/24hrprice'
        resp = requests.get(url)
        await self.bot.say(resp.text + '')
        
    @commands.command(pass_context=True)
    async def hrcount(self, ctx):
        """Shows the 24hr transactioncount."""
        url = 'https://blockchain.info/q/24hrtransactioncount'
        resp = requests.get(url)
        await self.bot.say(resp.text + '')
        
def setup(bot):
    n = BTC(bot)
    bot.add_cog(n)
