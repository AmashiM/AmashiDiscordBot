from discord.ext import commands
import requests
from discord import Embed

class Fun(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def get_insult(self):
    res = requests.get("https://evilinsult.com//generate_insult.php")
    return res.text

  @commands.command()
  async def insult(self, ctx: commands.Context):
    insult = await self.get_insult()

    embed = Embed(
      title="Insult",
      color=self.bot.color,
      description=f"> {insult}"
    )
    await ctx.send(
      embed=embed
    )






def setup(bot):
  bot.add_cog(Fun(bot))
