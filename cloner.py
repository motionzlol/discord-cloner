import discord
import json
import os
import string
import random
from datetime import datetime
import time
import asyncio
CLONES_DIR = "clones"
WELL_KNOWN_BOTS = {
    "mee6": "https://mee6.xyz",
    "dyno": "https://dyno.gg",
    "carl-bot": "https://carl.gg",
    "yagpdb": "https://yagpdb.xyz",
    "suggester": "https://suggester.js.org",
    "tatsu": "https://tatsu.gg",
    "probot": "https://probot.io"
}
def generate_reference():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))
async def delete_existing_channels(guild):
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error deleting channel {channel.name}: {e}")
async def delete_existing_roles(guild):
    for role in guild.roles:
        try:
            if not role.managed and role.name != "@everyone":
                await role.delete()
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error deleting role {role.name}: {e}")
async def create_clone_reference(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("This command can only be used in a server.")
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("You need administrator permissions to use this command.")
    os.makedirs(CLONES_DIR, exist_ok=True)
    reference = generate_reference()
    file_path = os.path.join(CLONES_DIR, f"{reference}.json")
    server_data = {
        "name": interaction.guild.name,
        "icon": str(interaction.guild.icon.url) if interaction.guild.icon else None,
        "channels": [],
        "roles": [],
        "bots": [],
        "created_at": datetime.utcnow().isoformat()
    }
    for channel in interaction.guild.channels:
        channel_data = {
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "permissions": [{
                "target": perm[0].name if perm[0] else "everyone",
                "permissions": perm[1]._values
            } for perm in channel.overwrites.items()],
            "category": channel.category.name if channel.category else None,
            "topic": channel.topic if hasattr(channel, 'topic') else None,
            "nsfw": channel.nsfw if hasattr(channel, 'nsfw') else False,
            "slowmode_delay": channel.slowmode_delay if hasattr(channel, 'slowmode_delay') else 0
        }
        server_data["channels"].append(channel_data)
    for role in interaction.guild.roles:
        if role.managed or role.name == "@everyone":
            continue
        role_data = {
            "name": role.name,
            "color": role.color.value,
            "permissions": role.permissions.value,
            "position": role.position,
            "hoist": role.hoist,
            "mentionable": role.mentionable
        }
        server_data["roles"].append(role_data)
    for member in interaction.guild.members:
        if member.bot:
            bot_info = {
                "name": member.name,
                "id": member.id,
                "avatar": str(member.avatar.url) if member.avatar else None
            }
            server_data["bots"].append(bot_info)
    with open(file_path, 'w') as f:
        json.dump(server_data, f, indent=4)
    await interaction.response.send_message(
        f"Finished cloning! Run `/clone` in a new server followed by this unique reference `{reference}` to clone your server. WRITE THIS DOWN SOMEWHERE.")
async def clone_server(interaction: discord.Interaction, reference: str):
    if not interaction.guild:
        return await interaction.response.send_message("This command can only be used in a server.")
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("You need administrator permissions to use this command.")
    file_path = os.path.join(CLONES_DIR, f"{reference}.json")
    if not os.path.exists(file_path):
        return await interaction.response.send_message("Invalid reference code.")
    start_time = time.time()
    await interaction.response.defer()
    try:
        await delete_existing_channels(interaction.guild)
        await delete_existing_roles(interaction.guild)
        with open(file_path, 'r') as f:
            server_data = json.load(f)
        role_mapping = {}
        for role_data in server_data["roles"]:
            try:
                new_role = await interaction.guild.create_role(
                    name=role_data["name"],
                    color=discord.Color(role_data["color"]),
                    permissions=discord.Permissions(role_data["permissions"]),
                    hoist=role_data.get("hoist", False),
                    mentionable=role_data.get("mentionable", False)
                )
                role_mapping[role_data["name"]] = new_role
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error creating role {role_data['name']}: {e}")
        for channel_data in server_data["channels"]:
            try:
                if channel_data["type"] == "text":
                    new_channel = await interaction.guild.create_text_channel(
                        name=channel_data["name"],
                        position=channel_data["position"],
                        topic=channel_data.get("topic"),
                        nsfw=channel_data.get("nsfw", False),
                        slowmode_delay=channel_data.get("slowmode_delay", 0)
                    )
                    for perm in channel_data["permissions"]:
                        target = discord.utils.get(interaction.guild.roles, name=perm["target"]) or interaction.guild.default_role
                        overwrite = discord.PermissionOverwrite(**{
                            perm_name: value for perm_name, value in perm["permissions"].items()
                        })
                        await new_channel.set_permissions(target, overwrite=overwrite)
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error creating channel {channel_data['name']}: {e}")
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        for channel in interaction.guild.text_channels:
            try:
                bot_list = "These are bots from previous servers:\n"
                for bot_info in server_data.get("bots", []):
                    if bot_info["name"].lower() in WELL_KNOWN_BOTS:
                        bot_list += f"- [{bot_info['name']}]({WELL_KNOWN_BOTS[bot_info['name'].lower()]})\n"
                    else:
                        bot_list += f"- {bot_info['name']}\n"
                await channel.send(f"<@{interaction.user.id}> Cloning has completed in {duration} seconds!\n{bot_list}")
                try:
                    with open(file_path, 'r+') as f:
                        data = json.load(f)
                        data["cloned"] = {
                            "cloned_at": datetime.utcnow().isoformat(),
                            "cloned_by": str(interaction.user),
                            "cloned_to": interaction.guild.name
                        }
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                    await channel.send("✅ This server has been marked as cloned in the file.")
                except Exception as e:
                    print(f"Error updating JSON file: {e}")
                    await channel.send("⚠️ Could not update the file, but cloning completed successfully.")
                break
            except Exception as e:
                print(f"Error sending completion message: {e}")
                continue
            break
        try:
            bot_links = "\nBot Invite Links:\n"
            for bot_info in server_data.get("bots", []):
                bot_links += f"- [{bot_info['name']}](https://discord.com/oauth2/authorize?client_id={bot_info['id']}&scope=bot&permissions=8)\n"
            await channel.send(bot_links)
        except Exception as e:
            print(f"Error sending bot links: {e}")
    except Exception as e:
        print(f"Error during cloning: {e}")
        await interaction.followup.send("An error occurred during cloning. Please try again.")