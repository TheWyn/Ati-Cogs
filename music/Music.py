import discord
from discord.ext import commands
from . import lavalink


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.lavalink = lavalink.Client(bot=bot, password='youshallnotpass', loop=self.bot.loop)

        self.state_keys = {}
        self.validator = ['op', 'guildId', 'sessionId', 'event']

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        """Play a URL."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

        if not player.is_connected():
            await player.connect(channel_id=ctx.author.voice.channel.id)

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        tracks = await self.lavalink.get_tracks(query)
        if not tracks:
            return await ctx.send('Nothing found 👀')

        await player.add(requester=ctx.author.id, track=tracks[0], play=True)

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                              title="Track Enqueued",
                              description=f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})')
        await ctx.send(embed=embed)

    @commands.command(aliases=['forceskip', 'fs'])
    async def skip(self, ctx):
        """Skip to the next track."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        await player.skip()

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        """Stop playback."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if player.is_playing():
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour, description="Stopping...")
            await ctx.send(embed=embed)
            await player.stop()
        else:
            pass

    @commands.command(aliases=['np', 'n'])
    async def now(self, ctx):
        """Now playing."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        song = 'Nothing'
        if player.current:
            arrow = await self._draw_time(ctx)
            pos = lavalink.Utils.format_time(player.position)
            if player.current.stream:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
        song = f'**[{player.current.title}]({player.current.uri})**\n{arrow}\n({pos}/{dur})'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Now Playing', description=song)
        await ctx.send(embed=embed)

    async def _draw_time(self, ctx):
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        pos = player.position
        dur = player.current.duration
        sections = 12
        loc_time = round((pos / dur) * sections)  # 10 sections

        bar = ':white_small_square:'
        seek = ':small_blue_diamond:'

        msg = "|"

        for i in range(sections):
            if i == loc_time:
                msg += seek
            else:
                msg += bar

        msg += "|"
        return msg

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """Lists the queue."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

        queue_list = 'Nothing queued' if not player.queue else ''
        for track in player.queue:
            queue_list += f'[**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Queue', description=queue_list)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def disconnect(self, ctx):
        """Disconnect from the voice channel."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        await player.disconnect()

    async def on_voice_server_update(self, data):
        self.state_keys.update({
            'op': 'voiceUpdate',
            'guildId': data.get('guild_id'),
            'event': data
        })

        await self.verify_and_dispatch()

    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            self.state_keys.update({'sessionId': after.session_id})

        await self.verify_and_dispatch()

    async def verify_and_dispatch(self):
        if all(k in self.state_keys for k in self.validator):
            await self.lavalink.dispatch_voice_update(self.state_keys)
            self.state_keys.clear()

