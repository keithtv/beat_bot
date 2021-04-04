import tweepy as tw
import yaml

with open("beatbot_vars.yml") as f:
    tokendata = yaml.safe_load(f)

twitter_handle = tokendata["twitter"]["twitter_handle"]

# Create and return Twitter authentication token
def twitterauthentication():
    consumer_key = tokendata["twitter"]["consumer_key"]
    consumer_secret = tokendata["twitter"]["consumer_secret"]
    access_token = tokendata["twitter"]["access_token"]
    access_secret = tokendata["twitter"]["access_secret"]

    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    TwitterToken = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return TwitterToken


# Return the last tweet in which you were mentioned (@username)
def getlastmention(twitterSession):
    session = twitterSession
    last_id = 0
    mentions = session.mentions_timeline(count=1)

    for message in mentions:
        last_id = message.id
        return last_id


# Return a list of all tweets requesting songs.
# Each tweet is dictionary - tweets in incorrect format are returned as 'INVALID'
def checktweets(twittersession, messageid, time):
    session = twittersession
    last_id = messageid
    starttime = time

    tweets = []

    mentions = session.mentions_timeline(since_id=last_id, count=999)

    for message in mentions:
        messagetext = message.text.upper().replace(str(twitter_handle).upper(), '').split("-")
        if len(messagetext) > 1 and message.created_at >= starttime:
            tweets.append({'id': message.id, 'message': messagetext})
        elif message.created_at < starttime:
            continue
        else:
            tweets.append({'id': message.id, 'message': "INVALID"})

    return tweets


# Reply to requestor that request was succesful or unsuccessful.
def replytorequest(twittersession, messageid, message):
    session = twittersession
    try:
        session.update_status(message, in_reply_to_status_id=messageid,
                              auto_populate_reply_metadata=True)
    except tw.TweepError as err:
        print(err)
    except Exception as err:
        print(err)


# Return the ID of the last tweet that was sent out
def getlasttweetid(twittersession):
    session = twittersession
    lasttweet = session.user_timeline(count=1)
    for tweet in lasttweet:
        lasttweetmessage = tweet.text

    return lasttweetmessage


# Return the ID of the last tweet sent out that wasn't a reply to a user request
def getlasttweetsince(twittersession, tweetID):
    statuslist = []
    session = twittersession
    timeline = session.user_timeline(count=100)
    for message in timeline:
        post = message.text
        if post.startswith("Currently Playing"):
            statuslist.append(post)
    return statuslist[0]


# Post a new status
def updateStatus(twittersession, newstatus):
    session = twittersession
    session.update_status(newstatus)


# Find a tweet matching a search string
def searchtweet(twittersession, tweetstring):
    session = twittersession
    matchingTweets = []
    matches = session.search(tweetstring)
    for tweet in matches:
        matchingTweets.append(tweet)
    return matchingTweets[0].id


# Retweet a tweet matching tweetID
def retweet(twittersession, tweetID):
    session = twittersession
    session.retweet(tweetID)
