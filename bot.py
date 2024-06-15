import discord
from discord.ext import commands
import requests
import json, os, asyncio
import random

# Reads discord token from file
TOKEN_FILE = open('bot_token.txt', 'r')
BOT_TOKEN = TOKEN_FILE.read()
TOKEN_FILE.close() # closes file to open space

# Reads Bing API key from file
bing_file = open('bing_api_key.txt', 'r')
BING_API_KEY = bing_file.read()
bing_file.close() # closes file to open space

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

# Tells the sever the bot is up and running and ready for use
@bot.event
async def on_ready():
    print("Hello! bot is ready!")
    try:
        synced = await bot.tree.sync()
        print(f'Successfully synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

# Bot greets users who invokes command (!hello)
@tree.command(name="hello", description="Reply's to user with gretting")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there!")

# Coin flip fuction - It flips a freaking coin what else should I say command(!flip)
@tree.command(name="coin_flip", description="Flips a coin")
async def flip(interaction: discord.Interaction):
    num = random.randint(1,2)
    if num == 1:
        await interaction.response.send_message("Heads!")
    elif num == 2:
        await interaction.response.send_message("Tails!")

@tree.command(name="random_cat", description="Sends a picture of a random cat")
async def cats(interaction: discord.Interaction):
    query = "cats"
    headers = {"Ocp-Apim-Subscription-key": BING_API_KEY}
    params = {"q":query, "count": 90} 

    url = "https://api.bing.microsoft.com/v7.0/images/search"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        await interaction.response.send_message("Failed to retrieve images. Please try again later.")
        return
    
    data = response.json()

    if 'value' not in data or len(data['value']) == 0:
        await interaction.response.send_message("No images found for cats.")
        return
    
    random_image = random.choice(data['value'])
    image_url = random_image['contentUrl']

    await interaction.response.send_message(image_url )

@tree.command(name="image", description="Sends random picture user requests")
async def image(interaction: discord.Interaction, query: str):
    headers = {"Ocp-Apim-Subscription-key": BING_API_KEY}
    params = {"q":query, "count": 90}

    url = "https://api.bing.microsoft.com/v7.0/images/search"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        await interaction.response.send_message("Failed to retrieve images. Please try again later.")
        return
    
    data = response.json()

    if 'value' not in data or len(data['value']) == 0:
        await interaction.response.send_message(f"No images found for '{query}'.")
        return
    
    random_image = random.choice(data['value'])
    image_url = random_image['contentUrl']

    await interaction.response.send_message(image_url )

@tree.command(name="poodle", description="Send random photo of a poodle to chat")
async def poodle(interaction: discord.Interaction):
    query = "poodles"
    headers = {"Ocp-Apim-Subscription-key": BING_API_KEY}
    params = {"q":query, "count": 90} 

    url = "https://api.bing.microsoft.com/v7.0/images/search"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        await interaction.response.send_message("Failed to retrieve images. Please try again later.")
        return
    
    data = response.json()

    if 'value' not in data or len(data['value']) == 0:
        await interaction.response.send_message("No images found for poodles.")
        return
    
    random_image = random.choice(data['value'])
    image_url = random_image['contentUrl']

    await interaction.response.send_message(image_url )

async def main():
    async with bot:
        await bot.load_extension('music')
        await bot.start(BOT_TOKEN)

asyncio.run(main())