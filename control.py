import sys
from datetime import datetime
from random import choice
import spotipy
from auth import get_valid_access_token
from config import read_config


def get_device_id(client, device_name):
    """
    Helper function to get device ID by its name.
    """
    devices = client.devices()
    device_id = None
    if not devices or not 'devices' in devices or len(devices['devices']) == 0:
        raise Exception('No Spotify devices online.')
    for dev in devices['devices']:
        if dev['name'] == device_name:
            device_id = dev['id']
            break
    if not device_id:
        raise Exception(f"Device '{device_name}' is not online.")
    return device_id

def play(config=None):
    """
    Main function to start playing random music on configured device.
    """
    # Read config.
    if not config:
        config = read_config()
    # Get Spotify Oauth2 token.
    access_token = get_valid_access_token()
    # Create a new Spotify API client based on the token we have.
    client = spotipy.Spotify(auth=access_token)

    # If night mode is configured, check if it is not too late.
    if 'night_starts' in config and 'night_ends' in config:
        now = datetime.now()
        pns = datetime.strptime(config['night_starts'], '%H:%M')
        pne = datetime.strptime(config['night_ends'], '%H:%M')
        night_starts = datetime.now().replace(hour=pns.hour, minute=pns.minute, second=0, microsecond=0)
        night_ends = datetime.now().replace(hour=pne.hour, minute=pne.minute, second=0, microsecond=0)
        # If it's later than night start timestamp.
        if night_starts <= now:
            # If night starts before midnight, it should end the next day.
            if night_starts > night_ends:
                night_ends = night_ends.replace(day=night_ends.day+1)
            # If the night not ended yet, quit.
            if night_ends >= now:
                print("It's too late, don't do anything.")
                return
        # Otherwise check if it's earlier than night end timestamp and exit if it is true.
        elif night_ends >= now:
            print("It's too late, don't do anything.")
            return

    # Find the device to play music on.
    device_id = get_device_id(client, config['device_name'])

    # Check if playback is active now.
    playback = client.current_playback()
    if playback and 'is_playing' in playback and playback['is_playing']:
        print("Playing something somewhere already.")
        return

    # Get a random category and a random playlist from it.
    category = None
    playlist = None
    while not category or not playlist:
        # Some categories might have no playlist in defined region or at all, need to skip them. Happens.
        try:
            categories_resp = client.categories(limit=50, country=config['country'])
            category = choice(categories_resp['categories']['items'])
            playlists_resp = client.category_playlists(category_id=category['id'], country=config['country'])
            playlist = choice(playlists_resp['playlists']['items'])
        except IndexError:
            print("Found some category with no playlists, skipping.")

    print("Category:", category['name'])
    print("Playlist:", playlist['name'])
    print("Starting playback...")

    # Enable shuffle.
    client.shuffle(config['shuffle'], device_id=device_id)
    # Set volumne.
    client.volume(config['volume'], device_id=device_id)
    # Start actual playback of the playlist we found before.
    client.start_playback(device_id=device_id, context_uri=playlist['uri'])

def pause(config=None):
    """
    A helper to pause playback.
    """
    if not config:
        config = read_config()

    # Get Spotify Oauth2 token.
    access_token = get_valid_access_token()
    # Create a new Spotify API client based on the token we have.
    client = spotipy.Spotify(auth=access_token)

    # Find the device we need to silence.
    device_id = get_device_id(client, config['device_name'])

    # Check if playback is active now. If it is, stahp.
    # The latest condition is needed to silence only if music still plays on controlled device.
    playback = client.current_playback()
    if playback and 'is_playing' in playback and playback['is_playing'] and playback['device']['id'] == device_id:
        print("Stopping playback.")
        client.pause_playback(device_id)
        return

if __name__ == '__main__':
    play()
