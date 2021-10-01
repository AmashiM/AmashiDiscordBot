

import asyncio
from discord.ext import commands
import discord
from youtube_search_requests import AsyncYoutubeSearch, AsyncYoutubeSession
import youtube_dl
from discord_components import DiscordComponents
from discord.ext.music import MusicClient, Track


class Bot(commands.Bot):
  def __init__(self, command_prefix, help_command=commands.MinimalHelpCommand(), description=None, **options):
    super(Bot, self).__init__(command_prefix, help_command=help_command, description=description, **options)

    DiscordComponents(self)
    self.youtube_search_session = AsyncYoutubeSession()
    self.youtube_search = AsyncYoutubeSearch(self.youtube_search_session)

    self.youtube = youtube_dl.YoutubeDL({
      'format': 'best'
    })

    if self.loop is None:
      self.loop = asyncio.get_event_loop()

    self.color = discord.Color.from_rgb(221, 69, 245)

    class MyHelpCommand(commands.MinimalHelpCommand):
      async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=self.bot.color, description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

    self.help_command = MyHelpCommand()


  def _get_stream_url(self, url: str):
    info = self.youtube.extract_info(url, download=False)
    return info, info['url']


  async def get_stream_url(self, query: str):
    # Check if query is valid url
    if query.startswith('https://') or query.startswith('http://'):
        info, stream_url = await self.loop.run_in_executor(None, lambda: self._get_stream_url(query))
        return True, info, stream_url
    results = await self.youtube_search.search_videos(query, max_results=1, timeout=3)
    if not results:
        return False, None, None
    result = results[0]
    info, stream_url = await self.loop.run_in_executor(None, lambda: self._get_stream_url(result['url']))
    return True, info, stream_url


  def get_voice_bot(self, guild: discord.Guild):
    """Get connected voice bot (if exist)"""
    for voice in self.voice_clients:
        if voice.guild.id == guild.id:
            return voice


  def check_voice_permissions(self, perms: discord.Permissions):
    """Check voice permissions"""
    words = ''
    if not perms.connect:
      words += 'Connect, '
    if not perms.speak:
      words += 'Speak'
    if not words:
      return True, None
    else:
      return False, words


  async def get_voice_user(self, ctx: commands.Context):
    """Get connected voice user"""
    # Get voice user
    voice_user = ctx.message.author.voice

    # If user is not connected to voice, throw error
    # To prevent users have playback controls outside voice channels
    if not voice_user:
      await ctx.send('You must connected to voice to use this command')
      return False

    # Get voice bot (if connected)
    voice_bot = self.get_voice_bot(voice_user.channel.guild)
    if voice_bot:

      # If bot is connected to voice channel but user connected to different voice channel
      # Throw error
      if voice_user.channel.id != voice_bot.channel.id:
          await ctx.send(f'{self.user.name} is being used in another voice channel')
          return False

      # Bot and user are connected to same voice channel and
      # We already connected to voice
      return voice_bot

    # Check bot permissions for connected user voice channel
    joinable, missing_perms = self.check_voice_permissions(voice_user.channel.permissions_for(ctx.me))

    # If not not enough permissions tell the user
    # That bot has not enough permissions
    if not joinable:
      await ctx.send(f'I don\'t have permissions `{missing_perms}` in <#{str(voice_user.id)}>')
      return False
    return voice_user.channel

  async def connect_music_client(self, ctx: commands.Context, channel: discord.VoiceChannel, timeout: int=60):
    """Connect to voice channel, return :class:`MusicClient`"""
    try:
      music_client = await channel.connect(timeout=timeout, cls=MusicClient)
    except asyncio.TimeoutError:
      # Failed to connect, Timeout occured
      await ctx.send(
        content=f'Failed to connect to <#{channel.id}> (Timeout)'
      )
      return False
    else:
      return music_client

  async def get_music_client(self, ctx: commands.Context) -> MusicClient:
    """Retrieve :class:`MusicClient`, create one if necessary"""
    # Retrieve voice channel that user connected to
    voice_user = await self.get_voice_user(ctx)

    if isinstance(voice_user, discord.VoiceChannel):
      # Initialize and connect MusicClient
      music_client = await self.connect_music_client(ctx, voice_user)
    else:
      # We already conencted to voice channel
      music_client = voice_user
    return music_client

  async def announce_next_song(err: Exception, track: Track):
    """Announce the next song"""
    # If playlist is reached the end of tracks
    # do nothing
    if not track:
      return

    channel = track.channel
    user_id = track.user_id

    # If error detected, tell the user that bot has trouble playing this song
    if err:
      embed = discord.Embed()
      embed.add_field(name='Failed to play song', value='[%s](%s) [<@!%s>]\nError: `%s`' % (
        track.name,
        track.url,
        user_id,
        str(err)
      ))

    # Send the announcer
    embed = discord.Embed()
    embed.set_thumbnail(url=track.thumbnail)
    embed.add_field(name='Now playing', value='[%s](%s) [<@!%s>]' % (
      track.name,
      track.url,
      user_id,
    ))
    await channel.send(embed=embed)
