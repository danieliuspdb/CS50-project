import websocket
import config
import os
from binance.client import Client



#SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

client = Client(config.API_KEY, config.API_SECRET)

print(client.get_asset_balance(asset='EUR'))

#def on_open(ws):
    #print('opened connection')

#def on_close(ws):
    #print('closed connection')

#def on_message(ws, message):
    #print('received message')

#ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
#ws.run_forever()
