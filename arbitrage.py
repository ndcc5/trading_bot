# File: arbitrage.py
import logging
from config import Config

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    def __init__(self, price_collector):
        self.price_collector = price_collector

    def check_arbitrage(self):
        with self.price_collector.lock:
            price_binance = self.price_collector.prices['binance']
            price_okx = self.price_collector.prices['okx']

        # 确保价格数据存在
        if not all([price_binance, price_okx]):
            logger.warning("Missing prices for Binance or OKX.")
            return None

        # 计算价格差
        spread = abs(price_binance - price_okx)
        logger.info(f"Checking arbitrage... Binance: {price_binance}, OKX: {price_okx}, Spread: {spread:.2f}")

        # 如果价格差超过阈值，认为适合套利
        if spread >= Config.SPREAD_THRESHOLD:
            logger.info(f"Arbitrage opportunity detected! Spread: {spread:.2f} - Suitable for arbitrage!")
            if price_binance > price_okx:
                return ('binance', 'okx', price_binance, price_okx)
            else:
                return ('okx', 'binance', price_okx, price_binance)
        else:
            logger.info(f"Current spread: {spread:.2f} - Not suitable for arbitrage.")
        return None

    def run(self):
        while True:
            opportunity = self.check_arbitrage()
            if opportunity:
                sell_ex, buy_ex, sell_price, buy_price = opportunity
                logger.info(f"Arbitrage opportunity detected! Sell {sell_ex} at {sell_price:.2f}, Buy {buy_ex} at {buy_price:.2f}")
                # 触发交易逻辑
                self.execute_arbitrage(sell_ex, buy_ex)
            time.sleep(1)  # 防止频繁交易
            time.sleep(0.1)

    def execute_arbitrage(self, sell_exchange, buy_exchange):
        # 实际的交易逻辑
        logger.info(f"Executing arbitrage between {sell_exchange} and {buy_exchange}")
