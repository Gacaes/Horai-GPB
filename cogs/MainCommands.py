from discord.ext import commands
from discord import Interaction, app_commands, interactions



def is_dev(itxn: Interaction):
    return itxn.user.id == 425748749462274048

class MainCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # instead of bot.command(), use this:
    @app_commands.command(description="Synchronise tree with bot's slash commands")
    @app_commands.check(is_dev)
    async def sync(self, itxn:interactions.Interaction, actually_sync: bool = False) -> None:
        if actually_sync:
            await self.bot.tree.sync()
            await itxn.response.send_message("Tree synced!",ephemeral=True)
            return None
        await itxn.response.send_message("Fake sync!",ephemeral=True)
        return None


    @commands.Cog.listener()
    async def on_ready(self):
        print("MainCommands cog ready!")


async def setup(bot):
    await bot.add_cog(MainCommands(bot))