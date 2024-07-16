import asyncio
import discord
from discord.ext import commands
from json import load
#from time import time
from os import listdir, environ
from pathlib import Path

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
db = {}

#create the bot
bot = commands.Bot(command_prefix='.', description="A general-purpose discord bot for Horai by Delta", intents=intents)

def is_dev(ctx):
    async def predicate(ctx):
        return bool(ctx.author.id in [425748749462274048])
    return bot.check(predicate)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}.'.format(bot))
    #await bot.tree.sync()


async def load_exts():
    for file in listdir(f'./cogs'):
        #for each cog file, load it's commands into the bot
        if file=="modUtils.py":
            pass
        if file.endswith('.py'):
            print(f"Trying to load {file}")
            await bot.load_extension(f'cogs.{file[:-3]}')

async def main():
    async with bot:
        await load_exts()
        await bot.start(token)

#if program run as the main file instead of imported
if __name__ == "__main__":
    try:
        if Path("secrets.json").exists():
            with open("secrets.json","r") as f:
                #load the secret from JSON
                token = load(f)["TOKEN"] or ""
        else:
            #try to get tokens from env vars
            token = environ.get("TOKEN", "")

        if token == "":
            raise Exception("TOKEN not found in secrets.json or environment vars.")
        
        #run the bot
        asyncio.run(main())
    
    except discord.HTTPException as e:
        if e.status == 429:
            print("The Discord servers denied the connection for making too many requests")
        else:
            raise e
