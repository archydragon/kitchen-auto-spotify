import logging
import sys
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
        raise Exception('no devices online')
    for dev in devices['devices']:
        if dev['name'] == device_name:
            device_id = dev['id']
            break
    if not device_id:
        raise Exception(f"device '{device_name}' is not online")
    return device_id

def play(config=None):
    """
    Main function to start playing random music on configured device.
    """
    # Enable logging.
    log = logging.getLogger('root')
    # Read config.
    if not config:
        config = read_config()
    # Get Spotify Oauth2 token.
    access_token = get_valid_access_token()
    # Create a new Spotify API client based on the token we have.
    client = spotipy.Spotify(auth=access_token)
    log.debug("Spotify client created.")

    # Find the device to play music on.
    try:
        device_id = get_device_id(client, config['device_name'])
    except Exception as e:
        log.critical(f"Failed to get Spotify device ID: {e}")
        return False

    # Check if playback is active now.
    playback = client.current_playback()
    if playback and 'is_playing' in playback and playback['is_playing']:
        log.info("Playing something somewhere already.")
        return False

    # Get a random category and a random playlist from it.
    category = None
    playlist = None
    while not category or not playlist:
        # Some categories might have no playlist in defined region or at all, need to skip them. Happens.
        try:
            categories_resp = client.categories(limit=50, country=config['country'])
            log.debug(f"Found {len(categories_resp['categories']['items'])} categories.")
            category = choice(categories_resp['categories']['items'])
            log.info(f"Category: {category['name']}")

            playlists_resp = client.category_playlists(category_id=category['id'], country=config['country'])
            log.debug(f"Found {len(playlists_resp['playlists']['items'])} playlists in the category.")
            playlist = choice(playlists_resp['playlists']['items'])
            log.info(f"Playlist: {playlist['name']}")
        except IndexError:
            log.info("Found some category with no playlists, skipping.")

    # Enable shuffle.
    log.debug("Enabling shuffle.")
    client.shuffle(config['shuffle'], device_id=device_id)
    # Set volumne.
    log.debug(f"Setting volume to {config['volume']}.")
    client.volume(config['volume'], device_id=device_id)
    # Start actual playback of the playlist we found before.
    log.info(f"Starting playback.")
    client.start_playback(device_id=device_id, context_uri=playlist['uri'])
    return True

def pause(config=None):
    """
    A helper to pause playback.
    """
    # Enable logging.
    log = logging.getLogger('root')
    # Read config.
    if not config:
        config = read_config()

    # Get Spotify Oauth2 token.
    access_token = get_valid_access_token()
    # Create a new Spotify API client based on the token we have.
    client = spotipy.Spotify(auth=access_token)
    log.debug("Spotify client created.")

    # Find the device to play music on.
    try:
        device_id = get_device_id(client, config['device_name'])
    except Exception as e:
        log.critical(f"Failed to get Spotify device ID: {e}")
        return

    # Check if playback is active now. If it is, stahp.
    # The latest condition is needed to silence only if music still plays on controlled device.
    playback = client.current_playback()
    if playback and 'is_playing' in playback and playback['is_playing'] and playback['device']['id'] == device_id:
        log.info("Stopping playback.")
        client.pause_playback(device_id)
        return

if __name__ == '__main__':
    play()
