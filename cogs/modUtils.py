from discord.ext import commands
from discord.abc import GuildChannel, PrivateChannel
from discord import Interaction, app_commands, interactions, Embed, DMChannel, User, Member, Role, TextChannel, Message, Object
from tinydb import TinyDB,Query
from os import listdir,mkdir,environ
from json import load
from pathlib import Path
from time import time

if Path("secrets.json").exists():
    with open("secrets.json","r") as f:
        loaded = load(f)
        dev = loaded["dev_id"] or ""
        dev_guild = Object(id=int(loaded["dev_guild_id"])) or ""
else:
    dev = environ.get("dev_id","")
    dev_guild = Object(id=int(environ.get("dev_guild_id","")))

if "" in [dev, dev_guild]:
    raise Exception("Unable to load variables from secrets.json or environment variables")

db = {}
query:Query = Query()

class whitelist:
    async def extended_check(itxn: interactions.Interaction):
        #print(f"{itxn.user.global_name} is trying to run a whitelist protected command called {itxn.command.name}")
        whitelisted = await viewDB(itxn=itxn, item="notice_role")
        whitelisted = [i["value"] for i in whitelisted]
        for role in itxn.user.roles:
            if str(role.id) in whitelisted:
                return True
        await itxn.response.send_message(content="You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.", ephemeral=True)
        return False

def has_whitelist():
    return app_commands.check(whitelist.extended_check)

def is_dev(itxn: Interaction):
    return itxn.user.id == dev

async def check_db(itxn:interactions.Interaction) -> bool:
    global db
    guild_id = str(itxn.guild.id)
    t1=True
    try:
        db[guild_id]["main"]
    except KeyError:
        db[guild_id] = {"main":TinyDB(f"DBs/{guild_id}.json")}
        t1=False
    if not Path(f"DBs/{guild_id}_users/").exists():
        mkdir(f"DBs/{guild_id}_users")
    return t1

async def addDB(itxn:interactions.Interaction, item: str, value: str) -> bool:
    global db
    guild_id = str(itxn.guild.id)
    try:
        temp = db[guild_id]["main"].search(query.type == item and query.value == value)
        if temp:
            #the type and item pair already exists
            return False
        db[guild_id]["main"].insert({"type":item, "value":value})
        return True
    except KeyError:
        db[guild_id]["main"] = TinyDB(f"DBs/{guild_id}.json")
        #print(f"Inserting {item},{value}")
        db[guild_id]["main"].insert({"type":item, "value":value})
        return True

async def remDB(itxn:interactions.Interaction, item: str, value: str = "") -> bool:
    global db
    guild_id = str(itxn.guild.id)
    checker = await check_db(itxn=itxn)
    if not checker:
        return False
    
    if value == "":
        temp = db[guild_id]["main"].search(query.type == item)
        if temp:
            db[guild_id]["main"].remove(query.type == item)
            return True
        return False
    else:
        temp = db[guild_id]["main"].search(query.type == item and query.value == value)
        if temp:
            db[guild_id]["main"].remove(query.type == item and query.value == value)
            return True
        return False

async def viewDB(itxn:interactions.Interaction, item: str | list[str] = "", value: str | list[str] = "") -> list:
    global db
    if not (item or value):
        #print("logic")
        #print("[viewDB]: KeyError")
        raise KeyError("No item or value given to be viewed from DB")
    #convert item and value both to list to iterate through
    if type(item) is str:
        item = [item]
    if type(value) is str:
        value = [value]
    guild_id = str(itxn.guild.id)
    try:
        #check if the guild has a DB
        db[guild_id]["main"]
    except KeyError:
        #if the guild doesn't have a DB, create one and return an empty list
        db[guild_id]["main"] = TinyDB(f"DBs/{guild_id}.json")
        return []
    
    gets = []
    for i in item:
        gets += db[guild_id]["main"].search(query.type == i)
    for i in value:
        gets += db[guild_id]["main"].search(query.value == i)
    return gets


async def check_User(itxn:interactions.Interaction, user_id: int) -> bool:
    global db
    await check_db(itxn=itxn)
    guild_id = str(itxn.guild.id)
    try:
        db[guild_id][user_id]
        return True
    except KeyError:
        db[guild_id][user_id] = TinyDB(f"DBs/{guild_id}_users/{user_id}.json")
    return False

