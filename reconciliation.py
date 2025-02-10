from trader import Trader
from position_manager import PositionManager
from notification import Notification

class Reconciliation:
    def __init__(self):
        self.trader = Trader()
        self.position_manager = PositionManager()
        self.notification = Notification()

    def verify_trade(self, action):
        # 验证交易是否成功
        if action == "sell_binance_buy_okx":
            binance_balance = self.position_manager.get_balance("binance")
            okx_balance = self.position_manager.get_balance("okx")
            if binance_balance < 0 or okx_balance < 0:
                self.notification.send_telegram("Trade verification failed! Please check manually.")
                self.hedge_position()

    def hedge_position(self):
        # 自动对冲仓位
        self.trader.execute_trade("buy_binance_sell_okx")