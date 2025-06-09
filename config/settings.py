# config/settings.py

# exchange settings
BINANCE_API_KEY = "FERXZLa8ne7klEGMKWSHcuk0S142wNElyDAa9SVT4HiMsMUUKvE7fFmB2lg96Z5d"
BINANCE_API_SECRET = "Gbt9clNcyTltaUwkbQL6GDC3DWth15Wky0XzVccHbhCE2Z84rcrflB4nrqz7JDaP"
BASE_URL = "https://fapi.binance.com"

# screener settings
TOP_N_SYMBOLS = 20 #10
MIN_VOLUME_USDT = 100_000_000  # Filter symbols with at least $100M volume
VOLATILITY_TIMEFRAME = '3m'         # e.g., '1m', '15m', '1h', '4h', etc.
VOLATILITY_LOOKBACK_DAYS = 2        # Lookback window for volatility calculation

# backtest settings
BACKTEST_LOOKBACK_DAYS = 1
MAX_TESTS_PER_STRATEGY = 20

# trading settings
TRADE_TIMEFRAME = ['1m', '3m'] #, '15m', '30m'] #, '1h']
DEFAULT_LEVERAGE = 10              # x leverage
RISK_PER_TRADE = 0.5              # 1% of account equity (ready to lose)
STOP_LOSS_PCT = 0.10               # SL % below entry for risk model
TRAILING_STOP_LOSS_PCT = 0.1
PROFIT_EXPECT = 0.05

