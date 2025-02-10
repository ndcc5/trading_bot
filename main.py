# File: main.py
import logging
import asyncio
from data_collector import PriceCollector
from arbitrage import ArbitrageEngine
from trader import Trader
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

async def main():
    # 初始化套利引擎
    arbitrage_engine = ArbitrageEngine(None)  # 先创建套利引擎实例

    # 初始化交易模块
    trader = Trader()

    # 初始化价格收集器并传递套利引擎和交易模块
    price_collector = PriceCollector(arbitrage_engine, trader)  # 把套利引擎和交易模块传入

    # 注入交易模块到套利引擎
    arbitrage_engine.execute_arbitrage = lambda s, e: trader.execute_pair(s, e)

    # 启动价格收集
    await price_collector.run()

    # 启动套利引擎
    await arbitrage_engine.run()

if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())
