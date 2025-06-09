# main.py

import time
from datetime import datetime
from market_screening.screener import screen_top_symbols
from backtest.backtester import run_batch_optimization
from execution.executor import Executor
from strategy.strategy_loader import load_strategy
from data.data_loader import get_historical_klines
from risk.risk_manager import RiskManager
from utils.logger import get_logger
from config.settings import (
    TRADE_TIMEFRAME,
    DEFAULT_LEVERAGE,
    TRAILING_STOP_LOSS_PCT,
    STOP_LOSS_PCT,
    MAX_TESTS_PER_STRATEGY
)
import warnings
warnings.filterwarnings('ignore')

logger = get_logger(__name__)

'''
# === 1. Market Screening ===
logger.info("🔍 Screening market...")
symbols = screen_top_symbols()

# === 2. Backtest & Optimize ===
logger.info("🧠 Optimizing strategies...")
results = run_batch_optimization(
    symbols=symbols,
    timeframes=TRADE_TIMEFRAME,
    max_tests_per_strategy=MAX_TESTS_PER_STRATEGY
)

# === 3. Select Best Strategy Combo ===
best = max(results, key=lambda r: r["score"])
logger.info(f"🏆 Selected: {best['strategy']} on {best['symbol']} [{best['timeframe']}]")

symbol = best['symbol']
timeframe = best['timeframe']
strategy_name = best['strategy']
config = best['config'] if isinstance(best['config'], dict) else eval(best['config'])

print(symbol)
print(timeframe)
print(strategy_name)
print(config)

'''

symbol = 'WCTUSDT'
timeframe = '3m'
strategy_name = 'SuperTrend'
config = {'atr_period': 7,
          'multiplier': 4.0}
# === 4. Initialize Core Components ===
executor = Executor(symbol=symbol, leverage=DEFAULT_LEVERAGE)
risk_mgr = RiskManager(symbol=symbol, leverage=DEFAULT_LEVERAGE)
strategy = load_strategy(strategy_name+'Strategy', symbol, timeframe, config)

df = get_historical_klines(symbol, interval=timeframe, limit=100)
df['signal'] = strategy.generate_signals(df)
signal = int(df['signal'].iloc[-1])
print(signal)

# === 5.2 Position Management ===
position = executor.get_open_position()
print(position['unRealizedProfit']/)

#entry_price = df['close'].iloc[-1]
#usdt_amt = risk_mgr.calculate_position_size(entry_price)

#print(entry_price)
#print(usdt_amt)

#usdt_amt = 10
#executor.place_order(usdt_amount=usdt_amt, signal=signal)

