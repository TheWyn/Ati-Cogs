from discord import Object
from discord.ext import commands
from random import randint


orderChannel = Object('266684197970640897')  # <---- place the channel ID there
orders = {}
orderMessage = '''
Something something Discord Pizza sucks.

A new order has been placed! 
Order number :: **{i}**
Server name :: **{s}**
Order string :: **{w}**
'''


class Orders:

    def __init__(self, bot):
        self.bot = bot

    # Set up the order command
    @commands.command(pass_context=True)
    async def order(self, ctx, *, whatYouWant:str=None):
        '''
        Lets you place a milkshake order through the bot
        '''

        # Make sure they're actually ordering something
        if whatYouWant == None:
            await self.bot.say('You can\'t place an order for nothing!')
            return

        # Handle the order - save it, the orderer, and the server somewhere
        # Store the context too, just in case
        
        # Generate the order number
        orderNumber = randint(0, 0xFFFFFF)
        orderHex = str(hex(orderNumber))[2:]

        # Store the order and all relevant data internally
        orders[orderHex] = {
                'ctx':ctx, 
                'author':ctx.message.author, 
                'server':ctx.message.server,
                'channel':ctx.message.channel,
                'message':ctx.message,
                'order':whatYouWant
                }

        # Print out to user
        await self.bot.say('Your order of `{}` has been placed. You have order ID `{}`.'.format(whatYouWant, orderHex))

        # Print out to a orders channel
        await self.bot.send_message(orderChannel, orderMessage.format(w=whatYouWant, i=orderHex, s=ctx.message.server.name))


    # Set up the order handling
    @commands.command(pass_context=True)
    async def fulfil(self, ctx, orderNumber:str=None):
        '''
        Handles the fulfilling of someone's order
        '''

        # Makes sure it's on the right server
        if ctx.message.server.id != '208895639164026880':
            await self.bot.say('This command cannot be run on this server.')
            return

        # Make sure the order number isn't blank
        if orderNumber == None:
            await self.bot.say('You can\'t leave the order number blank.')
            return

        # Get the info of the order
        try:
            orderInfo = orders[orderNumber.lower()]
        except KeyError:
            await self.bot.say('The given order number does not exist.')
            return

        # Generate an invite to the given server
        invite = await self.bot.create_invite(orderInfo['server'], max_uses=1)
        await self.bot.say('Give the order of `{}` (`{}`) here :: {}'.format(orderInfo['order'], orderNumber.lower(), invite.url))

        # Delete the order from storage
        del orders[orderNumber.lower()]


    @commands.command(pass_context=True)
    async def openorders(self, ctx):
        '''
        Shows the orders that aren't fulfilled yet
        '''

        # Makes sure it's on the right server
        if ctx.message.server.id != '208895639164026880':
            await self.bot.say('This command cannot be run on this server.')
            return

        # Print them out nicely
        orderStuff = []
        for i, o in orders.items():
            orderStuff.append('[' + o['order']+ ',' + i + ']')
        await self.bot.say('```\n' + '\n'.join(orderStuff) + '```')


def setup(bot):
    bot.add_cog(Orders(bot))


