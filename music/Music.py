import asyncio
import discord
from discord.ext import commands
from . import lavalink


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.lavalink = lavalink.Client(bot=bot, password='youshallnotpass', loop=self.bot.loop)

        self.state_keys = {}
        self.validator = ['op', 'guildId', 'sessionId', 'event']

    async def _stopping(self, ctx):
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        """Play a URL or search for a song."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

        if not player.is_connected():
            await player.connect(channel_id=ctx.author.voice.channel.id)

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        tracks = await self.lavalink.get_tracks(query)
        if not tracks:
            return await ctx.send('Nothing found ??')

        await player.add(requester=ctx.author.id, track=tracks[0], play=True)

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                              title="Track Enqueued",
                              description=f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})')
        await ctx.send(embed=embed)

    @commands.command(aliases=["resume"])
    async def pause(self, ctx):
        """Pause and resume."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

        if not player.is_playing():
            return
        if player.paused:
            await player.set_paused(False)
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title="Music resumed.")
            await ctx.send(embed=embed)
        else:
            await player.set_paused(True)
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title="Music paused.")
            await ctx.send(embed=embed)

    @commands.command(aliases=['forceskip', 'fs'])
    async def skip(self, ctx):
        """Skips to the next track."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        await player.skip()

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        """Stops playback."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if player.is_playing():
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title="Stopping...")
            await ctx.send(embed=embed)
            await player.stop()
        else:
            pass

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, volume):
        """Sets the volume, 1 - 100."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

        if not player.is_playing():
            return

        if not lavalink.Utils.is_number(volume):
            return await ctx.send('You didn\'t specify a valid number!')

        await player.set_volume(int(volume))
        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title="Volume:", description=volume)
        await ctx.send(embed=embed)

    @commands.command(aliases=['np', 'n', 'song'])
    async def now(self, ctx):
        """Now playing."""
        expected = ["?", "?", "?", "?", "?"]
        emoji = {
            "back": "?",
            "stop": "?",
            "pause": "?",
            "play": "?",
            "next": "?"
        }
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        song = 'Nothing'
        if player.current:
            arrow = await self._draw_time(ctx)
            pos = lavalink.Utils.format_time(player.position)
            if player.current.stream:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
        if not player.current:
            song = f'Nothing.'
        else:
            song = f'**[{player.current.title}]({player.current.uri})**\n{arrow}\n({pos}/{dur})'

        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Now Playing', description=song)
        message = await ctx.send(embed=embed)

        def check(r, u):
            return r.message.id == message.id and u == ctx.message.author

        if player.current:
            for i in range(5):
                await message.add_reaction(expected[i])
        try:
            (r, u) = await self.bot.wait_for('reaction_add', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await self._clear_react(message)
            return

        reacts = {v: k for k, v in emoji.items()}
        react = reacts[r.emoji]

        if react == "back":
            await self._clear_react(message)
            pass
        elif react == "stop":
            await self._clear_react(message)
            await ctx.invoke(self.stop)
        elif react == "pause":
            await self._clear_react(message)
            await ctx.invoke(self.pause)
        elif react == "play":
            await self._clear_react(message)
            await ctx.invoke(self.resume)
        elif react == "next":
            await self._clear_react(message)
            await ctx.invoke(self.skip)
        
    async def _clear_react(self, message):
        try:
            await message.clear_reactions()
        except:
            return

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

    @commands.command(aliases=['dc'])
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
