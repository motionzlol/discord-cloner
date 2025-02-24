import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import cloner
import cloneinfo
import asyncio
load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="all of the stars have a reason"
    ))
    print(f'Logged in as {bot.user}')
@bot.tree.command(name="clone", description="Clone a server using a reference code")
async def clone(interaction: discord.Interaction, reference: str):
    await cloner.clone_server(interaction, reference)
@bot.tree.command(name="cloner", description="Create a clone reference of the current server")
async def cloner_command(interaction: discord.Interaction):
    await cloner.create_clone_reference(interaction)
@bot.tree.command(name="cloneinfo", description="Get information about a clone")
async def cloneinfo_command(interaction: discord.Interaction, reference: str):
    await cloneinfo.get_clone_info(interaction, reference)
bot.run(os.getenv('tkn'))