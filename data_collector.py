# File: data_collector.py
import asyncio
import json
import websockets
import logging
from config import Config
import time

logger = logging.getLogger(__name__)

class PriceCollector:
    def __init__(self, arbitrage_engine, trader):
        self.arbitrage_engine = arbitrage_engine  # 保存传入的 arbitrage_engine 实例
        self.trader = trader  # 保存传入的 trader 实例
        self.prices = {
            'binance': None,
            'okx': None
        }
        self.lock = asyncio.Lock()
        self.last_okx_time = time.time()

    async def binance_ws(self):
        try:
            async with websockets.connect(Config.BINANCE_WS_URL) as ws:
                logger.info("Connected to Binance WebSocket...")
                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        "btcusdt@ticker"
                    ],
                    "id": 1
                }
                await ws.send(json.dumps(subscribe_message))
                while True:
                    try:
                        msg = await ws.recv()
                        msg = json.loads(msg)
                        if 's' in msg and msg['s'] == 'BTCUSDT' and 'c' in msg:
                            price = float(msg['c'])
                            async with self.lock:
                                self.prices['binance'] = price
                            logger.info(f"Binance BTC Price: {price}")
                            self.check_arbitrage_opportunity()  # 检查是否有套利机会
                    except Exception as e:
                        logger.error(f"Error in Binance WebSocket: {e}")
        except Exception as e:
            logger.error(f"Error in connecting to Binance WebSocket: {e}")

    async def okx_ws(self):
        try:
            async with websockets.connect(Config.OKX_WS_URL) as ws:
                logger.info("Connected to OKX WebSocket...")
                subscribe_message = {
                    "op": "subscribe",
                    "args": [
                        {
                            "channel": "tickers",
                            "instId": "BTC-USDT"
                        }
                    ]
                }
                await ws.send(json.dumps(subscribe_message))
                while True:
                    try:
                        msg = await ws.recv()
                        msg = json.loads(msg)
                        if 'data' in msg and isinstance(msg['data'], list):
                            for data in msg['data']:
                                if 'last' in data:
                                    price = float(data['last'])
                                    async with self.lock:
                                        self.prices['okx'] = price
                                    
                                    current_time = time.time()
                                    if current_time - self.last_okx_time >= 5:
                                        self.last_okx_time = current_time
                                        logger.info(f"OKX BTC Price: {price}")
                                        self.check_arbitrage_opportunity()  # 检查是否有套利机会

                    except Exception as e:
                        logger.error(f"Error in OKX WebSocket: {e}")
        except Exception as e:
            logger.error(f"Error in connecting to OKX WebSocket: {e}")

    def check_arbitrage_opportunity(self):
        binance_price = self.prices.get('binance')
        okx_price = self.prices.get('okx')
        
        if binance_price is not None and okx_price is not None:
            spread = abs(binance_price - okx_price)
            logger.info(f"当前价格差值为 {spread:.2f}")

            if spread > Config.SPREAD_THRESHOLD:
                logger.info(f"当前价格差值为 {spread:.2f} > {Config.SPREAD_THRESHOLD}，适合套利")
                
                # 调用 Trader 的 execute_pair 方法执行套利交易
                self.execute_arbitrage_trade(binance_price, okx_price)
            else:
                logger.info(f"当前价格差值为 {spread:.2f} < {Config.SPREAD_THRESHOLD}，不适合套利")

    def execute_arbitrage_trade(self, binance_price, okx_price):
        # 调用 Trader 类的 execute_pair 方法来执行交易
        # sell_ex 和 buy_ex 可以根据价格决定，假设是卖出 binance，买入 okx
        sell_ex = 'binance'
        buy_ex = 'okx'
        
        # 调用 execute_pair 来执行套利交易
        trade_successful = self.trader.execute_pair(sell_ex, buy_ex)
        
        if trade_successful:
            logger.info("Arbitrage trade executed successfully.")
        else:
            logger.error("Arbitrage trade failed.")
    
    async def run(self):
        logger.info("PriceCollector is running...")
        await asyncio.gather(
            self.binance_ws(),
            self.okx_ws()
        )
