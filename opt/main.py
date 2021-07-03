import datetime
from time import sleep
import traceback
import sys
import os
from dotenv import load_dotenv
load_dotenv()
from bybit_api import BybitAPI
from twitter_api import TwitterApi

# 対象の通貨名（表記ゆれを考慮して複数指定）
target_coin_names = [
    'ビットコイン',
    'bitcoin',
    'btc'
]

# 買い要因になりそうな単語（表記ゆれを考慮して複数指定）
positive_words = [
    '買い',
    'buy'
]

# 売り要因になりそうな単語（表記ゆれを考慮して複数指定）
negativewords = [
    '売り',
    'sell'
]

# Twitter API
twitter_api = TwitterApi()

# ツイートを監視する相手のユーザーID
screen_name = os.getenv('TWITTER_SCREEN_NAME')

# Bybit API
bybit_api = BybitAPI()

# 取引したい通貨ペア
symbol = 'BTC/USD'

# 注文量（USD）
amount = 1

# エントリー中かどうかのフラグ
entry_flag = False

# 決済予定時刻
close_time = None

print('Start!')

while True:
    try:
        # 現在時刻を算出
        now = datetime.datetime.now()
        
        if entry_flag == False:
            # ツイートを取得
            tweet = twitter_api.get_user_recent_tweet(screen_name)
            
            # ツイート内に対象の通貨名（条件1）＋買い要因or売り要因の単語（条件2）が含まれるかを確認（ex. ビットコイン 買い）
            # 条件1と条件2は必ずセットである必要があり、どちらか1つだけでは成立しない
            if any([target_coin_name in tweet.text.lower() for target_coin_name in target_coin_names]) \
                and any([positive_word in tweet.text.lower() for positive_word in positive_words]):
                
                # 成り行き買い注文
                order = bybit_api.create_order(symbol, 'market', 'buy', amount)
                print(f'Buy: {now}')
                
                # エントリーフラグをTrueに変更
                entry_flag = True

                # 決済予定時刻を設定（現在時刻から〇分後）※ minutesに指定する値は任意でOK
                close_time = now + datetime.timedelta(minutes = 5)
            
            elif any([target_coin_name in tweet.text.lower() for target_coin_name in target_coin_names]) \
                and any([negativeword in tweet.text.lower() for negativeword in negativewords]):
                
                # 成り行き売り注文
                order = bybit_api.create_order(symbol, 'market', 'sell', amount)
                print(f'Sell: {now}')

                # エントリーフラグをTrueに変更
                entry_flag = True

                # 決済予定時刻を設定（現在時刻から〇分後）※ minutesに指定する値は任意でOK
                close_time = now + datetime.timedelta(minutes = 5)
            
            else:
                # 無かった場合はパス
                pass

        else:
            # 現在時刻 > 決済予定時刻なら決済を行う
            if close_time != None and now > close_time:
                # 自分のポジション状況を確認
                position = bybit_api.get_position(symbol)

                # 買いポジションを持っていた場合は売り
                if position['side'] == 'Buy':
                    order = bybit_api.create_order(symbol, 'market', 'sell', amount)
                    print(f'Close: {now}')

                    # 決済が済んだらシステム終了
                    sys.exit()
                
                # 売りポジションを持っていた場合は買い
                elif position['side'] == 'Sell':
                    order = bybit_api.create_order(symbol, 'market', 'buy', amount)
                    print(f'Close: {now}')

                    # 決済が済んだらシステム終了
                    sys.exit()

                else:
                    # 何かの間違いで万が一ノーポジだった場合はパス
                    pass

            else:
                # 現在時刻 < 決済予定時刻ならパス
                pass
        
        # 10秒空ける（Twitter APIの制限値は15分で180回までなので少し余裕を持ちたい）
        sleep(10)

    except:
        # 異常が起きた場合はシステム終了
        print(traceback.format_exc())
        sys.exit()
