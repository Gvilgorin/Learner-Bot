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

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

# Tells the sever the bot is up and running and ready for use
@bot.event
async def on_ready():
    print("Hello! bot is ready!")

# Bot greets users who invokes command (!hello)
@bot.command()
async def hello(ctx):
    await ctx.reply("Hello there!")

# Coin flip fuction - It flips a freaking coin what else should I say command(!flip)
@bot.command()
async def flip(ctx):
    num = random.randint(1,2)
    if num == 1:
        await ctx.send("Heads!")
    elif num == 2:
        await ctx.send("Tails!")

@bot.command()
async def cats(ctx):
    query = "cats"
    headers = {"Ocp-Apim-Subscription-key": BING_API_KEY}
    params = {"q":query, "count": 90} 

    url = "https://api.bing.microsoft.com/v7.0/images/search"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        await ctx.send("Failed to retrieve images. Please try again later.")
        return
    
    data = response.json()

    if 'value' not in data or len(data['value']) == 0:
        await ctx.send("No images found for cats.")
        return
    
    random_image = random.choice(data['value'])
    image_url = random_image['contentUrl']

    await ctx.send(image_url )

@bot.command()
async def image(ctx, *, query):
    headers = {"Ocp-Apim-Subscription-key": BING_API_KEY}
    params = {"q":query, "count": 90}

    url = "https://api.bing.microsoft.com/v7.0/images/search"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        await ctx.send("Failed to retrieve images. Please try again later.")
        return
    
    data = response.json()

    if 'value' not in data or len(data['value']) == 0:
        await ctx.send(f"No images found for '{query}'.")
        return
    
    random_image = random.choice(data['value'])
    image_url = random_image['contentUrl']

    await ctx.send(image_url )

@bot.command()
async def poodle(ctx):
    query = "poodles"
    headers = {"Ocp-Apim-Subscription-key": BING_API_KEY}
    params = {"q":query, "count": 90} 

    url = "https://api.bing.microsoft.com/v7.0/images/search"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        await ctx.send("Failed to retrieve images. Please try again later.")
        return
    
    data = response.json()

    if 'value' not in data or len(data['value']) == 0:
        await ctx.send("No images found for poodles.")
        return
    
    random_image = random.choice(data['value'])
    image_url = random_image['contentUrl']

    await ctx.send(image_url )

async def main():
    async with bot:
        await bot.load_extension('music')
        await bot.start(BOT_TOKEN)

asyncio.run(main())