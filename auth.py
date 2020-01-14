import os
import yaml
import spotipy
from config import read_config


CONFIG_ROOT = os.path.expanduser("~/.config/kitchen")
TOKEN_INFO = os.path.join(CONFIG_ROOT, "token.yml")

API_SCOPES = 'user-read-playback-state,user-modify-playback-state,user-top-read,playlist-read-collaborative,app-remote-control'
FAKE_REDIRECT_URI = 'http://localhost:5500/'


def new_oauth(client_id, client_secret):
    """
    Creates a new Spotify Oauth2 object based on the defined configuration.
    """
    return spotipy.oauth2.SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = FAKE_REDIRECT_URI,
        scope = API_SCOPES,
    )

def new_token(client_id, client_secret):
    """
    Creates a new Spotify Oauth2 token based on the defined configuration.
    """
    oauth = new_oauth(client_id, client_secret)
    # Get new authentication URL and ask user to use it.
    # I'm too lazy to set up proper local HTTP server, and also it might be not that local.
    # So just ask user to copy generated URL from the browser and parse it.
    auth_url = oauth.get_authorize_url(show_dialog=True)
    print(auth_url)
    response = input('Paste the above link into your browser, then paste the redirect url here: ')
    code = oauth.parse_response_code(response)
    token_info = oauth.get_access_token(code)
    return token_info

def refresh_token(client_id, client_secret, refresh_token):
    """
    Refresh Spotify Oauth2 token.
    """
    oauth = new_oauth(client_id, client_secret)
    new_token_info = oauth.refresh_access_token(refresh_token)
    return new_token_info

def get_valid_access_token(config=None):
    """
    Get valid Spotify Oauth access token.
    """
    if not config:
        config = read_config()
    # Read Oauth token from saved file. If read fails, generate a new one.
    token_info = None
    try:
        with open(TOKEN_INFO, 'r') as file:
            token_info = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("No existing token file found, need to create a new one.")
        token_info = new_token(config['client_id'], config['client_secret'])
    # If the token has expired, refresh it.
    if spotipy.oauth2.is_token_expired(token_info):
        print("Token has expired, refreshing.")
        token_info = refresh_token(config['client_id'], config['client_secret'], token_info['refresh_token'])
    # Save token info to the file.
    with open(TOKEN_INFO, 'w') as file:
        yaml.dump(token_info, file)
    return token_info['access_token']

if __name__ == '__main__':
    get_valid_access_token()
