# test_backtest.py

from backtest.backtester import Backtester
from strategy.strategies.rsi_reversion import RSIReversionStrategy

def main():
    symbol = "BTCUSDT"
    timeframe = "1h"

    print(f"Running backtest on {symbol} [{timeframe}]...\n")

    bt = Backtester(symbol=symbol, timeframe=timeframe)

    # === Single backtest run ===
    config = {
        "rsi_period": 14,
        "overbought": 70,
        "oversold": 30
    }

    result = bt.run_backtest("RSIReversionStrategy", config)
    print("Backtest Result:")
    for key, val in result.items():
        print(f"  {key}: {val}")

    # === Grid optimization ===
    print("\nOptimizing strategy...")
    best = bt.optimize_strategy(
        strategy_class=RSIReversionStrategy,
        param_grid=RSIReversionStrategy.hyperparameter_space(),
        max_tests=20
    )

    print("\nBest Optimization Result:")
    for key, val in best.items():
        print(f"  {key}: {val}")

if __name__ == "__main__":
    main()