async def User_add(itxn:interactions.Interaction, user_id: int, item: str, value) -> bool:
    global db
    guild_id = str(itxn.guild.id)
    await check_User(itxn=itxn, user_id=user_id)
    
    if db[guild_id][user_id].search(query.type == item and query.value == value):
        #has already been inserted
        return False
    db[guild_id][user_id].insert({"type":item, "value":value})
    return True

async def User_view(itxn:interactions.Interaction, user_id:int, item: str | list[str] = "", value: str | list[str] = "") -> list:
    global db
    guild_id = str(itxn.guild.id)
    if not (item or value):
        #print("user logic")
        #print("[viewDB]: KeyError")
        raise KeyError("No item or value given to be viewed from DB")
    #convert item and value both to list to iterate through
    if type(item) is str:
        item = [item]
    if type(value) is str:
        value = [value]
    #print(2)
    await check_User(itxn=itxn, user_id=user_id)
    #print(await check_User(itxn=itxn, user_id=user_id))
    #print("user checked")
    
    gets = []
    for i in item:
        gets += db[guild_id][user_id].search(query.type == i)
    for i in value:
        gets += db[guild_id][user_id].search(query.value == i)
    return gets

async def User_rem(itxn:interactions.Interaction, user_id:int, item: str, value: str = "") -> bool:
    global db
    guild_id = str(itxn.guild.id)
    exists = await check_User(itxn=itxn, user_id=user_id)
    if not exists:
        return False
    
    if value == "":
        temp = db[guild_id][user_id].search(query.type == item)
        if temp:
            db[guild_id][user_id].remove(query.type == item)
            return True
        return False
    else:
        print("item=",item)
        print("value=",value)
        temp = db[guild_id][user_id].search(query.type == item and query.value == value)
        print("temp=",temp)
        if temp:
            db[guild_id][user_id].remove(query.type == item and query.value == value)
            return True
        return False

