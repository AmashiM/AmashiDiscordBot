from custom_pycord.discord.ext import commands
import custom_pycord.discord as discord
from custom_pycord.discord import Embed
import requests
import json

class Data(commands.Cog):
  def __init__(self, bot) -> None:
    self.bot: commands.Bot = bot

  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f"My Ping: {round(self.bot.latency * 1000)}ws")

  @commands.command()
  async def discordstatus(self, ctx):
    res = requests.get('https://discordstatus.com/metrics-display/5k2rt9f7pmny/day.json')
    data = json.loads(res.text)
    latency = round(data['summary']['mean'])

    embed = Embed(
      description=f"Current: {latency}",
    )

    await ctx.send(embed=embed)


def setup(bot):
  bot.add_cog(Data(bot))
