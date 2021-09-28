from discord.ext import commands
from dotenv import load_dotenv
import os
import discord
from discord_components import DiscordComponents

load_dotenv()


class Bot(commands.Bot):
  def __init__(self, command_prefix, help_command=commands.DefaultHelpCommand(), description=None, **options):
    super().__init__(command_prefix, help_command=help_command, description=description, **options)

    self.color = discord.Color.from_rgb(221, 69, 245)
    DiscordComponents(self)




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
  bot.load_extension(cog)
print("done registering")


bot.run(os.getenv("TOKEN"))


