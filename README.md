<h1 align="center">Learner Bot</h1>
This is a simple Discord bot that provides a few fun commands such as greeting users, flipping a coin, fetching random images of cats, poodles, or any other query from the Bing Image Search API, and playing music from YouTube.

# Prerequisites

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
    - `/hello`: The bot will greet the user.
    - `/flip`: The bot will flip a coin and return "Heads!" or "Tails!".
    - `/cats`: The bot will fetch a random image of a cat.
    - `/image`: [query]: The bot will fetch a random image based on the provided query.
    - `/poodle`: The bot will fetch a random image of a poodle.
## 
- Music Commands
    - `!join`: The bot will join the user's voice channel.
    - `!leave`: The bot will leave the current voice channel.
    - `!add [song_name]`: Add a song to the queue.
    - `!queue`: Display the current song queue.
    - `!remove [song_num]`: Remove a song from the queue by its position.
    - `!clear`: Clear all songs from the queue.
    - `!play`: Play the song(s) in the queue and resumes paused songs.
        - `!play [song_name]`: Plays song choice automaticlly if no song is in queue / adds song to queue if song is already playing
    - `!stop`: Stop the current song.
    - `!skip`: Skip the current song.
    - `!pause`: Pauses song that is currently playing
    - `!move [song_queue_position] [new_position]`: Moves song to new assigned position in queue
    - `!now_playing`: Display the currently playing song.

<!-- <h1 align="center">Terms of Service</h1>

## **Introduction**
Welcome to Learner Bot! By using Learner Bot, you agree to comply with and be bound by the following terms and conditions of use. Please review these terms carefully. If you disagree with these terms, you should not use this bot.

## **Usage**

1. Eligibility: You must be at least 13 years old to use this bot. By using this bot, you represent and warrant that you are at least 13 years of age.

2. License: We grant you a non-exclusive, non-transferable, revocable license to access and use the bot for its intended purpose.

3. Prohibited Uses: You agree not to use the bot for any unlawful purpose or in a way that could damage, disable, overburden, or impair the bot. Prohibited uses include, but are not limited to:

    - Harassment, abuse, or harm of another person.
    - Violating any local, state, national, or international law.
    - Interfering with or disrupting the bot or the servers or networks connected to the bot.
    - Attempting to gain unauthorized access to the bot, other accounts, computer systems, or networks connected to the bot.

## **Data Privacy**
1. User Data: The bot may collect certain information about you, such as your Discord username and messages you send to the bot. This information is used solely for the purpose of providing the bot's services and improving its functionality.

2. Third-Party Services: The bot may use third-party services (such as Bing Image Search) to provide certain features. These services have their own privacy policies, and we are not responsible for their practices.

## **Disclaimer of Warranties**
The bot is provided on an "as is" and "as available" basis. We do not warrant that the bot will be uninterrupted, error-free, or free of viruses or other harmful components. We disclaim all warranties, express or implied, including, but not limited to, implied warranties of merchantability and fitness for a particular purpose.

## **Limitation of Liability**
To the fullest extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses, resulting from:

- Your use of or inability to use the bot.
- Any unauthorized access to or use of our servers and/or any personal information stored therein.
- Any bugs, viruses, trojan horses, or the like that may be transmitted to or through the bot by any third party.
- Any errors or omissions in any content or for any loss or damage incurred as a result of the use of any content posted, emailed, transmitted, or otherwise made available through the bot.
## **Changes to Terms**
We reserve the right to modify these terms at any time. Any changes will be effective immediately upon posting of the revised terms. Your continued use of the bot following the posting of changes to these terms means you accept the changes.

## **Contact Information**
If you have any questions about these Terms of Service, please contact me via GitHub or join the [Discord](https://discord.gg/8gvubBdH) for support. -->




