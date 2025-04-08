import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
import asyncio
import json
from datetime import datetime

# Bot configuration
ROBLOX_GREEN = 0x00B06F  # Roblox green color for embeds

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Helper function to create consistent embeds
def create_embed(title, description=None, fields=None, thumbnail=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=ROBLOX_GREEN,
        timestamp=datetime.now()
    )
    
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
        
    embed.set_footer(text="Roblox Discord Bot", 
                    icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Roblox_player_icon_black.svg/1200px-Roblox_player_icon_black.svg.png")
    
    return embed

# Roblox API helper functions
async def get_roblox_user(username):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.roblox.com/users/get-by-username?username={username}") as response:
            if response.status == 200:
                data = await response.json()
                if "Id" in data:
                    return data
            return None

async def get_roblox_avatar(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png") as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["imageUrl"]
            return None

async def get_game_details(game_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://games.roblox.com/v1/games?universeIds={game_id}") as response:
            if response.status == 200:
                data = await response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]
            return None

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash Commands
@bot.tree.command(name="profile", description="Look up a Roblox profile")
async def profile(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    user_data = await get_roblox_user(username)
    if not user_data:
        embed = create_embed("Error", f"Could not find Roblox user: {username}")
        await interaction.followup.send(embed=embed)
        return
    
    user_id = user_data["Id"]
    avatar_url = await get_roblox_avatar(user_id)
    
    fields = [
        ("User ID", str(user_id), True),
        ("Profile", f"[View Profile](https://roblox.com/users/{user_id}/profile)", True),
        ("Created", user_data.get("Created", "Unknown"), True)
    ]
    
    embed = create_embed(
        f"Roblox Profile: {user_data['Username']}", 
        description=f"Information about {user_data['Username']}", 
        fields=fields,
        thumbnail=avatar_url
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="game", description="Get information about a Roblox game")
async def game(interaction: discord.Interaction, game_id: int):
    await interaction.response.defer()
    
    game_data = await get_game_details(game_id)
    if not game_data:
        embed = create_embed("Error", f"Could not find Roblox game with ID: {game_id}")
        await interaction.followup.send(embed=embed)
        return
    
    fields = [
        ("Creator", game_data.get("creator", {}).get("name", "Unknown"), True),
        ("Playing", f"{game_data.get('playing', 0):,}", True),
        ("Visits", f"{game_data.get('visits', 0):,}", True),
        ("Created", game_data.get("created", "Unknown"), True),
        ("Updated", game_data.get("updated", "Unknown"), True),
        ("Max Players", str(game_data.get("maxPlayers", "Unknown")), True),
    ]
    
    embed = create_embed(
        f"Roblox Game: {game_data.get('name', 'Unknown')}", 
        description=game_data.get("description", "No description available"),
        fields=fields,
        thumbnail=game_data.get("iconImageUrl")
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="verify", description="Verify your Roblox account")
async def verify(interaction: discord.Interaction):
    embed = create_embed(
        "Roblox Verification", 
        "To verify your Roblox account, please follow these steps:\n\n"
        "1. Click the button below to start the verification process\n"
        "2. You'll be asked to enter your Roblox username\n"
        "3. You'll need to add a verification code to your profile\n"
        "4. Once verified, you'll receive roles based on your Roblox groups"
    )
    
    # In a real bot, you would implement buttons here
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roles", description="Set up automatic roles based on Roblox groups")
@app_commands.default_permissions(administrator=True)
async def roles(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        embed = create_embed("Error", "You need administrator permissions to use this command.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = create_embed(
        "Roblox Group Roles Setup", 
        "This command allows you to configure automatic role assignment based on Roblox groups.\n\n"
        "Use the following subcommands:\n"
        "• `/roles add <group_id> <rank_id> <discord_role>` - Add a role mapping\n"
        "• `/roles remove <group_id> <rank_id>` - Remove a role mapping\n"
        "• `/roles list` - List all current role mappings"
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    commands = [
        {"name": "/profile <username>", "description": "Look up a Roblox profile"},
        {"name": "/game <game_id>", "description": "Get information about a Roblox game"},
        {"name": "/verify", "description": "Verify your Roblox account"},
        {"name": "/roles", "description": "Set up automatic roles based on Roblox groups (Admin only)"},
        {"name": "/help", "description": "Show this help message"}
    ]
    
    fields = []
    for cmd in commands:
        fields.append((cmd["name"], cmd["description"], False))
    
    embed = create_embed(
        "Roblox Discord Bot - Help", 
        "Here are all the available commands:",
        fields=fields
    )
    
    await interaction.response.send_message(embed=embed)

# Run the bot
bot.run(os.environ.get('DISCORD_TOKEN'))
