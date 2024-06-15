import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import time

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
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration') 

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.song_list = []
        self.current_player = None
        self.start_time = None
        self.play_next_song = True

    # This add a join command for the bot to join the selected uses channel
    @commands.command()
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return
        
        channel = ctx.message.author.voice.channel
        await channel.connect()

    # Fuction to allow users to disconnect bot from voice channel
    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def add(self, ctx, *, song_name):
        self.song_list.append(song_name)
        await ctx.reply(f"{song_name} added to queue!")
        
    @commands.command()
    async def queue(self, ctx):
        if not self.song_list:
            await ctx.send("The queue is currently empty.")
            return
        
        embed = discord.Embed(title="Current song(s) in queue", color=discord.Color.blue())
        for i, song in enumerate(self.song_list, start=1):
            embed.add_field(name=f"{i}. {song}", value="\u200b", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, song_num: int):
        index = song_num - 1
        if 0 <= index < len(self.song_list):
            removed_song = self.song_list.pop(index)
            await ctx.send(f"'{removed_song}' has been removed from the queue")
        else:
            await ctx.send("Please only enter a song queue position to be removed")

    @commands.command()
    async def clear(self, ctx):
        self.song_list.clear()
        await ctx.send("all songs have been cleared from the queue")

    @commands.command()
    async def play(self, ctx):
        if not self.song_list:
            await ctx.send("The queue is currently empty.")
            return

        if not ctx.voice_client:
            if ctx.message.author.voice:
                channel = ctx.message.author.voice.channel
                await channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel")
                return

        self.play_next_song = True
        await self._play_song(ctx)

    async def _play_song(self, ctx):
        if not self.song_list:
            await ctx.send("No more songs in the queue.")
            return
        
        if not self.play_next_song:
            return
        
        async with ctx.typing():
            try:
                song_name = self.song_list.pop(0)
                self.current_player = await YTDLSource.from_url(f"ytsearch:{song_name}", loop=self.bot.loop, stream=True)
                ctx.voice_client.play(self.current_player, after=lambda e: self.bot.loop.create_task(self._play_song(ctx)))
                self.start_time = time.time()
                await ctx.send(f'Now playing: {self.current_player.title} ({self.current_player.duration // 60}:{self.current_player.duration % 60})')
            except Exception as e:
                await ctx.send(f'An error occurred: {e}')
                print(f'An error occurred while trying to play the song: {e}')

    @commands.command()
    async def stop(self, ctx):
        self.play_next_song = False
        if ctx.voice_client:
            ctx.voice_client.stop()
        
    @commands.command()
    async def skip(self, ctx):
        if not self.song_list:
            await ctx.send('Cannot skip, the queue is empty.')
            return

        # Stop the current song if playing
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command(aliases=['np', 'now playing'])
    async def now_playing(self, ctx):
        if not self.current_player:
            await ctx.send("No song is currently playing.")
            return
        
        elapsed_time = int(time.time() - self.start_time)
        total_duration = self.current_player.duration

        await ctx.send(f"Now playing: {self.current_player.title}\n"
               f"Duration: {total_duration // 60}:{total_duration % 60}\n"
               f"Elapsed time: {elapsed_time // 60}:{elapsed_time % 60}")


async def setup(bot):
    await bot.add_cog(Music(bot))
