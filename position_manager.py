from binance.client import Client as BinanceClient
from okx import MarketData as OKXClient
from config import Config

class PositionManager:
    def __init__(self):
        self.binance_client = BinanceClient(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)
        self.okx_client = OKXClient(Config.OKX_API_KEY, Config.OKX_API_SECRET)

    def get_balance(self, exchange):
        if exchange == "binance":
            balance = self.binance_client.get_asset_balance(asset="BTC")
            return float(balance["free"])
        elif exchange == "okx":
            balance = self.okx_client.get_account_balance(currency="BTC")
            return float(balance["data"][0]["details"][0]["availBal"])

    def sync_balance(self):
        binance_balance = self.get_balance("binance")
        okx_balance = self.get_balance("okx")
        if binance_balance > okx_balance:
            transfer_amount = binance_balance - okx_balance
            self.transfer("binance", "okx", transfer_amount)
        else:
            transfer_amount = okx_balance - binance_balance
            self.transfer("okx", "binance", transfer_amount)

    def transfer(self, from_exchange, to_exchange, amount):
        if from_exchange == "binance":
            self.binance_client.transfer_spot_to_margin(asset="BTC", amount=amount)
        elif from_exchange == "okx":
            self.okx_client.transfer_spot_to_margin(currency="BTC", amount=amount)