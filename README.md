<h1 align="center">
# Learner Bot
</h1>
This is a simple Discord bot that provides a few fun commands such as greeting users, flipping a coin, fetching random images of cats, poodles, or any other query from the Bing Image Search API, and playing music from YouTube.

### Prerequisites

- Python 3.6+
- `discord.py[voice]` library
- `requests` library
- `yt-dlp` library
- FFpmeg
- Bing API Key


## Features

- **Greeting:** The bot greets users with a friendly message.
- **Coin Flip:** The bot flips a coin and returns either "Heads!" or "Tails!".
- **Image Search:** The bot fetches random images based on the provided query using the Bing Image Search API.
- **Music Playback:** The bot can join voice channels and play music from YouTube, along with other music-related commands.

## Commands
- General Commands
    - /hello: The bot will greet the user.
    - /flip: The bot will flip a coin and return "Heads!" or "Tails!".
    - /cats: The bot will fetch a random image of a cat.
    - /image: [query]: The bot will fetch a random image based on the provided query.
    - /poodle: The bot will fetch a random image of a poodle.
## 
- Music Commands
    - /join: The bot will join the user's voice channel.
    - /leave: The bot will leave the current voice channel.
    - /add [song_name]: Add a song to the queue.
    - /queue: Display the current song queue.
    - /remove [song_num]: Remove a song from the queue by its position.
    - /clear: Clear all songs from the queue.
    - /play: Play the songs in the queue.
    - /stop: Stop the current song.
    - /skip: Skip the current song.
    - /now_playing: Display the currently playing song.


