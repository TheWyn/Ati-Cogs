import discord
from discord.ext import commands
import aiohttp

class BTC:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    @commands.command(pass_context=True)
    async def currency(self, ctx, currency:str):
        """fetches the price of btc in a currency."""
        url = 'https://blockchain.info/ticker'
        async with self.session.get(url) as resp:
            temp = await resp.json()
        btc = temp[currency]
        await self.bot.say(btc['symbol'] + '' + str(btc['last']))

    @commands.command(pass_context=True)
    async def unconf(self, ctx):
        """Shows the amount of unconfirmed transactions."""
        url = 'https://blockchain.info/q/unconfirmedcount'
        async with self.session.get(url) as resp:
            text = await resp.text()
        await self.bot.say(text)
        
    @commands.command(pass_context=True)
    async def totalbtc(self, ctx):
        """Shows the total amount of Bitcoin."""
        url = 'https://blockchain.info/q/totalbc'
        async with self.session.get(url) as resp:
            text = await resp.text()
        await self.bot.say(text)

    @commands.command(pass_context=True)
    async def hrprice(self, ctx):
        """Shows the 24 hour price."""
        url = 'https://blockchain.info/q/24hrprice'
        async with self.session.get(url) as resp:
            text = await resp.text()
        await self.bot.say(text)
        
    @commands.command(pass_context=True)
    async def hrcount(self, ctx):
        """Shows the 24hr transactioncount."""
        url = 'https://blockchain.info/q/24hrtransactioncount'
        async with self.session.get(url) as resp:
            text = await resp.text()
        await self.bot.say(text)

        
def setup(bot):
    n = BTC(bot)
    bot.add_cog(n)
