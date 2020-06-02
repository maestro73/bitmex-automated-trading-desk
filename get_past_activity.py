"""
This script aims to connect with Bitmex and to get the last 1000 candles and insert them with additional data in a database.
"""
import bitmex, datetime, os, pytz, sys, time, warnings
import anchored_vwaps as anch_vwaps

import db_management as dbm
import td_sequential as td
warnings.filterwarnings("ignore")

BITMEX_API_KEY ='YOUR API KEY'
BITMEX_API_SECRET = 'YOUR API SECRET'

BITMEX_AVAILABLE_TIMEFRAMES = ["5m", "1h", "1d"]
ANCH_VWAP_LOOKBACK_VALUES = [50, 100, 150, 200, 600]


def connect_bitmex():
    return bitmex.bitmex(test = False, api_key = BITMEX_API_KEY, api_secret = BITMEX_API_SECRET)

def get_user(bitmex_client):
    return bitmex_client.User.User_getMargin().result()

def get_wallet_balance(user_object):
    #Converting sats to $BTC
    return user_object[0]["walletBalance"] / 100000000

def get_ticker_info(bitmex_client, ticker_name, timeframe_id):
    return bitmex_client.Trade.Trade_getBucketed(symbol = ticker_name, binSize = timeframe_id, partial=True, count=700, reverse=True).result()




if __name__ == "__main__":


    for timeframe_id in BITMEX_AVAILABLE_TIMEFRAMES:
        bitmex_client = connect_bitmex()
        candle_array = get_ticker_info(bitmex_client, "XBTUSD", timeframe_id)[0]

        #We work with the previous candle in order to have the full and accurate data of a candle
        dbm.insert_candle(timeframe_id, candle_array[1])
        vwap_values = anch_vwaps.get_anch_vwap_value(timeframe_id, candle_array[1:], ANCH_VWAP_LOOKBACK_VALUES)
        try:
            td.get_td_sequential(timeframe_id, candle_array[1:])
        except Exception as exception_e:
            print("Unable to compute td_sequential for %s timeframe " % timeframe_id)
            print(exception_e)



