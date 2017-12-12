import asyncio
import discord
import math
from discord.ext import commands
from lavalink import lavalink


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.lavalink = lavalink.Client(bot=bot, password='youshallnotpass', loop=self.bot.loop)

        self.state_keys = {}
        self.validator = ['op', 'guildId', 'sessionId', 'event']

    @commands.command()
    async def audiostats(self, ctx):
        """Audio stats."""
        servers = await self._get_playing()
        await self._embed_msg(ctx, f'Playing music in {servers} servers.')

    @commands.command(name="clear")
    async def queueclear(self, ctx):
        """Clears the queue."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        player.queue = []
        await self._embed_msg(ctx, "Queue cleared.")

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """Disconnect from the voice channel."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        await player.disconnect()

    @commands.command(aliases=['np', 'n', 'song'])
    async def now(self, ctx):
        """Now playing."""
        expected = ["⏮", "⏹", "⏸", "▶", "⏭"]
        emoji = {
            "back": "⏮",
            "stop": "⏹",
            "pause": "⏸",
            "play": "▶",
            "next": "⏭"
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
            req_user = self.bot.get_user(player.current.requester)
            song = f'**[{player.current.title}]({player.current.uri})**\nReqested by: **{req_user}**\n{arrow}\n({pos}/{dur})'

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
            if player.paused:
                await ctx.invoke(self.pause)
        elif react == "next":
            await self._clear_react(message)
            await ctx.invoke(self.skip)

    @commands.command(aliases=["resume"])
    async def pause(self, ctx):
        """Pause and resume."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to pause the music.")

        if not player.is_playing():
            return
        if player.paused:
            await player.set_paused(False)
            await self._embed_msg(ctx, "Music resumed.")
        else:
            await player.set_paused(True)
            await self._embed_msg(ctx, "Music paused.")

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        """Play a URL or search for a song."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to use the play command.")
        if not player.is_connected():
            await player.connect(channel_id=ctx.author.voice.channel.id)
        query = query.strip('<>')
        if not query.startswith('http'):
            query = f'ytsearch:{query}'
        tracks = await self.lavalink.get_tracks(query)
        if not tracks:
            return await self._embed_msg(ctx, "Nothing found 👀")
        if 'list' in query and 'ytsearch:' not in query:
            for track in tracks:
                await player.add(requester=ctx.author.id, track=track, play=True)
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                                  title="Playlist Enqueued!",
                                  description=f"Added {len(tracks)} tracks to the queue.")
        else:
            await player.add(requester=ctx.author.id, track=tracks[0], play=True)
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                                  title="Track Enqueued",
                                  description=f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})')
        await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int=None):
        """Lists the queue."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not player.queue:
            return await self._embed_msg(ctx, "There\'s nothing in the queue!")

        if player.current is None:
            return await self._embed_msg(ctx, "The player is stopped.")

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        page = lavalink.Utils.get_number(page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''

        for i, track in enumerate(player.queue[start:end], start=start):
            req_user = self.bot.get_user(track.requester)
            queue_list += f'`{i + 1}.` [**{track.title}**]({track.uri}), requested by **{req_user}**\n'

        pos = player.position
        dur = player.current.duration
        remain = dur - pos
        time = lavalink.Utils.format_time(remain)
        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Queue for ' + ctx.guild.name, description=queue_list)

        if player.current.stream:
            embed.set_footer(text=f'Page {page}/{pages} | {len(player.queue)} tracks | Currently livestreaming {player.current.title}')
            await ctx.send(embed=embed)
        else:
            embed.set_footer(text=f'Page {page}/{pages} | {len(player.queue)} tracks | {time} left on {player.current.title}')
            await ctx.send(embed=embed)

    @commands.command()
    async def repeat(self, ctx):
        """Toggles repeat."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to toggle shuffle.")

        if not player.is_playing():
            return await self._embed_msg(ctx, "Nothing playing.")

        player.repeat = not player.repeat

        title = ('Repeat ' + ('enabled!' if player.repeat else 'disabled.'))
        return await self._embed_msg(ctx, title)

    @commands.command()
    async def search(self, ctx, *, query):
        """Pick a song with a search."""
        expected = ["1⃣", "2⃣", "3⃣"]
        emoji = {
            "one": "1⃣",
            "two": "2⃣",
            "three": "3⃣"
        }
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to enqueue songs.")
        if not player.is_connected():
            await player.connect(channel_id=ctx.author.voice.channel.id)
        query = query.strip('<>')
        if not query.startswith('http'):
            query = f'ytsearch:{query}'
        tracks = await self.lavalink.get_tracks(query)
        if not tracks:
            return await self._embed_msg(ctx, "Nothing found 👀")
        if 'list' not in query and 'ytsearch:' in query:
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                                  title="Tracks Found:",
                                  description=f'1. [{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})\n2. [{tracks[1]["info"]["title"]}]({tracks[1]["info"]["uri"]})\n3. [{tracks[2]["info"]["title"]}]({tracks[2]["info"]["uri"]})')
            message = await ctx.send(embed=embed)

            def check(r, u):
                return r.message.id == message.id and u == ctx.message.author
            for i in range(3):
                await message.add_reaction(expected[i])
            try:
                (r, u) = await self.bot.wait_for('reaction_add', check=check, timeout=10.0)
            except asyncio.TimeoutError:
                await self._clear_react(message)
                return
            reacts = {v: k for k, v in emoji.items()}
            react = reacts[r.emoji]
            if react == "one":
                await self._clear_react(message)
                await player.add(requester=ctx.author.id, track=tracks[0], play=True)
                embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                                      title="Track Enqueued",
                                      description=f'[{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]})')
                await ctx.send(embed=embed)
            elif react == "two":
                await self._clear_react(message)
                await player.add(requester=ctx.author.id, track=tracks[1], play=True)
                embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                                      title="Track Enqueued",
                                      description=f'[{tracks[1]["info"]["title"]}]({tracks[1]["info"]["uri"]})')
                await ctx.send(embed=embed)
            elif react == "three":
                await self._clear_react(message)
                await player.add(requester=ctx.author.id, track=tracks[2], play=True)
                embed = discord.Embed(colour=ctx.guild.me.top_role.colour,
                                      title="Track Enqueued",
                                      description=f'[{tracks[2]["info"]["title"]}]({tracks[2]["info"]["uri"]})')
                await ctx.send(embed=embed)
        else:
            for track in tracks:
                await player.add(requester=ctx.author.id, track=track, play=True)

            songembed = discord.Embed(colour=ctx.guild.me.top_role.colour, title=f"Queued {len(tracks)} track(s).")
            message = await ctx.send(embed=songembed)

    @commands.command()
    async def shuffle(self, ctx):
        """Toggles shuffle."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to toggle shuffle.")

        if not player.is_playing():
            return await self._embed_msg(ctx, "Nothing playing.")

        player.shuffle = not player.shuffle

        title = ('Shuffle ' + ('enabled!' if player.shuffle else 'disabled.'))
        return await self._embed_msg(ctx, title)

    @commands.command(aliases=['forceskip', 'fs'])
    async def skip(self, ctx):
        """Skips to the next track."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)

        if player.current is None:
            return await self._embed_msg(ctx, "The player is stopped.")

        if not player.queue:
            pos = player.position
            dur = player.current.duration
            remain = dur - pos
            time = lavalink.Utils.format_time(remain)
            if player.current.stream:
                embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='There\'s nothing in the queue!')
                embed.set_footer(text=f'Currently livestreaming {player.current.title}')
                return await ctx.send(embed=embed)
            elif player.current.track:
                embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='There\'s nothing in the queue!')
                embed.set_footer(text=f'{time} left on {player.current.title}')
                return await ctx.send(embed=embed)
            else:
                return await self._embed_msg(ctx, "There\'s nothing in the queue!")

        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to skip the music.")

        await player.skip()
        if player.current:
            song = f'**[{player.current.title}]({player.current.uri})**'
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title='Now Playing', description=song)
            await ctx.send(embed=embed)

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        """Stops playback."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to stop the music.")
        if player.is_playing():
            await self._embed_msg(ctx, "Stopping...")
            await player.stop()

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, volume=None):
        """Sets the volume, 1 - 100."""
        player = await self.lavalink.get_player(guild_id=ctx.guild.id)
        if not ctx.author.voice or (player.is_connected() and ctx.author.voice.channel.id != int(player.channel_id)):
            return await self._embed_msg(ctx, "You must be in the voice channel to change the volume.")
        if not volume:
            vol = player.volume
            embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title="Volume: ", description=str(vol) + "%")
            return await ctx.send(embed=embed)
        if not player.is_playing():
            return await self._embed_msg(ctx, "Nothing playing.")
        if not lavalink.Utils.is_number(volume):
            return await self._embed_msg(ctx, "You didn\'t specify a valid number!")
        if int(volume) > 100:
            volume = 100
            await player.set_volume(int(volume))
        else:
            await player.set_volume(int(volume))
        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title="Volume:", description=str(volume) + "%")
        await ctx.send(embed=embed)

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
        loc_time = round((pos / dur) * sections)
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

    async def _embed_msg(self, ctx, title):
        embed = discord.Embed(colour=ctx.guild.me.top_role.colour, title=title)
        await ctx.send(embed=embed)

    async def _get_playing(self):
        return len([p for p in self.bot.players.values() if p.is_playing()])

    async def on_voice_server_update(self, data):
        self.state_keys.update({
            'op': 'voiceUpdate',
            'guildId': data.get('guild_id'),
            'event': data
        })

        await self.verify_and_dispatch()

    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        await self.lavalink._update_voice(guild_id=member.guild.id, channel_id=after.channel.id)

        self.state_keys.update({'sessionId': after.session_id})
        await self.verify_and_dispatch()

    async def verify_and_dispatch(self):
        if all(k in self.state_keys for k in self.validator):
            await self.lavalink.send(**self.state_keys)
            self.state_keys.clear()
