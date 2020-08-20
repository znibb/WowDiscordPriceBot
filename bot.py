import os
from discord.ext import commands

# Command prefix
bot = commands.Bot(command_prefix='-', case_insensitive=True)

# Load environment parameters
token = os.getenv("DISCORD_TOKEN")

# Bot joins
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Command error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Error: Missing argument. Try !help.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Error: Unknown command. Try !help.")
    else:
        await ctx.send("Error: Unknown error. Check server logs for more info.")
        raise error

# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
