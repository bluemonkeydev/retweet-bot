Python Retweet Bot
==================

This script retweets all Tweets containing your search terms or usernames. To limit Twitter requests a savepoint file marks Tweets found before. It's Twitter API v1.1 ready.

How to start:
-------------
* Depends on http://tweepy.github.com/ (pip install tweepy)
* Copy 'config.sample' to 'config'
* Define your hashtag or search query
* Define your usernames
* Add your Twitter app credentials
* (Tune some other options if you like)
* $ python retweet.py
* Add this call to your crontab (or something similar) to retweet all new tweets regularly
