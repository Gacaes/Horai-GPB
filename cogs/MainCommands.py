from discord.ext import commands
from discord import Interaction, app_commands, interactions, Object, Message
from json import load as Jload
from os import environ, listdir, mkdir
from pathlib import Path
#from pickle import load as Pload,dump as Pdump
#from classes import User
from time import time

if Path("secrets.json").exists():
    with open("secrets.json","r") as f:
        loaded = Jload(f)
        dev = loaded["dev_id"] or ""
        dev_guild = Object(id=int(loaded["dev_guild_id"])) or ""
else:
    dev = environ.get("dev_id","")
    dev = int(dev) if not dev is None else ""
    dev_guild = Object(id=int(environ.get("dev_guild_id","")))

if "" in [dev, dev_guild]:
    raise Exception("Unable to load variables from secrets.json or environment variables")

def is_dev(itxn: Interaction | commands.Context):
    if isinstance(itxn, Interaction):
        return itxn.user.id == dev
    else:
        return itxn.author.id == dev

guilds = {"dev": 775899147915231263}
def time_checker():
    epoch:int = time()//900
    print(f"[TC]: Epoch={epoch}")
    for guild in list(guilds.values()):
        if not Path(f"DBs/").exists():
            mkdir("DBs/")
        if not Path(f"DBs/{guild}/").exists():
            mkdir(f"DBs/{guild}/")
        if not Path(f"DBs/{guild}/epochs").exists():
            mkdir(f"DBs/{guild}/epochs/")

        epochs = [int(i) for i in listdir(f"DBs/{guild}/epochs/")]
        maxi = max(epochs)
        print(f"[TC]: Last max epoch={maxi}")

class MainCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    #@app_commands.command(description="Synchronise tree with bot's slash commands")
    #@app_commands.check(is_dev)
    async def sync(self, itxn:interactions.Interaction, actually_sync: bool = False) -> None:
        if actually_sync:
            print("Trying to sync")
            await itxn.response.defer(thinking=True,ephemeral=True)
            try:
                results = await self.bot.tree.sync()
                results = ", ".join([i.name for i in results])
            except Exception as ex:
                print(f"Failed to sync, exception ocurred: {ex}")
                await itxn.followup.send(f"Sync failed!",ephemeral=True)
                return None
            print(f"Synced commands: {results} !")
            await itxn.followup.send(f"Synced commands: {results} !",ephemeral=True)
            #await itxn.response.send_message("Tree synced!",ephemeral=True)
            return None
        await itxn.response.send_message("Fake sync!",ephemeral=True)
        return None

    @commands.hybrid_command(with_app_command=False)
    @commands.check(is_dev)
    async def sink(self, ctx: commands.Context, actually_sync: bool = False) -> None:
        #await ctx.reply(content="this is a test of sink",ephemeral=True)
        if actually_sync:
            print("Trying to sync")
            #await itxn.response.defer(thinking=True,ephemeral=True)
            try:
                results = await self.bot.tree.sync()
                results = ", ".join([i.name for i in results])
            except Exception as ex:
                print(f"Failed to sync, exception ocurred: {ex}")
                await ctx.reply(f"Sync failed!",ephemeral=True)
                return None
            print(f"Synced commands: {results} !")
            await ctx.reply(f"Synced commands: {results} !",ephemeral=True)
            #await itxn.response.send_message("Tree synced!",ephemeral=True)
            return None
        await ctx.reply("Fake sync!",ephemeral=True)
        return None
    
    #@commands.Cog.listener()
    async def on_app_command_completion(self, itxn: interactions.Interaction, command: app_commands.Command | app_commands.ContextMenu):
        print("\ncommand_compl:\n\tdata=",itxn.data,"\n\tuser name=",itxn.user.name,"\n\tcommand name=",command.name)
    
    #@commands.Cog.listener()
    async def on_interaction(self, itxn: interactions.Interaction):
        print("\non_intxn:\n\tdata=",itxn.data,"\n\tuser name=",itxn.user.name)

    @app_commands.command(description="Test interaction")
    async def test(self, itxn: interactions.Interaction, msg: str = ""):
        await itxn.response.send_message(f"This is a test interaction. Msg: {msg}")
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        print("[MainCommands]: MainCommands cog ready!")
    
    #@commands.Cog.listener()
    async def on_message(self, message: Message):
        print("msg embeds=",message.embeds)


async def setup(bot):
    await bot.add_cog(MainCommands(bot))