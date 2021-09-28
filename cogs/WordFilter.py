
from discord.ext.commands.errors import BadColorArgument
import requests
from discord.ext import commands
from requests.api import request

from database import words
import json
import ai_math
import discord
import re

regex = re.compile(" +|\\n+", flags=re.DOTALL|re.IGNORECASE|re.MULTILINE)


class WordFilter(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot

    self.bad_words = ["bitch", "cock", "dick", 'penis']

  async def db_find_similar(self, word: str):
    matches = words.find({ "similar": { "$in": [word] } })

  async def jaro_wink(self, str1: str, str2: str):
    return ai_math.jaro_Winkler(str1, str2)

  async def get_similar_spelled_words(self, word: str) -> list[str]:
    res = requests.get(f'https://api.datamuse.com/words?sp={word}')
    return [i['word'] for i in res.json()]

  async def get_similar_sounding_words(self, word: str) -> list[str]:
    res = requests.get(f"https://api.datamuse.com/words?sl={word}")
    return [i['word'] for i in res.json()]


  @commands.Cog.listener("on_message")
  async def on_message(self, message: discord.Message):
    words = regex.split(message.content)

    marks = []

    for word in words:
      sl = await self.get_similar_sounding_words(word)
      sp = await self.get_similar_spelled_words(word)
      for i in sl:
        if i in self.bad_words:
          if message is not None:
            await message.delete()
            marks.append(f"sl {i}")
      for i in sp:
        if i in self.bad_words:
          if message is not None:
            await message.delete()
            marks.append(f"sp {i}")

    txt = f'Detected:\n {",".join(marks)}'

    if len(txt) > 0:
      await message.channel.send(
        content=txt
      )



  @commands.group()
  async def blacklist(self, ctx: commands.Context):
    pass

  @blacklist.command()
  async def add(self, ctx: commands.Context, *, phrase: str):
    print(phrase)

  @blacklist.command
  async def remove(self, ctx: commands.Context, *, phrase: str):
    print(phrase)

  @commands.group()
  async def whitelist(self, ctx: commands.Context):
    pass

  @whitelist.command()
  async def add(self, ctx: commands.Context, *, phrase: str):
    print(phrase)

  @whitelist.command()
  async def remove(self, ctx: commands.Context, *, phrase: str):
    print(phrase)




def setup(bot):
  bot.add_cog(WordFilter(bot))

