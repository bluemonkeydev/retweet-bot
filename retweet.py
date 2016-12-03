#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, ConfigParser, tweepy, inspect, hashlib, time
from random import randint

# blacklisted users and words
userBlacklist = []
wordBlacklist = ["RT", u"♺"]

def getLastId(queryString):
  # build savepoint path + file
  hashedHashtag = hashlib.md5(queryString).hexdigest()
  last_id_filename = "last_id_hashtag_%s" % hashedHashtag
  rt_bot_path = os.path.dirname(os.path.abspath(__file__))
  last_id_file = os.path.join(rt_bot_path, last_id_filename)

  # retrieve last savepoint if available
  try:
    with open(last_id_file, "r") as file:
      return file.read()
  except IOError:
    print "No savepoint found."
    return ""
# end def

def setLastId(queryString, last_tweet_id):
  # build savepoint path + file
  hashedHashtag = hashlib.md5(queryString).hexdigest()
  last_id_filename = "last_id_hashtag_%s" % hashedHashtag
  rt_bot_path = os.path.dirname(os.path.abspath(__file__))
  last_id_file = os.path.join(rt_bot_path, last_id_filename)

  # write last retweeted tweet id to file
  with open(last_id_file, "w") as file:
   file.write(str(last_tweet_id))
# end def

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# read config
config = ConfigParser.SafeConfigParser()
config.read(os.path.join(path, "config"))

hashtags = config.get("settings","search_query")
usernames = config.get("settings","usernames")

tweetLanguage = ""
if (config.has_option("settings","tweet_language")):
  tweetLanguage = config.get("settings","tweet_language")

maxretweets = 15
if (config.has_option("settings","max_retweets")):
  maxretweets = config.getint("settings","max_retweets")

tweetsPerQuery = 10
if (config.has_option("settings","tweets_per_query")):
  tweetsPerQuery = config.getint("settings","tweets_per_query")

randomdelay = 0
if (config.has_option("settings","random_delay")):
  randomdelay = config.getint("settings","random_delay")

favorite = "no"
if (config.has_option("settings","favorite")):
  favorite = config.get("settings","favorite").lower()

# pick a delay
randomdelay = randint(0,randomdelay)

print ("delay (min): " + str(randomdelay))
time.sleep(randomdelay * 60)

# create bot
auth = tweepy.OAuthHandler(config.get("twitter","consumer_key"), config.get("twitter","consumer_secret"))
auth.set_access_token(config.get("twitter","access_token"), config.get("twitter","access_token_secret"))
api = tweepy.API(auth)

timeline = []

# users
for username in usernames.split(","):
  username = username.strip()
  if len(username) == 0:
    continue

  savepoint = getLastId(username)

  # bug in the "since_id", if blank it fails.
  if savepoint != "":
    timelineIterator = tweepy.Cursor(api.user_timeline, id=username, since_id=savepoint).items(tweetsPerQuery)
  else:
    timelineIterator = tweepy.Cursor(api.user_timeline, id=username).items(tweetsPerQuery)

  for status in timelineIterator:
    timeline.append(status)

  try:
    last_tweet_id = timeline[0].id
  except IndexError:
    last_tweet_id = savepoint

  setLastId(username, last_tweet_id)
# end username loop

# search/hashtag
for hashtag in hashtags.split(","):
  hashtag = hashtag.strip()
  if len(hashtag) == 0:
    continue

  savepoint = getLastId(hashtag)

  timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint, lang=tweetLanguage).items(tweetsPerQuery)

  for status in timelineIterator:
    timeline.append(status)

  try:
    last_tweet_id = timeline[0].id
  except IndexError:
    last_tweet_id = savepoint

  setLastId(hashtag, last_tweet_id)
# end search/hashtag loop

# filter @replies/blacklisted words & users out and reverse timeline
timeline = filter(lambda status: status.text[0] != "@", timeline)
timeline = filter(lambda status: not any(word in status.text.split() for word in wordBlacklist), timeline)
timeline = filter(lambda status: status.author.screen_name not in userBlacklist, timeline)
timeline.reverse()

tw_counter = 0
err_counter = 0

# iterate the timeline and retweet
print "total tweets: " + str(len(timeline))
for status in timeline:
  try:
    print "%(id)s: (%(date)s) %(name)s: %(message)s\n" % \
      { "id" : status.id,
      "date" : status.created_at,
      "name" : status.author.screen_name.encode('utf-8'),
      "message" : status.text.encode('utf-8') }

    # wait 0 to 2 minutes for each re-tweet
    waiting = randint(0,2*60)
    print("waiting: " + str(waiting))
    time.sleep(waiting)
    api.retweet(status.id)

    if (favorite == "yes"):
      api.create_favorite(id)
      pass
    
    tw_counter += 1
    if tw_counter >= maxretweets:
      break;
  except tweepy.error.TweepError as e:
    # just in case tweet got deleted in the meantime or already retweeted
    err_counter += 1
    #print e
    continue
# end timeline loop

print "Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter)

