# test_batch_optimization.py

from typing import List, Any
from backtest.backtester import run_batch_optimization
from strategy.strategies.rsi_reversion import RSIReversionStrategy
from strategy.strategies.macd_cross import MACDCrossStrategy
from strategy.strategies.bollinger_band import BollingerBandStrategy

def main():
    symbols = ["BTCUSDT", "ETHUSDT"]
    timeframes = ["1h", "4h"]

    strategies = [
        RSIReversionStrategy,
        MACDCrossStrategy,
        BollingerBandStrategy
    ]

    results = run_batch_optimization(
        symbols=symbols,
        timeframes=timeframes,
        max_tests_per_strategy=10
    )

    print("\n✅ Best Strategy/Symbol/Timeframe Combos:")
    for res in results:
        print(f"({res['strategy']}, {res['symbol']}, {res['timeframe']}): Return = {res['return']*100:.2f}%, Sharpe = {res['sharpe_ratio']:.2f}, Avg. Daily PnL = {res['avg_daily_pnl']*100:.2f}%")

if __name__ == "__main__":
    main()