class modUtils(commands.Cog):
    group = app_commands.Group(name="notice", description="Creation of notices to certain channel/s by certain role/s")

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @group.command(description="Add, remove or view roles whitelisted for use of notices.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="The role to be used for add/remove queries. Supports multiple roles.",action="The action to be taken with respect to the role. 'view' shows you all of the roles that are whitelisted.")
    @app_commands.choices(action=[app_commands.Choice(name="add",value="add"),app_commands.Choice(name="remove",value="remove"),app_commands.Choice(name="view",value="view")])
    async def whitelist(self, itxn:interactions.Interaction, action: app_commands.Choice[str], role: Role | None = None) -> None:
        embed_ = Embed()

        if action.name == "add":
            embed_.title = "Notices"
            embed_.description = "Roles to add to whitelist for notices"
            if role is None:
                await itxn.response.send_message("Missing role to add",ephemeral=False)
                return None
            string = f""
            added = await addDB(itxn=itxn, item="notice_role", value=role.id)
            string += f"{role.mention}"
            if not added:
                string += f" has already been added"
            string += "\n"
            embed_.add_field(name="Roles added",value=string)
            await itxn.response.send_message(embed=embed_,ephemeral=False)
            return None
        
        elif action.name == "view":
            embed_.title = "Notices"
            embed_.description = "View roles on whitelist for notices"
            temp = await viewDB(itxn=itxn, item="notice_role")
            string = f""
            if temp:
                for role_ in temp:
                    string += f"<@&{role_['value']}>\n"
            else:
                string += "(None to show)"
            embed_.add_field(name="Roles on whitelist",value=string)
            await itxn.response.send_message(embed=embed_,ephemeral=False)
            return None
        
        elif action.name == "remove":
            embed_.title = "Notices"
            embed_.description = "Roles to remove from whitelist for notices"
            if role is None:
                await itxn.response.send_message("Missing role to remove",ephemeral=False)
                return None
            string = f""
            removed = await remDB(itxn=itxn, item="notice_role", value=role.id)
            string += f"{role.mention}"
            if not removed:
                string += f" already isn't in the whitelist"
            string += "\n"
            embed_.add_field(name="Roles removed",value=string)
            await itxn.response.send_message(embed=embed_,ephemeral=False)
            return None
        
        else:
            await itxn.response.send_message("Bad input",ephemeral=True)
            return None

    @group.command(description="Create a notice")
    @app_commands.describe(user="The user/s the notice is with regards to",reason="The reason given for the notice (optional, default=None)",channel="The channel/s to send the notice to",notify="Whether to notify the user/s in question (optional, default=False)",dm="If 'notify' is True, 'dm' will determine whether to send the user/s the notice in their DMs or in this current channel (optional, default=False)")
    #@has_whitelist()
    async def create(self, itxn:interactions.Interaction, user: Member, channel: TextChannel, reason: str = "", notify: bool = False, dm: bool = False) -> None:
        #perms = [i["value"] for i in await viewDB(itxn, item="notice_role")]
        #role_ids = [str(i.id) for i in itxn.user.roles]
        if await whitelist.extended_check(itxn):
            #if the user has a role in the whitelist to be able to run this command

            current_user_notices = await User_view(itxn=itxn, user_id=user.id, item="notice")
            total = len(current_user_notices)
            new_reason = reason if reason else '(None given)'
            new_notify = '(None)' if not notify else 'DM' if dm else '<#'+str(itxn.channel_id)+'>'
            timestamp = int(time())

            embed = Embed()
            embed.title = f"Notice"
            embed.color = 0xFFFF00 #yellow
            embed.set_author(name=itxn.user.global_name,icon_url=itxn.user.avatar.url) #the user who executed the command
            embed.add_field(name="Details",value=f"User: {user.mention}\nUser ID: {user.id}\nReason: {new_reason}\nNotified by: <@{itxn.user.id}>")

            if notify:
                if dm:
                    if user.dm_channel:
                        sent = await user.dm_channel.send(content=f"{user.mention}, you are being served a notice:",embed=embed)
                    else:
                        dm:DMChannel = await user.create_dm()
                        sent = await dm.send(content=f"{user.mention}, you are being served a notice:",embed=embed)
                else:
                    sent = await itxn.channel.send(content=f"{user.mention}, you are being served a notice:",embed=embed)
            else:
                sent = None

            embed.add_field(name="Extra details",value=f"\nNotice given: {notify}\nChannel notified: {new_notify}\nTotal notices: {total}\nNotice Link: {sent.to_reference().jump_url if not sent is None else '(User was not notified)'}\nTimestamp: <t:{timestamp}:F>")
            mod = await channel.send(embed=embed)

            notice_data = {"id":int(total), "reason":new_reason, "notified":notify, "channel":new_notify, "mod_channel":channel.id, "by":itxn.user.id, "time":timestamp, "user_notice_id":sent.id if not sent is None else None, "mod_notice_id":mod.id,"prev_reason":None,"edited_timestamp":None}
            await User_add(itxn=itxn,user_id=user.id,item="notice",value=notice_data)

            await itxn.response.send_message(content="Notice/s sent",ephemeral=True)
        else:
            #the user is not whitelisted
            await itxn.response.send_message("You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.",ephemeral=True)
        return None

    @group.command(description="Connect two users together as aliases")
    @app_commands.describe(user="The user to add an alias to",user_alias="The alias of the user")
    async def alias(self, itxn:interactions.Interaction, user: Member, user_alias: Member) -> None:
        #perms = [i["value"] for i in await viewDB(itxn, item="notice_role")]
        #role_ids = [str(i.id) for i in itxn.user.roles]
        if await whitelist.extended_check(itxn):
            current_user_aliases_list: list[dict] = await User_view(itxn=itxn, user_id=user.id, item="alias")
            current_alias_aliases_list: list[dict] = await User_view(itxn=itxn, user_id=user_alias.id, item="alias")
            await User_add(itxn=itxn, user_id=user.id, item="alias", value=user_alias.id)
            await User_add(itxn=itxn, user_id=user_alias.id, item="alias", value=user.id)
            #print(await User_view(itxn=itxn,user_id=user.id,item="alias"))
            #await itxn.response.send_message(content="WIP")
            #return None
            for alias in current_user_aliases_list:
                await User_add(itxn=itxn, user_id=alias["value"], item="alias", value=user_alias.id)
            for alias in current_alias_aliases_list:
                await User_add(itxn=itxn, user_id=alias["value"], item="alias", value=user.id)
            await itxn.response.send_message(content="Aliases connected")
        else:
            #the user is not whitelisted
            await itxn.response.send_message(content="You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.",ephemeral=True)
        return None

    @group.command(description="View a user's notices (Requires you to have a whitelisted role)")
    @app_commands.describe(user="The user whose notices to view and their associated aliases", page="The page number of notices to display")
    async def view(self, itxn: interactions.Interaction, user: Member, page: int = 1) -> None:
        #notice_data = {"id":int(total), "reason":new_reason, "notified":notify, "channel":new_notify, "by":itxn.user.id, "time":timestamp}

        if not await whitelist.extended_check(itxn):
            await itxn.response.send_message(content="You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.", ephemeral=True)
            return None

        embed = Embed(colour=0xFFFF00, title=f"{user.global_name}'s notices")
        embed.set_author(name=user.global_name,icon_url=user.avatar.url)

        notices = await User_view(itxn=itxn, user_id=user.id, item="notice")
        notices.reverse()
        pages = len(notices)//5 + 1*bool(len(notices)%5)
        if pages:
            page = (page-1)%pages
        else:
            page = 0

        if notices:
            for notice in notices[page*5:(page+1)*5]:
                data = notice["value"]
                embed.add_field(name=f"Notice #{data['id']}", value=f"Reason: {data['reason']}\nWas notified? {data['notified']}\nChannel notified: {data['channel']}\nNotified by: <@{data['by']}>\nTimestamp: <t:{data['time']}:F>", inline=False)
        else:
            embed.add_field(name="User notices:",value="(None to show)")
        aliases = await User_view(itxn=itxn, user_id=user.id, item="alias")
        print("aliases=",aliases)
        embed.add_field(name="Aliases",value=", ".join([f'{i["value"]} : <@{i["value"]}>' for i in aliases]) if aliases else "(No associated aliases to show)",inline=False)
        embed.set_footer(text=f"Page {page+1} of {pages if pages else 1}")
        
        await itxn.response.send_message(embed=embed)
        return None
    
    @group.command(description="View your own notices")
    @app_commands.describe(page="The page number of notices to display")
    async def me(self, itxn: interactions.Interaction, page: int = 1) -> None:
        await itxn.response.send_message(content="Notice me senpai? UwU")
        
        embed = Embed(colour=0xFFFF00, title=f"{itxn.user.global_name}'s notices")
        embed.set_author(name=itxn.user.global_name,icon_url=itxn.user.avatar.url)

        notices = await User_view(itxn=itxn, user_id=itxn.user.id, item="notice")
        notices.reverse()
        pages = len(notices)//5 + 1*bool(len(notices)%5)
        if pages:
            page = (page-1)%pages
        else:
            page = 0

        if notices:
            for notice in notices[page*5:(page+1)*5]:
                data = notice["value"]
                embed.add_field(name=f"Notice #{data['id']}", value=f"Reason: {data['reason']}\nWas notified? {data['notified']}\nChannel notified: {data['channel']}\nNotified by: <@{data['by']}>\nTimestamp: <t:{data['time']}:F>", inline=False)
        else:
            embed.add_field(name="User notices:",value="(None to show)")
        #aliases = await User_view(itxn=itxn, user_id=itxn.user.id, item="alias")
        #embed.add_field(name="Aliases",value=", ".join([i["value"] for i in aliases]) if aliases else "(No associated aliases to show)",inline=False)
        embed.set_footer(text=f"Page {page+1} of {pages if pages else 1}")
        
        await itxn.edit_original_response(content=None,embed=embed)
        return None

    @group.command(description="Edit a user's notice given the user's notice's ID")
    @app_commands.describe(user="The user whose notice you want to edit",new_reason="The new reason you want to change the notice to",notice_id="The notice ID that you want to edit (defaults to the last notice given)")
    async def edit(self, itxn: interactions.Interaction, user: Member, new_reason: str, notice_id: int = -1) -> None:
        if not await whitelist.extended_check(itxn):
            await itxn.response.send_message(content="You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.", ephemeral=True)
            return None
        
        notices = await User_view(itxn=itxn, user_id=user.id, item="notice")
        if not notices:
            await itxn.response.send_message(content=f"User {user.mention} does not have any notices")
            return None
        #print(1)
        notice_ids = [notice["value"]["id"] for notice in notices]
        #print("notice_ids=",notice_ids)
        if notice_id == -1:
            notice_id = max(notice_ids)
        if not notice_id in notice_ids:
            await itxn.response.send_message(f"{user.mention} does not have a notice with ID #{notice_id}")
            return None
        #print("notice_id=",notice_id)
        
        global db
        notice = notices[notice_ids.index(notice_id)]
        #print("notice=",notice)

        notice_data:dict = notice["value"]
        #{"id":int(total), "reason":new_reason, "notified":notify, "channel":new_notify, "mod_channel":channel.id, "by":itxn.user.id, "time":timestamp, "user_notice_id":sent.id if not sent is None else None, "mod_notice_id":mod.id,"prev_reason":None,"edited_timestamp":None}
        new_data = dict(notice_data)
        new_data["prev_reason"] = notice_data["reason"]
        new_data["reason"] = new_reason
        new_data["edited_timestamp"] = int(time())
        #print(2)
        db[str(itxn.guild_id)][user.id].update({"value":new_data}, query.value == notice_data)
        #print(3)
        await itxn.response.send_message(f"Notice #{notice_id} for {user.mention} reason has been changed from '{notice_data['reason']}' to '{new_reason}'")
        return None

        '''
        if notice["value"]["notify"]:
            #if the user was notified
            if notice["value"]["channel"].startswith("<#"):
                #the user was notified in a guild channel
                channel:GuildChannel = self.bot.get_channel(notice["value"]["channel"][2:-1])
            else:
                #the user was notified in DMs
                channel:DMChannel = user.dm_channel
            message:Message = channel.fetch_message(notice["value"]["user_notice_id"])
            embed = Embed(title="Notice",colour=0xFFFF00)
            embed.set_author(name=,icon_url=) #the user who executed the command
            embed.add_field(name="Details",value=f"User: {user.mention}\nUser ID: {user.id}\nReason: {new_reason}\nNotified by: <@{itxn.user.id}>")
            message.edit(content=f"{user.mention}, you are being served a notice:",embed=embed)
        '''

    @group.command(description="Remove a user's notice given the user's notice's ID")
    @app_commands.describe(user="The user whose notice you want to edit",notice_id="The notice ID that you want to edit (defaults to the last notice given)")
    @has_whitelist()
    async def remove(self, itxn: interactions.Interaction, user: Member, notice_id: int = -1) -> None:
        #if not await whitelist.extended_check(itxn):
        #    await itxn.response.send_message(content="You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.", ephemeral=True)
        #    return None
        
        notices = await User_view(itxn=itxn, user_id=user.id, item="notice")
        if not notices:
            await itxn.response.send_message(content=f"User {user.global_name} does not have any notices")
            return None
        notice_ids = [notice["value"]["id"] for notice in notices]
        if notice_id == -1:
            notice_id = max(notice_ids)
        if not notice_id in notice_ids:
            await itxn.response.send_message(f"{user.global_name} does not have a notice with ID #{notice_id}")
            return None
        
        done = await User_rem(itxn=itxn, user_id=user.id, item="notice", value=notices[notice_ids.index(notice_id)]["value"])
        if done:
            await itxn.response.send_message(content=f"Successfully removed notice #{notice_id} for {user.global_name}")
        else:
            await itxn.response.send_message(content=f"Something went wrong. Unable to remove notice #{notice_id} for {user.global_name}")
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        print("[modUtils.py]: modUtils cog ready!")


async def setup(bot):
    global query,db
    
    if not Path("DBs/").exists():
        mkdir("DBs")

    for filename in listdir("./DBs"):
        if filename.endswith(".json"):
            print(f"[modUtils]: Loading DBs/{filename}")
            db[filename[:-5]] = {"main":TinyDB(f"DBs/{filename}")}

        if Path(f"DBs/{filename[:-5]}_users/").exists():
            for username in listdir(f"./DBs/{filename[:-5]}_users/"):
                print(f"[modUtils]: Loading DBs/{filename[:-5]}_users/{username}")
                db[filename[:-5]][username[:-5]] = TinyDB(f"DBs/{filename[:-5]}_users/{username}")

    await bot.add_cog(modUtils(bot))