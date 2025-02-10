import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Exchange API配置
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    OKX_API_KEY = os.getenv('OKX_API_KEY')
    OKX_API_SECRET = os.getenv('OKX_API_SECRET')
    OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE')
    BINANCE_SANDBOX = True  # 设置为 True 使用 Binance 模拟盘，False 使用正式盘
    OKX_SANDBOX = True  # 设置为 True 使用 OKX 测试网，False 使用正式网
    # 交易参数
    SYMBOL = 'BTC/USDT'
    QUANTITY = 0.001  # 每次交易数量
    SPREAD_THRESHOLD = 10.0  # 触发套利的价差阈值
    MAX_SLIPPAGE = 10.0  # 最大允许滑点

    # WebSocket配置
    #  BINANCE_WS_URL = 'wss://testnet.binance.vision/ws/btcusdt@ticker'  # 使用测试网的WebSocket URL
    BINANCE_WS_URL = 'wss://testnet.binance.vision/ws'  # 使用测试网的WebSocket URL
    OKX_WS_URL = 'wss://ws.okx.com:8443/ws/v5/public'  # OKX的WebSocket URL（模拟账户）

    # 日志配置
    LOG_FILE = 'arbitrage.log'

    # 邮件通知配置
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL = os.getenv('EMAIL')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    ALERT_RECIPIENTS = os.getenv('ALERT_RECIPIENTS', '').split(',')
    # Telegram通知配置
    TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')