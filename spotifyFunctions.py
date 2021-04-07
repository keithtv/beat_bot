import spotipy
import spotipy.util as util
import yaml

#Create and return authentication token.  Scope defines permissions.
def spotifyauthentication(SpotifyScope):
    scope = SpotifyScope

    with open("beatbot_vars.yml") as f:
        tokendata = yaml.safe_load(f)

    token = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                          client_id=tokendata["spotify"]["client_id"],
                                          client_secret=tokendata["spotify"]["client_secret"],
                                          redirect_uri=tokendata["spotify"]["redirect_uri"])

    if token:
        url = token.get_auth_response()
        code = token.parse_response_code(url)
        token_info = token.get_access_token(code)
        accesstoken = token_info['access_token']
        sp = spotipy.Spotify(auth=accesstoken)
        token_expiration = token_info['expires_at']
    else:
        print("Can't get token for", tokendata["spotify"]["username"])
        return
    return sp, token_expiration


#Add track to playlists.  Requires Spotify token, track/artist name, and device ID
def addToPlaylist(artistName,trackName,spSession, deviceID):
    session = spSession
    artist = artistName
    track = trackName

    trackInfo = session.search(q='artist:' + artist + ' track:' + track, type='track')
    trackID = trackInfo['tracks']['items'][0]['uri']

    try:
        session.add_to_queue(uri=trackID, device_id=deviceID)
        return True
    except spotipy.SpotifyException:
        print("I found a requests but you're not actively listening.  I let the requester know.")
        return False


#Return track that is currently playing.  Requires Spotify token, track/artist name, and device ID
def getCurrentlyPLaying(spSession):
    session = spSession
    currentlyPlaying = session.current_playback()
    playingArtist = currentlyPlaying['item']['album']['artists'][0]['name']
    playingSong = currentlyPlaying['item']['name']
    arstistandsong = playingSong + " by " + playingArtist
    return(arstistandsong)


#Return active spotify device.  If none are active, default to desktop ID
def getDeviceID(spSession):
    session = spSession
    devcount = 0
    deviceID = None
    deviceInfo = session.devices()
    while devcount < len(deviceInfo['devices']):
        if deviceInfo['devices'][devcount]['is_active'] == True:
            deviceID = deviceInfo['devices'][devcount]['id']
        devcount = devcount + 1
    return deviceID
