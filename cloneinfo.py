import discord
import json
import os
from datetime import datetime
CLONES_DIR = "clones"
async def get_clone_info(interaction: discord.Interaction, reference: str):
    if not interaction.guild:
        return await interaction.response.send_message("This command can only be used in a server.")
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("You need administrator permissions to use this command.")
    file_path = os.path.join(CLONES_DIR, f"{reference}.json")
    if not os.path.exists(file_path):
        return await interaction.response.send_message("Invalid reference code.")
    with open(file_path, 'r') as f:
        server_data = json.load(f)
    embed = discord.Embed(
        title=f"Clone Information: {server_data['name']}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Original Server Name", value=server_data['name'], inline=False)
    if server_data['icon']:
        embed.set_thumbnail(url=server_data['icon'])
    channel_count = len(server_data['channels'])
    embed.add_field(name="Channels", value=f"{channel_count} channels cloned", inline=False)
    role_count = len(server_data['roles'])
    embed.add_field(name="Roles", value=f"{role_count} roles cloned", inline=False)
    bot_count = len(server_data['bots'])
    embed.add_field(name="Bots", value=f"{bot_count} bots detected", inline=False)
    created_at = datetime.fromisoformat(server_data['created_at'])
    embed.add_field(
        name="Clone Created", 
        value=f"<t:{int(created_at.timestamp())}:F>", 
        inline=False
    )
    if 'cloned' in server_data:
        cloned_at = datetime.fromisoformat(server_data['cloned']['cloned_at'])
        embed.add_field(
            name="Cloning Status",
            value=f"✅ This clone has been applied to '{server_data['cloned']['cloned_to']}' on <t:{int(cloned_at.timestamp())}:F> by {server_data['cloned']['cloned_by']}",
            inline=False
        )
    else:
        embed.add_field(
            name="Cloning Status",
            value="❌ This clone has not been applied to any server yet",
            inline=False
        )
    await interaction.response.send_message(embed=embed)