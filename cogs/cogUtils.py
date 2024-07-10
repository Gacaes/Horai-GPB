from discord.ext import commands
from discord import Interaction, app_commands, interactions
from os import listdir
from copy import deepcopy
from pathlib import Path
from json import load

perma_cog_files = set([i for i in listdir("./cogs") if i.endswith('.py')])
perma_cog_files.discard("cogUtils.py")
perma_cog_files.discard("MainCommands.py")
current_cog_files = deepcopy(perma_cog_files)

with open("secrets.json","r") as f:
    loaded = load(f)
    dev = loaded["dev_id"] or ""
    dev_guild = loaded["dev_guild_id"]


def is_dev(itxn: Interaction):
    return itxn.user.id == dev

class cogUtils(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot


    @app_commands.command(description="Shut the bot down")
    @app_commands.check(is_dev)
    @app_commands.guilds(dev_guild)
    async def kill(self, itxn: interactions.Interaction):
        await itxn.response.send_message("Bot is promptly dying...")
        print(f"[cogUtils]: Bot killed by {itxn.message.author.global_name}")
        await self.bot.close()


    @app_commands.command(description="Attempts to load a cog, given it's filename, and register it")
    @app_commands.check(is_dev)
    @app_commands.describe(filename="The filename of the cog to attempt to import and register")
    @app_commands.guilds(dev_guild)
    async def register(self, itxn: interactions.Interaction, filename: str) -> None:
        global perma_cog_files,current_cog_files
        if Path(filename).exists():
            try:
                await self.bot.load_extension(f"cogs.{filename}")
                perma_cog_files.add(filename)
                current_cog_files.add(filename)
                await itxn.response.send_message(f"cogs.{filename} has successfully been imported and registered",ephemeral=True)
            except commands.ExtensionAlreadyLoaded:
                perma_cog_files.add(filename)
                current_cog_files.add(filename)
                await itxn.response.send_message(f'cogs.{filename} has already been loaded.',ephemeral=True)
            except Exception as ex:
                print(f'[cogUtils]: cogUtils.register({filename}) error: {ex}')
                await itxn.response.send_message(f'Error: {ex}',ephemeral=True)
        else:
            await itxn.response.send_message(f'cogs.{filename} does not exist.',ephemeral=True)
        return None


    @app_commands.command(description="Attempt to load a cog given it's filename")
    @app_commands.check(is_dev)
    @app_commands.describe(extension="The name of the cog's filename to attempt to load")
    @app_commands.choices(extension=[app_commands.Choice(name=cog,value=cog) for cog in perma_cog_files]+[app_commands.Choice(name="all",value="all")])
    @app_commands.guilds(dev_guild)
    async def load(self, itxn: interactions.Interaction, extension: app_commands.Choice[str]) -> None:
        #doesn't let you import a new cog that has been added since starting the bot?
        global current_cog_files
        diff = perma_cog_files.difference(current_cog_files)

        if extension.name == "all":
            extension = diff
        elif not extension.name in perma_cog_files:
            await itxn.response.send_message(f"{extension.name} is not registered. Use `/register {extension.name}`",ephemeral=True)
            return None
        else:
            extension = [extension.name]

        for ext in extension:
            try:
                print(f"[cogUtils]: Trying to load {ext}")
                await self.bot.load_extension(f'cogs.{ext[:-3]}')
                await itxn.response.send_message(f'{ext} Loaded.',ephemeral=True)
                current_cog_files.add(str(ext))
            except commands.ExtensionAlreadyLoaded:
                await itxn.response.send_message(f'{ext} is already loaded.',ephemeral=True)
                current_cog_files.add(str(ext))
            except Exception as ex:
                print(f'[cogUtils]: cogUtils.load({ext}) error: {ex}')
                await itxn.response.send_message(f'Error: {ex}',ephemeral=True)
        return None


    @app_commands.command(description="Attempt to unload a cog given it's filename")
    @app_commands.check(is_dev)
    @app_commands.describe(extension="The name of the cog's filename to attempt to unload")
    @app_commands.choices(extension=[app_commands.Choice(name=cog,value=cog) for cog in current_cog_files]+[app_commands.Choice(name="all",value="all")])
    @app_commands.guilds(dev_guild)
    async def unload(self, itxn: interactions.Interaction, extension: app_commands.Choice[str]) -> None:
        global current_cog_files

        if extension.name == "all":
            extension = current_cog_files
        elif not extension.name in current_cog_files:
            await itxn.response.send_message(f'{extension.name} already unloaded.',ephemeral=True)
            return None
        else:
            extension = [extension.name]

        for ext in extension:
            try:
                print(f"[cogUtils]: Trying to unload {ext}")
                await self.bot.unload_extension(f'cogs.{ext[:-3]}')
                await itxn.response.send_message(f'{ext} Unloaded.',ephemeral=True)
                current_cog_files.discard(str(ext))
            except commands.ExtensionNotLoaded:
                await itxn.response.send_message(f'{ext} is already unloaded.',ephemeral=True)
                current_cog_files.discard(str(ext))
            except Exception as ex:
                print(f'[cogUtils]: cogUtils.unload({ext}) error: {ex}')
                await itxn.response.send_message(f'Error: {ex}',ephemeral=True)
        return None


    @app_commands.command(description="Attempt to reload a or multiple cog/s given their filename/s")
    @app_commands.check(is_dev)
    @app_commands.describe(extension="The name of the cog/s' filename/s to attempt to reload")
    @app_commands.choices(extension=[app_commands.Choice(name=cog,value=cog) for cog in current_cog_files]+[app_commands.Choice(name="current",value="all")]+[app_commands.Choice(name="all",value="all")])
    @app_commands.guilds(dev_guild)
    async def reload(self, itxn: interactions.Interaction, extension: app_commands.Choice[str]) -> None:
        global current_cog_files

        if extension.name in ["all", "current"]:
            unloads = current_cog_files
        elif extension.name not in perma_cog_files:
            await itxn.response.send_message(f"{extension.name} is not registered. Use `/register {extension.name}`",ephemeral=True)
            return None
        else:
            unloads = [extension.name] if extension.name in current_cog_files else []
            
        
        loads = perma_cog_files if extension.name == "all" else deepcopy(current_cog_files) if extension.name == "current" else [extension.name]

        string = f""
        for cog in unloads:
            if not Path(f"cogs/{cog}").exists():
                string += f"cogs.{cog} does not exist\n"
                print(f"[cogUtils]: cogs.{cog} does not exist")
                continue
            try:
                print(f"[cogUtils]: Trying to unload {cog}")
                await self.bot.unload_extension(f'cogs.{cog[:-3]}')
                string += f"cogs.{cog} unloaded\n"
                print(f"[cogUtils]: cogs.{cog} unloaded")
            except commands.ExtensionNotLoaded:
                string += f"cogs.{cog} already unloaded\n"
                print(f"[cogUtils]: cogs.{cog} already unloaded")
            except Exception as ex:
                string += f"Error while trying to unload cogs.{cog}: {ex}\n"
                print(f"[cogUtils]: Error while trying to unload cogs.{cog}: {ex}")
        for cog in loads:
            if not Path(f"cogs/{cog}").exists():
                string += f"cogs.{cog} does not exist\n"
                print(f"[cogUtils]: cogs.{cog} does not exist")
                continue
            try:
                print(f"[cogUtils]: Trying to load {cog}")
                await self.bot.load_extension(f'cogs.{cog[:-3]}')
                string += f"cogs.{cog} loaded\n"
                print(f"[cogUtils]: cogs.{cog} loaded")
            except commands.ExtensionAlreadyLoaded:
                string += f"cogs.{cog} already loaded\n"
                print(f"cogs.{cog} already loaded")
            except Exception as ex:
                string += f"Error while trying to load cogs.{cog}: {ex}\n"
                print(f"[cogUtils]: Error while trying to load cogs.{cog}: {ex}")
        
        await itxn.response.send_message(string,ephemeral=True)
        return None



    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[cogUtils]: perma_cog_files={perma_cog_files}\n[cogUtils]: current_cog_files={current_cog_files}")
        print("[cogUtils]: cogUtils cog ready!")


async def setup(bot):
    await bot.add_cog(cogUtils(bot))