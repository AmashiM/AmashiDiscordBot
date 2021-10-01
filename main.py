from dotenv import load_dotenv
import os
from discord_components import DiscordComponents, ComponentsBot
from discord.ext import commands
import discord
load_dotenv()
import gc

ans = None
while ans is None:
  val = input("testing? (y/n)")
  if val not in ['y','n']:
    continue
  else:
    ans = val

token = os.getenv("TOKEN")

if ans == 'y':
  token = os.getenv("TEST_TOKEN")

from src.Bot import Bot




prefix = commands.when_mentioned_or('.')

bot = Bot(command_prefix=prefix)

@bot.event
async def on_ready():
  print(f"{bot.user} has logged in !")

  if ans == 'n':
    from app import keep_alive
    keep_alive()
    del keep_alive

cogs = [
  f"cogs.{file[:-3]}" for file in os.listdir("./cogs/")
  if file.endswith('.py')
]

for cog in cogs:
  print(f"registering cog: {cog}")
  try:
    bot.load_extension(cog)
  except Exception as err:
    print(err)
print("done registering")


bot.run(token)


