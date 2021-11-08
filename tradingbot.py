#Trading bot that gets information from binance and depending on the RSI can
#buy and sell a pair of arbitrarily selected crypto

import websocket, json, numpy, talib, pprint, config
from binance.enums import *
from binance.client import Client

RSI_PERIOD = 14
OVERSOLD_THRESHOLD = 35
OVERBOUGHT_THRESHOLD = 70
TRADE_QUANTITY = 360
#YOU CAN CHOOSE ANY TRADING PAIR FROM THE BINANCE TRADING LIST
TRADE_SYMBOL = 'ETHUSDT'
SOCKET = "wss://stream.binance.com:9443/ws/adausdt@kline_1m"

bought_price = 0
closes = []
in_position = False
client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity,symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print('sending order')
        order = client.create_order(symbol=symbol,side=side,type=ORDER_TYPE_MARKET,quantity = quantity)
        print(order)
        return True
    except Exception as e:
        return False

def on_error(ws,error):
    print(error)

def on_open(ws):
    print("socket is open")

def on_close(ws):
    print("socket is closed")
    ws = websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message,on_error=on_error)
    ws.run_forever()



def on_message(ws,message):
    global closes
    global bought_price
    global in_position
    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    #in this part we want to find a good spot to buy
    if is_candle_closed:
        print('candle closed at:{}'.format(close))
        closes.append(float(close))
        print(len(closes))
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes,RSI_PERIOD)
            last_rsi = rsi[-1]
            print('the RSI is:')
            print(last_rsi)
            if last_rsi > OVERBOUGHT_THRESHOLD:
                if in_position:
                    #SELL YOUR CRYPTO
                    print('i would sell if i follow rsi strategy only')
                    #order_succided = order(SIDE_SELL,TRADE_QUANTITY,TRADE_SIMBOL)
                    #if orders_succeded:
                    #    in_position = False
                else:
                    pass

            elif last_rsi < OVERSOLD_THRESHOLD:
                if in_position:
                    print('you already own a piece of ethereum')
                else:
                    print('Time to buy that piece of ethereum')
                    order_succeded = order(SIDE_BUY,TRADE_QUANTITY,TRADE_SYMBOL)
                    bought_price = close
                    if order_succeded:
                        print('we just bought some crypto')
                        in_position = True
            else:
                print('the prices are not favorable for either sell or buy')
    #in this part we want to win a certain percentaje of the ehtereum
    if in_position:
        print('we now have 0.05 ethereum ready to be sold')
        if float(close) > float(bought_price)*1.012:
            order_succeded = order(SIDE_SELL,TRADE_QUANTITY,TRADE_SYMBOL)
            if order_succeded:
                print('we just win some cash!!!')
                in_position = False




ws = websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message,on_error=on_error)


ws.run_forever()
