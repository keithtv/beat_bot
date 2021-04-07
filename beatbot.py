import twitterFunctions
import spotifyFunctions
import time
import datetime
import urllib.request

# Return current time - used for logging
def getCurrentTime():
    t = time.localtime()
    current_time = time.strftime("%d/%m/%Y %H:%M:%S", t)
    return current_time


# Write a string to a log file, also prints to console
def writelog(file, log):
    logfile = open(file, 'a')
    logfile.write('\n')
    logfile.write(log)
    logfile.close()
    print(log)

if __name__ == "__main__":

    #perform initial connectivity check
    while True:
        try:
            print("Checking internet connectivity")
            urllib.request.urlopen("http://www.spotify.com")
            urllib.request.urlopen("http://www.twitter.com")
            break
        except:
            print('Connectivity check failed - trying again in 10 seconds...')
            time.sleep(10)

    print("Connectivity check successful.")

    startTime = datetime.datetime.now()

    # Create authentication tokens
    twitterLogin = twitterFunctions.twitterauthentication()
    spotifyLogin = spotifyFunctions.spotifyauthentication('user-read-playback-state user-modify-playback-state')

    # Get the last mention and last status
    lastMentionID = twitterFunctions.getlastmention(twitterLogin)
    lastTweetID = twitterFunctions.getlasttweetid(twitterLogin)

    token_Expiration = 0

    # Start process in while loop - run indefinitely
    while True:
        # Create new authentication tokens periodically - every 30 min
        if (token_Expiration - time.time()) < 60:
            print("Token is expiring in <1 min, refreshing token.")
            try:
                spotifyLogin, token_Expiration = spotifyFunctions.spotifyauthentication(
                    'user-read-playback-state user-modify-playback-state')
                print("Authentication Token Renewed.  Expires at: " + str(token_Expiration))
                writelog('controllerlog', getCurrentTime() + ": Created new Spotify authentication token.")
            except:
                writelog('controllerlog', getCurrentTime() + ": Something went wrong in renewing Spotify token.")

        # Log status
        writelog('controllerlog', getCurrentTime() + ": Looking for new tweets.")

        # Get latest tweets - if tweets are found, reply to them and add request to playlist if tweet is valid
        tweets = twitterFunctions.checktweets(twitterLogin, lastMentionID, startTime)
        if len(tweets) > 0:
            for tweet in tweets:
                if tweet['message'] == "INVALID":
                    twitterFunctions.replytorequest(twitterLogin, tweet['id'], "I couldn't understand your request.")
                else:
                    # Valid tweet - try adding to spotify playlist.  If successful reply to  user.
                    try:
                        DeviceID = spotifyFunctions.getDeviceID(spotifyLogin)
                        if spotifyFunctions.addToPlaylist(tweet['message'][0], tweet['message'][1], spotifyLogin, DeviceID) == True:
                            twitterFunctions.replytorequest(twitterLogin, tweet['id'], "Your request has been added to the playlist.")
                            writelog('controllerlog',
                                     getCurrentTime() + ": A new request was added to the playlist:" + tweet['message'][
                                         0] + "-" + tweet['message'][1])
                        else:
                            twitterFunctions.replytorequest(twitterLogin, tweet['id'], "I am not listening right now. Please try again later.")
                    except IndexError:
                        # If unsuccessful, notify user and continue.
                        twitterFunctions.replytorequest(twitterLogin, tweet['id'], "Hmmm, I don't know that one.")
                    except Exception as err:
                        print(err)

            lastMentionID = tweets[len(tweets)-1]['id']
        else:
            writelog('controllerlog', getCurrentTime() + ": No new tweets found.")
        # Sleep for 3 sec to allow spotify/twitter to update
        time.sleep(5)

        # Check on currently playing song, update status if a new song is playing.
        try:
            # try to get the currently playng song
            currentlyPlaying = spotifyFunctions.getCurrentlyPLaying(spotifyLogin)
        except:
            # failure may occur if no devices are active on spotify -
            # in that case sleep the process then continue initial "while" loop.
            time.sleep(25)
            continue

        # Get the last "currently playing" status, compare to what's playing now.  Update status if song has changed.
        lasttweettext = twitterFunctions.getlasttweetsince(twitterLogin, lastMentionID)
        if lasttweettext != ("Currently Playing - " + currentlyPlaying):
            newstatus = "Currently Playing - " + currentlyPlaying
            try:
                twitterFunctions.updateStatus(twitterLogin, newstatus)
                writelog('controllerlog', getCurrentTime() + ": New song playing - Status Updated.")
            except twitterFunctions.tw.error.TweepError:
                # If song was played recently Twitter will not allow an identical status update so quickly...
                # In that case a retweet of the matching tweet will be made...
                # If that tweet has already been retweeted, then we will have to skip this status update.
                writelog('controllerlog', getCurrentTime() + ": A duplicate status was found - attempting retweet.")
                matchingID = twitterFunctions.searchtweet(twitterLogin, newstatus)
                try:
                    twitterFunctions.retweet(twitterLogin, matchingID)
                    writelog('controllerlog', getCurrentTime() + ": Retweet successful.")
                except:
                    writelog('controllerlog', getCurrentTime() + ": Retweet failed - skipping this status update.")
                time.sleep(25)
                continue
        else:
            writelog('controllerlog', getCurrentTime() + ": Status is current - no need to update.")
        time.sleep(25)
