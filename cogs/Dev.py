from pycord.discord.ext import commands
import pycord.discord as discord
from pycord.discord.ext.commands.errors import (
  ExtensionAlreadyLoaded,
  ExtensionError,
  ExtensionNotLoaded,
  ExtensionNotFound,
  ExtensionFailed
)
import asyncio
import os
from discord_components import Interaction, Select, SelectOption

devs = [635959963134459904, 827749968848355338]

async def is_dev(m: discord.Message):
    return m.author.id in devs

class Dev(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot

  async def send_confirm(self, ctx):
    msg = await ctx.send('done')
    await asyncio.sleep(5)
    await msg.delete()

  @commands.command()
  @commands.check(is_dev)
  async def cmd(self, ctx, *, input_):
    os.system(input_)

  async def reload_extension(self, ctx: commands.Context, extension: str):
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

  async def load_extension(self, ctx: commands.Context, extension: str):
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

  async def unload_extension(self, ctx: commands.Context, extension: str):
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
  async def cog(self, ctx: commands.Context):
    pass

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def load(self, ctx: commands.Context, *, extension: str):
    await self.load_extension(ctx, extension)
    await self.send_confirm(ctx)

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def unload(self, ctx: commands.Context, *, extension: str):
    await self.unload_extension(ctx, extension)
    await self.send_confirm(ctx)

  @cog.command(help="Dev Only", hidden=True)
  @commands.check(is_dev)
  async def reload(self, ctx: commands.Context, *, extension: str):
    await self.unload_extension(ctx, extension)
    await self.load_extension(ctx, extension)
    await self.send_confirm(ctx)

  @property
  def cog_files(self):
    return [
      (f"cogs.{filename[:-3]}", filename, filename[:-3]) for filename in os.listdir(".")
      if filename.endswith('.py')
    ]

  def cog_file_options(self, type: str):
    options = []
    for ext, filename, name in self.cog_files:
      options.append(
        dict(
          label=name,
          description=f"{type}: {name}",
          value=f"{type} {ext}"
        )
      )
    return options

  @commands.command()
  async def cogs(self, ctx: commands.Context):

    menu = Select(
      options=[
        SelectOption(
          label="reload",
          value="reload",
          description="open reload cog menu"
        ),
        SelectOption(
          label="load",
          value="load",
          description="open load cog menu"
        ),
        SelectOption(
          label="unload",
          value="unload",
          description="open unload cog menu"
        )
      ],
      id="cog menu",
      placeholder="Choose An Extension Menu"
    )
    

    await ctx.send(
      content="no Content",
      components=[menu]
    )

  @commands.Cog.listener("on_select_option")
  async def on_button_click(self, interaction: Interaction):
    comp = interaction.component
    print(comp)
    data = comp.to_dict()
    id: str = data.get('id')
    category, command = id.split(" ")
    option = interaction.values[0]
    
    if category == 'cog':
      if command == 'menu':
        if option == 'reload':
          opts = self.cog_file_options("reload")

          embed = discord.Embed(title=option,color=self.bot.color)

          await interaction.respond(
            embeds=[embed],
            components=[
              Select(
                options=opts,
                id=f"cog {option}"
              )
            ]
          )

        elif option == 'load':
          opts = self.cog_file_options("load")
          
          embed = discord.Embed(title=option,color=self.bot.color)

          await interaction.respond(
            embeds=[embed],
            components=[
              Select(
                options=opts,
                id=f"cog {option}"
              )
            ]
          )
        elif option == 'unload':
          opts = self.cog_file_options("unload")
          
          embed = discord.Embed(title=option,color=self.bot.color)

          await interaction.respond(
            embeds=[embed],
            components=[
              Select(
                options=opts,
                id=f"cog {option}"
              )
            ]
          )

def setup(bot):
  bot.add_cog(Dev(bot))
