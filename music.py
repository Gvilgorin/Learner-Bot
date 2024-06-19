import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotify_credentials import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

# Constant Variables
SONGS_PER_PAGE = 10

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

# Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

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
        self.current_song = None
        self.bot.queue_messages = {}

    async def ensure_voice(self, interaction):
        if not interaction.guild.voice_client:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
            else:
                await interaction.response.send_message("You are not connected to a voice channel")
                return False
        return True

    async def add_song_to_queue(self, interaction, song_name_or_url):
        async with interaction.channel.typing():
            try:
                youtube_url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
                spotify_url_pattern = re.compile(r'https://open\.spotify\.com/(track|playlist)/[a-zA-Z0-9]+')

                if youtube_url_pattern.match(song_name_or_url):
                    url = song_name_or_url
                    ytdl_source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                    song_title = ytdl_source.title

                    self.song_list.append({'title': song_title, 'url': url})
                    await interaction.response.send_message(f"'{song_title}' added to the queue!")
                    return song_title

                elif spotify_url_pattern.match(song_name_or_url):
                    if 'track' in song_name_or_url:
                        track_id = song_name_or_url.split('/')[-1].split('?')[0]
                        track = sp.track(track_id)
                        song_title = f"{track['name']} by {track['artists'][0]['name']}"
                        search_query = f"ytsearch:{song_title}"

                        self.song_list.append({'title': song_title, 'url': search_query})
                        await interaction.response.send_message(f"'{song_title}' added to the queue!")
                        return song_title

                    elif 'playlist' in song_name_or_url:
                        playlist_id = song_name_or_url.split('/')[-1].split('?')[0]
                        playlist = sp.playlist(playlist_id)
                        for item in playlist['tracks']['items']:
                            track = item['track']
                            song_title = f"{track['name']} by {track['artists'][0]['name']}"
                            search_query = f"ytsearch:{song_title}"
                            self.song_list.append({'title': song_title, 'url': search_query})
                        await interaction.response.send_message(f"Added {len(playlist['tracks']['items'])} songs from the playlist to the queue!")
                        return

                    # ytdl_source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                    # song_title = ytdl_source.title

                else:
                    search_query = f"ytsearch:{song_name_or_url}"
                    ytdl_source = await YTDLSource.from_url(search_query, loop=self.bot.loop, stream=True)
                    song_title = ytdl_source.title

                    self.song_list.append({'title': song_title, 'url': search_query})
                    await interaction.response.send_message(f"'{song_title}' added to the queue!")
                    return song_title
                
            except Exception as e:
                await interaction.response.send_message(f'An error occurred while adding the song: {e}')
                return None

    @app_commands.command(name="join", description="Joins the voice channel")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("You are not connected to a voice channel")
            return

        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Joined {channel.name}")

    @app_commands.command(name="leave", description="Leaves the voice channel")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel")
        else:
            await interaction.response.send_message("Not connected to any voice channel")

    @app_commands.command(name="add", description="Adds a song to the queue")
    @app_commands.describe(song_name_or_url="The name or URL of the song to add")
    async def add(self, interaction: discord.Interaction, song_name_or_url: str):
        await self.add_song_to_queue(interaction, song_name_or_url)

    @app_commands.command(name="queue", description="Displays the current song queue")
    @app_commands.describe(page="The page number of the queue to display")
    async def queue(self, interaction: discord.Interaction, page: int = 1):
        if not self.song_list and not self.current_song:
            await interaction.response.send_message("The queue is currently empty.")
            return

        total_pages = (len(self.song_list) - 1) // SONGS_PER_PAGE + 1
        if page < 1 or page > total_pages:
            await interaction.response.send_message(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
            return

        start_index = (page - 1) * SONGS_PER_PAGE
        end_index = start_index + SONGS_PER_PAGE

        embed = discord.Embed(title=f"Current song(s) in queue - Page {page}/{total_pages}", color=discord.Color.blue())
        if self.current_song:
            embed.add_field(name=f"Now playing: {self.current_song}", value="\u200b", inline=False)
        for i, song in enumerate(self.song_list[start_index:end_index], start=start_index + 1):
            embed.add_field(name=f"{i}. {song}", value="\u200b", inline=False)

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response() 
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        self.bot.queue_messages[message.id] = {'page': page, 'total_pages': total_pages}

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        message_id = reaction.message.id
        if message_id not in self.bot.queue_messages:
            return

        emoji = str(reaction.emoji)
        if emoji not in ["⬅️", "➡️"]:
            return

        queue_info = self.bot.queue_messages[message_id]
        current_page = queue_info['page']
        total_pages = queue_info['total_pages']

        if emoji == "⬅️":
            new_page = current_page - 1 if current_page > 1 else total_pages
        elif emoji == "➡️":
            new_page = current_page + 1 if current_page < total_pages else 1

        await self.update_queue_embed(reaction.message, new_page)

        # Remove the user's reaction to keep the reactions clean
        await reaction.message.remove_reaction(reaction.emoji, user)

    async def update_queue_embed(self, message, page):
        total_pages = self.bot.queue_messages[message.id]['total_pages']

        start_index = (page - 1) * SONGS_PER_PAGE
        end_index = start_index + SONGS_PER_PAGE

        embed = discord.Embed(title=f"Current song(s) in queue - Page {page}/{total_pages}", color=discord.Color.blue())
        if self.current_song:
            embed.add_field(name=f"Now playing: {self.current_song}", value="\u200b", inline=False)
        
        for i, song in enumerate(self.song_list[start_index:end_index], start=start_index + 1):
            embed.add_field(name=f"{i}. {song}", value="\u200b", inline=False)

        await message.edit(embed=embed)
        self.bot.queue_messages[message.id]['page'] = page



    @app_commands.command(name="remove", description="Removes a song from the queue")
    @app_commands.describe(song_num="The position of the song in the queue to remove")
    async def remove(self, interaction: discord.Interaction, song_num: int):
        index = song_num - 1
        if 0 <= index < len(self.song_list):
            removed_song = self.song_list.pop(index)
            await interaction.response.send_message(f"'{removed_song}' has been removed from the queue")
        else:
            await interaction.response.send_message("Please enter a valid song queue position to be removed")

    @app_commands.command(name="clear", description="Clears the entire song queue")
    async def clear(self, interaction: discord.Interaction):
        self.song_list.clear()
        await interaction.response.send_message("All songs have been cleared from the queue")

    @app_commands.command(name="play", description="Plays a song or resumes the current song")
    @app_commands.describe(song_name_or_url="The name or URL of the song to play")
    async def play(self, interaction: discord.Interaction, song_name_or_url: str = None):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("Resumed the paused song.")
            return

        if song_name_or_url:
            await self.add_song_to_queue(interaction, song_name_or_url)
            if not self.current_song:
                if await self.ensure_voice(interaction):
                    self.play_next_song = True
                    await self._play_song(interaction)
                return

        if not self.song_list and not self.current_song:
            await interaction.response.send_message("The queue is currently empty.")
            return

        if not self.current_song:
            if await self.ensure_voice(interaction):
                self.play_next_song = True
                await self._play_song(interaction)

    @app_commands.command(name="pause", description="Pauses the currently playing song")
    async def pause(self, interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("Playback has been paused.")
        else:
            await interaction.response.send_message("No song is currently playing.")

    async def _play_song(self, interaction: discord.Interaction):
        if not self.song_list:
            self.current_song = None
            if interaction.response.is_done():
                await interaction.followup.send("No more songs in the queue.")
            else:
                await interaction.response.send_message("No more songs in the queue.")
            return

        if not self.play_next_song:
            return

        async with interaction.channel.typing():
            try:
                song_info = self.song_list.pop(0)
                self.current_song = song_info['title']
                # Use the stored URL if available, otherwise use the search query
                song_url = song_info['url'] if 'url' in song_info else f"ytsearch:{song_info['title']}"
                self.current_player = await YTDLSource.from_url(song_url, loop=self.bot.loop, stream=True)
                interaction.guild.voice_client.play(self.current_player, after=lambda e: self.bot.loop.create_task(self._play_song(interaction)))
                self.start_time = time.time()
                now_playing_message = f'Now playing: {self.current_player.title} ({self.current_player.duration // 60}:{self.current_player.duration % 60})'
                if interaction.response.is_done():
                    await interaction.followup.send(content=now_playing_message)
                else:
                    await interaction.response.send_message(content=now_playing_message)
            except Exception as e:
                error_message = f'An error occurred: {e}'
                if interaction.response.is_done():
                    await interaction.followup.send(content=error_message)
                else:
                    await interaction.response.send_message(content=error_message)
                print(f'An error occurred while trying to play the song: {e}')


    @app_commands.command(name="stop", description="Stops the currently playing song")
    async def stop(self, interaction: discord.Interaction):
        self.play_next_song = False
        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()
        self.current_song = None
        await interaction.response.send_message("Stopped the song.")

    @app_commands.command(name="skip", description="Skips the currently playing song")
    async def skip(self, interaction: discord.Interaction):
        if not self.song_list and not self.current_song:
            await interaction.response.send_message('Cannot skip, the queue is empty.')
            return

        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()

        await interaction.response.send_message('Skipped the current song')

    @app_commands.command(name="move", description="Moves a song to a new position in the queue")
    @app_commands.describe(song_num="The current position of the song in the queue", new_position="The new position of the song in the queue")
    async def move(self, interaction: discord.Interaction, song_num: int, new_position: int):
        song_num -= 1
        new_position -= 1

        if not self.song_list:
            await interaction.response.send_message('Cannot move song in an empty queue')
            return

        if 0 <= song_num < len(self.song_list) and 0 <= new_position < len(self.song_list):
            temp = self.song_list.pop(song_num)
            self.song_list.insert(new_position, temp)
            await interaction.response.send_message(f"{temp} has been moved from {song_num + 1} to {new_position + 1}")
        else:
            await interaction.response.send_message("Make sure the new position is a valid number in the queue")

    @app_commands.command(name="now_playing", description="Displays the currently playing song")
    async def now_playing(self, interaction: discord.Interaction):
        if not self.current_player:
            await interaction.response.send_message("No song is currently playing.")
            return

        elapsed_time = int(time.time() - self.start_time)
        total_duration = self.current_player.duration

        await interaction.response.send_message(f"Now playing: {self.current_player.title}\n"
                                                f"Duration: {total_duration // 60}:{total_duration % 60}\n"
                                                f"Elapsed time: {elapsed_time // 60}:{elapsed_time % 60}")

async def setup(bot):
    await bot.add_cog(Music(bot))

