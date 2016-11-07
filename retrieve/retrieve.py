from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import MySQLdb
import sys
import time
import datetime

cnx = MySQLdb.connect(user='root', passwd='',
             host='127.0.0.1', db='wirdm', charset="utf8mb4")

#consumer key, consumer secret, access token, access secret.

ckey=""
csecret=""
atoken=""
asecret=""

sql = "replace INTO tweets (id, tweet, username, `timestamp`, lang, retweet_count, favorite_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"
sql2 = "replace into users (id, username, verified, created_at) values (%s, %s, %s, %s)"

count = 1
cursor = cnx.cursor()

def getReliabilityScore(username):

    sql = "select COMPUTED from users where username=%s"
    cursor.execute(sql, (username, ))

    if cursor.rowcount != 1:
        return 100;

    return cursor.fetchone()[0]

class listener(StreamListener):

    def on_data(self, data):
        global count

        all_data = json.loads(data)

        # Uncomment for removal of retweets
        if "quoted_status" in all_data:
            all_data = all_data["quoted_status"]

        # # Uncomment for removal of retweets
        if "retweeted_status" in all_data:
            all_data = all_data["retweeted_status"]

        # tweet_id = all_data["id_str"]
        tweet_id = all_data["id"]
        tweet = all_data["text"]
        username = all_data["user"]["screen_name"]
        verified = all_data["user"]["verified"]
        userid = all_data["user"]["id"]
        created = time.mktime(datetime.datetime.strptime(all_data["user"]["created_at"], "%a %b %d %H:%M:%S +0000 %Y").timetuple())

        retweet_count = all_data["retweet_count"]
        favorite_count = all_data["favorite_count"]
        # Sun Oct 16 00:06:16 +0000 2016
        timestamp_ms = 0;
        if "timestamp_ms" in all_data.keys():
            timestamp_ms = all_data["timestamp_ms"]
        else: 
            timestamp_ms = time.mktime(datetime.datetime.strptime(all_data["created_at"], "%a %b %d %H:%M:%S +0000 %Y").timetuple())*1000

        lang = all_data["lang"]

        cursor.execute(sql, (tweet_id, tweet, username, timestamp_ms, lang, retweet_count, favorite_count))
        cursor.execute(sql2, (userid, username, verified, created))
        cnx.commit()

        print ("Tweet added count: %i" % count)
        count = count + 1

        return True

    def on_error(self, status):
        print (status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["aleppo"])
