import websocket
import config
import os
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

print(client.get_asset_balance(asset='EUR'))
