import time
from config import Config

class RiskControl:
    def __init__(self):
        self.last_trade_time = 0
        self.max_loss = -100  # 最大允许亏损金额（以 USDT 计）

    def can_trade(self):
        current_time = time.time()
        if current_time - self.last_trade_time >= 60:  # 60秒内只能交易一次
            self.last_trade_time = current_time
            return True
        return False

    def check_loss(self, pnl):
        if pnl <= self.max_loss:
            return False
        return True