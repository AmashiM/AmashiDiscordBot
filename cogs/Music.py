import collections
import gc
from collections import namedtuple
from random import choice, shuffle
from typing import AsyncContextManager

import discord
from discord.ext.music.voice_source.legacy import MusicSource
import py_youtube as yti
import youtube_dl
from database import queues
from discord.ext import commands, music
import discord
from discord.ext.music import (
  MusicClient, Track, LibAVAudio,
  LibAVOpusAudio, IllegalSeek,
  NoMoreSongs
)
from database import queues
import gc

from src.Bot import Bot

class Song:
  def __init__(self, **kwargs):
    self.title: str = None
    self.url: str = None
    self.user_id: str = None
    self.placement: int = 0

  def to_dict(self) -> dict:
    val = {}
    needs = ["title", 'url', 'user_id', 'placement']
    for key in needs:
      val[key] = getattr(self, key)
    return val

class Queue:
  def __init__(self, guild_id: int):
    self.guild_id: int = guild_id

    queue = queues.find_one(self.query)
    if not queue:
      queues.insert_one({
        "guild_id": guild_id,
        "songs": [],
        "loop": False,
        "current": []
      })

  @property
  def query(self):
    return { "guild_id": self.guild_id }

  async def get(self):
    return queues.find_one(self.query)


class QueueManager:
  def get(self, guild_id: int) -> Queue:
    return Queue(guild_id)


