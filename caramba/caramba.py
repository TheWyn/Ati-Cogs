class Caramba:
    def __init__(self, bot):
        self.bot = bot

    async def listener(self, message):
        if message.author.id != self.bot.user.id and (
            message.content.lower().startswith('ayy')
            or message.content.lower().startswith('aayy')
        ):
            await self.bot.send_message(message.channel, '¡Caramba!')


def setup(bot):
    n = Caramba(bot)
    bot.add_listener(n.listener, "on_message")
    bot.add_cog(n)
