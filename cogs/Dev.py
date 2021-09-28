from discord.ext import commands
from discord.ext.commands.bot import *
from discord.ext.commands.errors import *
import os
from discord import *

devs = [635959963134459904, 827749968848355338]

async def is_dev(m: Message):
    return m.author.id in devs

class Dev(Cog):
  def __init__(self, bot):
    self.bot: Bot = bot

  async def send_confirm(self, ctx):
    msg = await ctx.send('done')
    await asyncio.sleep(5)
    await msg.delete()

  @commands.command()
  @commands.check(is_dev)
  async def cmd(self, ctx, *, input_):
    os.system(input_)

  async def reload_extension(self, ctx: Context, extension: str):
    try:
      self.bot.reload_extension(name=extension)
    except ExtensionAlreadyLoaded as err:
      await ctx.send(f"ExtensionAlreadyLoaded: {err}")
    except ExtensionError as err:
      await ctx.send(f"ExtensionError: {err}")
    except ExtensionNotLoaded as err:
      await ctx.send(f"ExtensionNotLoaded: {err}")
    except ExtensionNotFound as err:
      await ctx.send(f"ExtensionNotFound: {err}")
    except ExtensionFailed as err:
      await ctx.send(f"ExtensionFailed: {err}")

  async def load_extension(self, ctx: Context, extension: str):
    try:
      self.bot.load_extension(name=extension)
    except ExtensionAlreadyLoaded as err:
      await ctx.send(f"ExtensionAlreadyLoaded: {err}")
    except ExtensionError as err:
      await ctx.send(f"ExtensionError: {err}")
    except ExtensionNotLoaded as err:
      await ctx.send(f"ExtensionNotLoaded: {err}")
    except ExtensionNotFound as err:
      await ctx.send(f"ExtensionNotFound: {err}")
    except ExtensionFailed as err:
      await ctx.send(f"ExtensionFailed: {err}")

  async def unload_extension(self, ctx: Context, extension: str):
    try:
      self.bot.unload_extension(name=extension)
    except ExtensionAlreadyLoaded as err:
      await ctx.send(f"ExtensionAlreadyLoaded: {err}")
    except ExtensionError as err:
      await ctx.send(f"ExtensionError: {err}")
    except ExtensionNotLoaded as err:
      await ctx.send(f"ExtensionNotLoaded: {err}")
    except ExtensionNotFound as err:
      await ctx.send(f"ExtensionNotFound: {err}")
    except ExtensionFailed as err:
      await ctx.send(f"ExtensionFailed: {err}")

  @commands.group()
  async def cog(self, ctx):
    pass

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def load(self, ctx, *, extension: str):
    await self.load_extension(ctx, extension)
    await self.send_confirm(ctx)

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def unload(self, ctx, *, extension: str):
    await self.unload_extension(ctx, extension)
    await self.send_confirm(ctx)

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def reload(self, ctx, *, extension: str):
    await self.unload_extension(ctx, extension)
    await self.load_extension(ctx, extension)
    await self.send_confirm(ctx)

def setup(bot):
  bot.add_cog(Dev(bot))
