import asyncio
import datetime
import logging
import os
import time
import subprocess


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from telegram_helper import send_music, send_post

# Set up your Spotify API credentials
client_id = '5f2fb8894e464653bd0c2fbd81e957a6'
client_secret = '789ef1750b48450ab767e7b44eb6f2c7'
bot_token = '5927525345:AAFNHk_jxBQXof3UEW2I--3zG71485Dnh1E'
chat_id = '@EclecticEuphoria'
interval = 15

# Initialize the Spotify API client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Define the Spotify playlist URI or URL
playlist_uri = 'https://open.spotify.com/playlist/0nixvGXVVYy23KDUD09e4y?si=88d8a7433512415a'


async def check_recently_added_tracks(playlist_uri):
    # Retrieve the current state of the playlist
    results = spotify.playlist_items(playlist_uri)

    # Get the current time in UTC
    current_time = datetime.datetime.utcnow()

    # Extract the track information from the retrieved tracks
    for track in results['items']:
        track_name = track['track']['name']
        added_at = track['added_at']
        artist_name = track['track']['artists'][0]['name']
        url = track['track']['external_urls']['spotify']
        path = f"./{artist_name} - {track_name}.mp3"

        # Convert the added_at timestamp to a datetime object
        added_time = datetime.datetime.strptime(added_at, "%Y-%m-%dT%H:%M:%SZ")

        # Calculate the time difference between current_time and added_time
        time_difference = current_time - added_time
        # Check if the track was added within the last 10 seconds
        if time_difference.total_seconds() <= interval:
            print(f"Recently added track: {track_name}")
            logging.info(f"Recently added track: {track_name}")
            await asyncio.run(download_and_send(url, path))

    time.sleep(interval)
    await check_recently_added_tracks(playlist_uri)


async def download_and_send(url, path):
    command = f"python -m spotdl {url}"
    logging.info(f"download is starting: {path}")
    process = await asyncio.create_subprocess_shell(command)
    await process.communicate()
    logging.info(f"sending: {path}")
    asyncio.run(send_music(bot_token, chat_id, path))
    # remove file after sending
    logging.info(f"removing: {path}")
    os.remove(path)
    return path


if __name__ == '__main__':
    # print_hi('PyCharm')

    asyncio.run(check_recently_added_tracks(playlist_uri))
    # asyncio.run(send_music(bot_token, chat_id, './music.mp3'))
    # send_audio(bot_token, chat_id, './music.mp3')
