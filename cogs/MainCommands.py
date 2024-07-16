from discord.ext import commands
from discord import Interaction, app_commands, interactions, Object
from json import load

with open("secrets.json","r") as f:
    loaded = load(f)
    dev = loaded["dev_id"] or ""
    dev_guild = Object(id=int(loaded["dev_guild_id"]))

def is_dev(itxn: Interaction):
    return itxn.user.id == dev

class MainCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # instead of bot.command(), use this:
    @app_commands.command(description="Synchronise tree with bot's slash commands")
    @app_commands.check(is_dev)
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


    @commands.Cog.listener()
    async def on_ready(self):
        print("[MainCommands]: MainCommands cog ready!")


async def setup(bot):
    await bot.add_cog(MainCommands(bot))