import tweepy
import os
from dotenv import load_dotenv
load_dotenv()

class TwitterApi:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    def client(self):
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        # 認証
        return tweepy.API(auth)
    
    # 対象ユーザーのリツイートとリプライを除外した上で最新ツイートを1件取得
    def get_user_recent_tweet(self, screen_name):
        return self.client().user_timeline(screen_name = screen_name, count = 1, include_rts = False, exclude_replies = True)[0]
