import ccxt
import logging
import time
from config import Config
from notification import Notifier  # 新增通知模块

logger = logging.getLogger(__name__)

class Trader:
    def __init__(self):
        # 修改为模拟盘的 API 地址
        okx_url = 'https://www.okx.com/api/v5/account/balance' if Config.OKX_SANDBOX else 'https://www.okx.com/api/v5/account/balance'
        binance_url = 'https://testnet.binance.vision/api' if Config.BINANCE_SANDBOX else 'https://api.binance.com'

        self.exchanges = {
            'binance': ccxt.binance({
                'apiKey': Config.BINANCE_API_KEY,
                'secret': Config.BINANCE_API_SECRET,
                'enableRateLimit': True,
                'urls': {
                    'api': binance_url  # 根据是否为模拟盘设置正确的 URL
                }
            }),
            'okx': ccxt.okx({
                'apiKey': Config.OKX_API_KEY,
                'secret': Config.OKX_API_SECRET,
                'password': Config.OKX_PASSPHRASE,
                'enableRateLimit': True,
                'urls': {
                    'api': okx_url  # 根据是否为模拟盘设置正确的 URL
                },
                'headers': {
                    'x-simulated-trading': '1' if Config.OKX_SANDBOX else None  # 模拟盘需要加入此头部信息
                }
            })
        }
        self.notifier = Notifier()  # 初始化通知系统

    def check_balance(self, exchange, currency):
        """检查账户余额"""
        try:
            if exchange == 'binance':
                return Config.QUANTITY  # 模拟余额

            balance = self.exchanges[exchange].fetch_balance()
            logger.info(f"Balance response from {exchange}: {balance}")  # 打印返回的完整数据结构

            if isinstance(balance, dict):  # 确保返回的是字典类型
                if exchange == 'okx' and 'data' in balance:
                    logger.info(f"OKX balance data structure: {balance['data']}")  # 打印OKX返回的具体数据
                    for item in balance['data']:
                        if isinstance(item, dict) and item.get('currency') == currency:
                            return float(item['available'])  # 返回余额
                else:
                    return balance['total'].get(currency, 0)
            else:
                logger.error(f"Unexpected response from {exchange}: {balance}")
                return 0
        except ccxt.NetworkError as e:
            logger.error(f"Network error while checking balance on {exchange}: {str(e)}")
            return 0
        except ccxt.BaseError as e:
            logger.error(f"API error while checking balance on {exchange}: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Failed to check balance on {exchange}: {str(e)}")
            return 0

    def execute_pair(self, sell_ex, buy_ex):
        try:
            # 1. 资金余额检查
            btc_balance_sell = self.check_balance(sell_ex, 'BTC')
            usdt_balance_buy = self.check_balance(buy_ex, 'USDT')

            if btc_balance_sell < Config.QUANTITY:
                msg = f"Insufficient BTC balance on {sell_ex}. Required: {Config.QUANTITY}, Available: {btc_balance_sell}"
                logger.error(msg)
                self.notifier.send_alert(msg)
                return False

            ticker = self.exchanges[buy_ex].fetch_ticker(Config.SYMBOL)
            estimated_cost = ticker['ask'] * Config.QUANTITY

            if usdt_balance_buy < estimated_cost:
                msg = f"Insufficient USDT balance on {buy_ex}. Required: {estimated_cost:.2f}, Available: {usdt_balance_buy:.2f}"
                logger.error(msg)
                self.notifier.send_alert(msg)
                return False

            # 2. 执行卖出订单
            sell_order = self.exchanges[sell_ex].create_market_sell_order(
                Config.SYMBOL,
                Config.QUANTITY
            )
            logger.info(f"Placed sell order on {sell_ex}: {sell_order}")

            if not self.verify_order(sell_ex, sell_order['id']):
                msg = f"Failed to verify sell order on {sell_ex}"
                logger.error(msg)
                self.notifier.send_alert(msg)
                return False

            # 3. 执行买入订单
            buy_order = self.exchanges[buy_ex].create_market_buy_order(
                Config.SYMBOL,
                Config.QUANTITY
            )
            logger.info(f"Placed buy order on {buy_ex}: {buy_order}")

            if not self.verify_order(buy_ex, buy_order['id']):
                msg = f"Failed to verify buy order on {buy_ex}"
                logger.error(msg)
                self.notifier.send_alert(msg)
                return False

            self.verify_trade_result(sell_order, buy_order)

            return True

        except Exception as e:
            logger.error(f"Trade failed: {str(e)}")
            self.notifier.send_alert(f"Trade failed: {str(e)}")
            return False

    def verify_order(self, exchange, order_id):
        """验证订单状态"""
        max_retries = 3
        retry_delay = 1  # seconds

        for _ in range(max_retries):
            try:
                order = self.exchanges[exchange].fetch_order(order_id)
                if order['status'] == 'closed':
                    return True
                time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Failed to verify order {order_id} on {exchange}: {str(e)}")
                time.sleep(retry_delay)

        return False

    def verify_trade_result(self, sell_order, buy_order):
        """核对交易结果并计算滑点"""
        try:
            sell_price = float(sell_order['price'])
            buy_price = float(buy_order['price'])

            spread = sell_price - buy_price
            expected_spread = Config.SPREAD_THRESHOLD
            slippage = spread - expected_spread

            trade_result = {
                'sell_exchange': sell_order['info']['symbol'],
                'sell_price': sell_price,
                'buy_exchange': buy_order['info']['symbol'],
                'buy_price': buy_price,
                'quantity': Config.QUANTITY,
                'slippage': slippage,
                'profit': spread * Config.QUANTITY
            }

            logger.info(f"Trade completed successfully: {trade_result}")
            self.notifier.send_trade_report(trade_result)

            if slippage > Config.MAX_SLIPPAGE:
                msg = f"Large slippage detected: {slippage:.2f}"
                logger.warning(msg)
                self.notifier.send_alert(msg)

        except Exception as e:
            logger.error(f"Failed to verify trade result: {str(e)}")
            self.notifier.send_alert(f"Failed to verify trade result: {str(e)}")
