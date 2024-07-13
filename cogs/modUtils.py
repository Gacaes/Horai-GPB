from discord.ext import commands
from discord import Interaction, app_commands, interactions, Embed, DMChannel, User
from tinydb import TinyDB,Query
from os import listdir,mkdir
from json import load
from pathlib import Path
from time import time

with open("secrets.json","r") as f:
    loaded = load(f)
    dev = loaded["dev_id"] or ""
    dev_guild = loaded["dev_guild_id"]

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
        return False
    except KeyError:
        db[guild_id][user_id] = TinyDB(f"DBs/{guild_id}_users/{user_id}.json")
    return True

async def User_add(itxn:interactions.Interaction, user_id: int, item: str, value) -> bool:
    global db
    guild_id = str(itxn.guild.id)
    await check_User(itxn=itxn, user_id=user_id)
    #print("109 checked")
    
    if db[guild_id][user_id].search(query.type == item and query.value == value):
        #has already been inserted
        #print("112 already inserted")
        return False
    db[guild_id][user_id].insert({"type":item, "value":value})
    #print("115 inserted")
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
    checker = await check_User(itxn=itxn, user_id=user_id)
    if not checker:
        return False
    
    if value == "":
        temp = db[guild_id][user_id].search(query.type == item)
        if temp:
            db[guild_id][user_id].remove(query.type == item)
            return True
        return False
    else:
        temp = db[guild_id][user_id].search(query.type == item and query.value == value)
        if temp:
            db[guild_id][user_id].remove(query.type == item and query.value == value)
            return True
        return False