class AmashiMusic(commands.Cog):
  def __init__(self, bot):
    self.bot: Bot = bot
    self.clients: list[MusicClient] = []
    self.youtube = youtube_dl.YoutubeDL({'format': 'best'})
    self.queues = QueueManager()
    self.connect_options = { "reconnect": True, "timeout": 15.0 }

    self.FFMPEG_OPTIONS = {
      "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
      "options": '-vn'
    }


  async def search_yt(self, query: str, limit=15):
    yt = yti.Search(query, limit)
    return yt.videos()


  async def create_client(self, channel: discord.VoiceChannel) -> MusicClient:
    client = MusicClient(self.bot, channel)
    self.clients.append(client)
    return client

  async def get_client(self, guild_id: int):
    return discord.utils.find(lambda client: client.guild.id == guild_id, self.clients)

  @commands.command(
    name="join"
  )
  @commands.guild_only()
  async def join(self, ctx: commands.Context):
    if ctx.author.voice is None:
      await ctx.send("you need to be in a voice channel")
    else:
      vc: discord.VoiceChannel = ctx.author.voice.channel
      if ctx.voice_client is None:
        client = await self.create_client(vc)
        await client.connect(reconnect=True)
      else:
        await ctx.voice_client.move_to(vc)


  @commands.command(
    name="leave"
  )
  @commands.guild_only()
  async def leave(self, ctx: commands.Context):
    if ctx.voice_client is not None:
      await ctx.voice_client.disconnect()

  @commands.command(
    name="play"
  )
  @commands.guild_only()
  async def play(self, ctx: commands.Context, *, query: str):
    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)

    # We're failed to connect to voice channel
    if not music_client:
        return
    print("music client exists")

    # Set announcer
    music_client.register_after_callback(self.bot.announce_next_song)
    print('registered')

    # Get stream url (if success)
    success, info, stream_url = await self.bot.get_stream_url(query)
    if not success:
        return await ctx.send('`%s` cannot be found' % query)

    # Create track
    track = Track(
        LibAVOpusAudio(stream_url),
        info['title'],
        info['webpage_url'],
        info['url'],
        info['thumbnail'],
        channel=ctx.channel, # Text channel for annouce the next song
        user_id=ctx.message.author.id # User that request this song
    )

    # Normally when you call MusicClient.play() it automatically add to playlist
    # even it still playing songs
    # So we need to check if MusicClient is still playing or not
    # to tell the user that this song will be put in queue
    if music_client.is_playing():
        embed = discord.Embed()
        embed.set_thumbnail(url=info['thumbnail'])
        embed.add_field(name='Added to queue', value='[%s](%s) [<@!%s>]' % (
            info['title'],
            info['webpage_url'],
            ctx.message.author.id
        ))
        await ctx.send(embed=embed)
        await music_client.play(track)
        return

    # Play the music !!
    await music_client.play(track)

    # Sending message that we're playing song
    embed = discord.Embed()
    embed.set_thumbnail(url=info['thumbnail'])
    embed.add_field(name='Now Playing', value='[%s](%s) [<@!%s>]' % (
        info['title'],
        info['webpage_url'],
        ctx.message.author.id
    ))
    await ctx.send(embed=embed)

  @commands.command(
    name="pause"
  )
  @commands.guild_only()
  async def pause(self, ctx: commands.Context):
    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)

    # We're failed to connect to voice channel
    if not music_client:
        return

    # Check if we're playing or not
    # If not, tell user that bot is not playing anything
    if not music_client.is_playing():
        return await ctx.send(f'{self.bot.user.name} not playing audio')

    # Pause the music
    await music_client.pause()
    await ctx.send('Paused')

  @commands.command(
    name="resume"
  )
  @commands.guild_only()
  async def resume(self, ctx: commands.Context):
    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)

    # We're failed to connect to voice channel
    if not music_client:
        return

    # Check if we're playing or not
    # If yes, tell user that bot is already playing audio
    if music_client.is_playing():
        return await ctx.send(f'{self.bot.user.name} already playing audio')

    # Check that we're not paused
    if not music_client.is_paused():
        return await ctx.send(f'{self.bot.user.name} is not in paused state')

    # Resume the music
    await music_client.resume()
    await ctx.send('Resumed')

  @commands.command(
    name="stop"
  )
  @commands.guild_only()
  async def stop(self, ctx):
    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)

    # We're failed to connect to voice channel
    if not music_client:
        return

    # Check if we're playing or not
    # If not, tell user that bot is not playing anything
    if not music_client.is_playing():
        return await ctx.send(f'{self.bot.user.name} not playing audio')

    # Stop the music
    await music_client.stop()
    await ctx.send('Stopped')

  @commands.command(
    name="volume",
    help="default is 1"
  )
  async def volume(self, ctx: commands.Context, volume: float = 1):
    music_client = await self.bot.get_music_client(ctx)
    source: MusicSource = music_client.source
    source.set_volume(volume)

  @commands.command()
  async def seek(self, ctx: commands.Context, _num):
    # Check given number is valid number
    try:
        number = float(_num)
    except ValueError:
        # Not a number
        return await ctx.send('Not a number')

    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)

    # We're failed to connect to voice channel
    if not music_client:
        return

    # Check if we're playing or not
    # If not, tell user that bot is not playing anything
    if not music_client.is_playing():
        return await ctx.send(f'{self.bot.user.name} not playing audio')

    # Check that we're paused
    if music_client.is_paused():
        return await ctx.send(f'{self.bot.user.name} is in paused state')

    # Begin seeking process
    try:
        await music_client.seek(number)
    except IllegalSeek:
        # Current stream does not support seeking
        await ctx.send('Current playing audio does not support seeking')
    else:
        await ctx.send('Jumped forward to %s seconds' % number)

  @commands.command()
  async def skip(self, ctx: commands.Context):
    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)


    # We're failed to connect to voice channel
    if not music_client:
        return

    # Skip to next song
    try:
        await music_client.next_track()
    except NoMoreSongs:
        # Playlist has reached at the end
        await ctx.send('There is no more next songs in playlist')
    else:
        track = music_client.track
        embed = discord.Embed()
        embed.set_thumbnail(url=track.thumbnail)
        embed.add_field(name='Now Playing', value='[%s](%s) [<@!%s>]' % (
            track.name,
            track.url,
            ctx.message.author.id
        ))
        await ctx.send(embed=embed)

  @commands.command()
  async def back(self, ctx: commands.Context):
    # Retrieve music client
    music_client = await self.bot.get_music_client(ctx)

    # We're failed to connect to voice channel
    if not music_client:
        return

    # Skip to next song
    try:
        await music_client.previous_track()
    except NoMoreSongs:
        # Playlist has reached at the end
        await ctx.send('There is no more next songs in playlist')
    else:
        track = music_client.track
        embed = discord.Embed()
        embed.set_thumbnail(url=track.thumbnail)
        embed.add_field(name='Now Playing', value='[%s](%s) [<@!%s>]' % (
            track.name,
            track.url,
            ctx.message.author.id
        ))
        await ctx.send(embed=embed)


  @commands.Cog.listener("on_connect")
  async def on_connect(self):
    # Create new session on AsyncYoutubeSearch
    await self.bot.youtube_search_session.new_session()



def setup(bot):
  bot.add_cog(AmashiMusic(bot))
