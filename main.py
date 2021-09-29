from dotenv import load_dotenv
import os
from discord_components import DiscordComponents, ComponentsBot

load_dotenv()
from discord.ext import commands
import discord


class Bot(ComponentsBot, commands.Bot):
  def __init__(self, command_prefix, help_command=commands.DefaultHelpCommand(), description=None, **options):
    super(Bot, self).__init__(command_prefix, help_command=help_command, description=description, **options)

    self.color = discord.Color.from_rgb(221, 69, 245)




prefix = commands.when_mentioned_or('.')

bot = Bot(command_prefix=prefix)

@bot.event
async def on_ready():
  print(f"{bot.user} has logged in !")

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


bot.run(os.getenv("TOKEN"))


