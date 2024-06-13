import discord
from discord.ext import commands
import requests
import yt_dlp as youtube_dl
import asyncio
import json
import os
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
    # channel = bot.get_channel(CHANNEL_ID)
    # await channel.send("Hello, Learner bot is up and running :)")

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

"""
Bunch of fun code for the music commands for leaner bot!!! This should
be all the code needed to make joining, leaving, adding, removing, play,
stop, pause, clear, & now playing.
"""
# Youtube DL options
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # Bind to all available IPv4 addresses
}
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

song_list = []
# This add a join command for the bot to join the selected uses channel
@bot.command()
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    channel = ctx.message.author.voice.channel
    await channel.connect()

# Fuction to allow users to disconnect bot from voice channel
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def add(ctx, *, song_name):
    song_list.append(song_name)
    await ctx.reply(f"{song_name} added to queue!")
     
@bot.command()
async def queue(ctx):
    if not song_list:
        await ctx.send("The queue is currently empty.")
        return
    
    embed = discord.Embed(title="Current song(s) in queue", color=discord.Color.pink())
    for i, song in enumerate(song_list, start=1):
        embed.add_field(name=f"{i}. {song}", value="\u200b", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def remove(ctx, song_num):
    index = int(song_num) - 1
    if 0 <= index < len(song_list):
        removed_song = song_list.pop(index)
        await ctx.send(f"'{removed_song}' has been removed from the queue")
    else:
        await ctx.send("Please only enter a song queue position to be removed")

@bot.command()
async def clear(ctx):
    song_list.clear()
    await ctx.send("all songs have been cleared from the queue")

@bot.command()
async def play(ctx):
    if not song_list:
        await ctx.send("The queue is currently empty.")
        return

    if not ctx.voice_client:
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel")
            return

    async with ctx.typing():
        try:
            song_name = song_list.pop(0)  # Get the first song in the queue
            player = await YTDLSource.from_url(f"ytsearch:{song_name}", loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f'Now playing: {player.title}')
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()

bot.run(BOT_TOKEN)