class modUtils(commands.Cog):
    group = app_commands.Group(name="notice", description="Creation of notices to certain channel/s by certain role/s")

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @group.command(name="role",description="Add, remove or view roles whitelisted for use of notices.")
    #@app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="The role to be used for add/remove queries. Supports multiple roles.",action="The action to be taken with respect to the role. 'view' shows you all of the roles that are whitelisted.")
    @app_commands.choices(action=[app_commands.Choice(name="add",value="add"),app_commands.Choice(name="remove",value="remove"),app_commands.Choice(name="view",value="view")])
    async def role(self, itxn:interactions.Interaction, action: app_commands.Choice[str], role: str = "") -> None:
        embed_ = Embed()

        if action.name == "add":
            embed_.title = "Notices"
            embed_.description = "Roles to add to whitelist for notices"
            if role == "":
                await itxn.response.send_message("Missing role to add",ephemeral=False)
                return None
            else:
                roles = role.split('>')[:-1]
            string = f""
            for role_ in roles:
                role_ = role_[role_.find("<"):]
                #print(f"role_={role_}")
                added = await addDB(itxn=itxn, item="notice_role", value=role_[3:])
                string += f"{role_}>"
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
            #print(temp)
            string = f""
            if temp:
                for role_ in temp:
                    #print(f"[modUtils]: role_={role_}")
                    string += f"<@&{role_['value']}>\n"
            else:
                string += "(None to show)"
            embed_.add_field(name="Roles on whitelist",value=string)
            await itxn.response.send_message(embed=embed_,ephemeral=False)
            return None
        
        elif action.name == "remove":
            embed_.title = "Notices"
            embed_.description = "Roles to remove from whitelist for notices"
            if role == "":
                await itxn.response.send_message("Missing role to remove",ephemeral=False)
                return None
            else:
                roles = role.split('>')[:-1]
            string = f""
            for role_ in roles:
                role_ = role_[role_.find("<"):]
                removed = await remDB(itxn=itxn, item="notice_role", value=role_[3:])
                string += f"{role_}>"
                if not removed:
                    string += f" already isn't in the whitelist"
                string += "\n"
            embed_.add_field(name="Roles removed",value=string)
            await itxn.response.send_message(embed=embed_,ephemeral=False)
            return None
        
        else:
            await itxn.response.send_message("Bad input",ephemeral=True)
            return None
        #await changeDB(itxn=itxn, item="", value="")

    @group.command(name="create",description="Create a notice")
    @app_commands.describe(user="The user/s the notice is with regards to",reason="The reason given for the notice (optional, default=None)",channel="The channel/s to send the notice to",notify="Whether to notify the user/s in question (optional, default=False)",dm="If 'notify' is True, 'dm' will determine whether to send the user/s the notice in their DMs or in this current channel (optional, default=False)")
    async def create(self, itxn:interactions.Interaction, user: str, channel: str, reason: str = "", notify: bool = False, dm: bool = False) -> None:
        perms = [i["value"] for i in await viewDB(itxn, item="notice_role")]
        role_ids = [str(i.id) for i in itxn.user.roles]
        if set(perms) & set(role_ids):
            #if the user has a role in the whitelist to be able to run this command
            users = [i[i.find("<")+2:] for i in user.split(">")[:-1]]
            print("[cogUtils]: users=",users)
            channels = [i[i.find("<")+2:] for i in channel.split(">")[:-1]]
            print("[cogUtils]: channels=",channels)

            for u in users:
                #print(1)
                current_user_notices = await User_view(itxn=itxn, user_id=u, item="notice")
                #print("current notices=",current_user_notices)
                total = len(current_user_notices)
                #print(total)
                new_reason = reason if reason else '(None given)'
                #print(new_reason)
                new_notify = '(None)' if not notify else 'DM' if dm else '<#'+str(itxn.channel_id)+'>'
                #print(new_notify)
                timestamp = int(time())
                #print(timestamp)
                #sent_messages = []

                embed = Embed()
                embed.title = f"Notice"
                embed.color = 0xFFFF00 #yellow
                #embed.description = f"given out by <@{itxn.user.id}>"
                embed.set_author(name=itxn.user.global_name,icon_url=itxn.user.avatar.url) #the user who executed the command
                embed.add_field(name="Details",value=f"User: <@{u}>\nUser ID: {u}\nReason: {new_reason}\nNotified by: <@{itxn.user.id}>")


                if notify:
                    if dm:
                        user:User = self.bot.get_user(int(u))
                        if user.dm_channel:
                            sent = await user.dm_channel.send(content=f"<@{u}>, you are being served a notice:",embed=embed)
                        else:
                            dm:DMChannel = await user.create_dm()
                            sent = await dm.send(content=f"<@{u}>, you are being served a notice:",embed=embed)
                    else:
                        sent = await itxn.channel.send(content=f"<@{u}>, you are being served a notice:",embed=embed)

                for c in channels:
                    try:
                        get_channel = self.bot.get_channel(int(c))
                    except Exception as ex:
                        print("error=",ex)
                        await itxn.response.send_message(content=ex)
                        continue

                    #print(2)
                    #print("embed made")
                    embed.add_field(name="Extra details",value=f"\nNotice given: {notify}\nChannel notified: {new_notify}\nTotal notices: {total}\nNotice Link: {sent.to_reference().jump_url}\nTimestamp: <t:{timestamp}:F>")
                    await get_channel.send(embed=embed)
                    
                notice_data = {"id":int(total), "reason":new_reason, "notified":notify, "channel":new_notify, "by":itxn.user.id, "time":timestamp}
                #print(notice_data)
                await User_add(itxn=itxn,user_id=u,item="notice",value=notice_data)
                #print("added")


            await itxn.response.send_message(content="Notice/s sent",ephemeral=True)
        else:
            #the user is not whitelisted
            await itxn.response.send_message("You do not have permission to use this command. If you believe there is an issue, contact your server admin/s or the dev.",ephemeral=True)
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        print("[modUtils.py]: modUtils cog ready!")


async def setup(bot):
    global query,db
    db = {}
    for filename in listdir("./DBs"):
        if filename.endswith(".json"):
            print(f"[modUtils]: Loading DBs/{filename}")
            db[filename[:-5]] = {"main":TinyDB(f"DBs/{filename}")}

        if Path(f"DBs/{filename[:-5]}_users/").exists():
            for username in listdir(f"./DBs/{filename[:-5]}_users/"):
                print(f"[modUtils]: Loading DBs/{filename[:-5]}_users/{username}")
                db[filename[:-5]][username[:-5]] = TinyDB(f"DBs/{filename[:-5]}_users/{username}")

    query = Query()
    await bot.add_cog(modUtils(bot))