# test_parallel_batch.py

import os
import pandas as pd
from backtest.backtester import run_batch_optimization_parallel

def main():
    os.makedirs("outputs", exist_ok=True)

    symbols = ["BTCUSDT", "ETHUSDT"]
    timeframes = ["1h", "4h"]

    results = run_batch_optimization_parallel(
        symbols=symbols,
        timeframes=timeframes,
        max_tests_per_strategy=10,
        max_workers=4
    )

    df = pd.DataFrame(results)
    df.to_csv("outputs/all_optimized_results.csv", index=False)

    best_per_strategy = df.sort_values("score", ascending=False).groupby("strategy").first()
    best_per_strategy.to_csv("outputs/best_per_strategy.csv")

    best_overall = df.loc[df['score'].idxmax()]
    best_overall.to_frame().T.to_csv("outputs/best_overall_strategy.csv", index=False)

    print("\n🏆 Best Overall Strategy:")
    print(best_overall[['strategy', 'symbol', 'timeframe', 'score']])

if __name__ == "__main__":
    main()
