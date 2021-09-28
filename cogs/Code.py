
from pycord.discord.ext import commands
import pycord.discord as discord
from pycord.discord import Embed
import pysourcebin as sbin
from discord_components import Button, ButtonStyle, Interaction, interaction
import re
import io

regex = re.compile("```[a-z]*\\n([\s\S]*?)\\n```", flags= re.IGNORECASE|re.DOTALL|re.MULTILINE)

sbin_url = re.compile("https:\/\/sourceb\.in\/?[^ \/]+?|http:\/\/srcb\.in\/")

class Code(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot

  def read(self, url):
    return sbin.read_url(url)

  async def create_sbin(self, name: str, txt: str):
    url = sbin.create(name, txt)
    return url

  @commands.Cog.listener("on_button_click")
  async def on_button_click(self, interaction: Interaction):
    data = interaction.component.to_dict()
    custom_id: str = data['custom_id']
    category, command = custom_id.split(" ")

    if category == 'sourcebin':
      if command == 'create':
        if interaction.responded is False:
          msg: discord.Message = await interaction.channel.fetch_message(interaction.message.reference.message_id)
          codes = regex.findall(msg.content)

          print(codes)

          if codes is None:
            await interaction.respond(content="Could Not pull code from message")
            return
          txt = ''
          for code in codes:
            txt += code

          url = await self.create_sbin(f"{self.bot.user}'s Code", txt)

          embed = Embed(
            title="__**Sourcebin**__",
            url= url,
            color=self.bot.color,
            description="> Here You Go I've Gone Ahead And Bundled it up in A SourceBin"
          ).set_footer(icon_url=self.bot.user.avatar_url, text="Powered By: http://srcb.in")

          await interaction.respond(
            embeds=[embed],
            ephemeral=False
          )


  @commands.Cog.listener("on_message")
  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return
    codes = regex.findall(message.content)
    if len(codes) > 0:
      await message.reply(
        content="Would You Like to make this a sourcebin?",
        components=[
          Button(
            style=ButtonStyle.green,
            label="Yes",
            id="sourcebin create"
          )
        ]
      )

  @commands.group(name="sourcebin")
  async def sourcebin(self, ctx: commands.Command):
    pass

  @sourcebin.command(name="read", help="read's the sourcebin for you")
  async def read(self, ctx: commands.Context, *, url: str):

    if sbin_url.match(url) is None:
      await ctx.send(content="Invalid SourceBin URL")
    else:
      data = sbin.read_url(url)
      codes = data['code']
      txt = ''

      for c in codes:
        txt += c

      if len(txt) > 2000:
        txt = txt[:1990] + '...'

      embed = Embed(
        title="Sourcbin Contents",
        description=f"```\n{txt}\n```",
        color=self.bot.color
      )

      file = discord.File(fp=io.BytesIO(str.encode(txt)), filename="Code As File.txt")

      await ctx.send(embed=embed, file=file)

def setup(bot):
  bot.add_cog(Code(bot))
