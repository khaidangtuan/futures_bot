# backtest/backtester.py

'''
- Single-strategy backtests
- Hyperparameter optimization using composite metrics
- Parallel batch optimization across all strategies, symbols, and timeframes
- Scoring using Return, Sharpe Ratio, and Win Rate
- Outputs suitable for downstream execution or reporting
'''
import os
import itertools
import inspect
import importlib
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings import BACKTEST_LOOKBACK_DAYS
from strategy.base_strategy import BaseStrategy
from strategy.strategy_loader import load_strategy, list_available_strategies
from data.data_loader import get_historical_klines
from utils.logger import get_logger

logger = get_logger(__name__)


class Backtester:
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe
        self.data = get_historical_klines(symbol, interval=timeframe, limit=1500)

    def _filter_lookback(self, df: pd.DataFrame) -> pd.DataFrame:
        cutoff = datetime.utcnow() - timedelta(days=BACKTEST_LOOKBACK_DAYS)
        return df[df['timestamp'] >= cutoff].copy()

    def run_backtest(self, strategy_name: str, config: dict) -> Dict[str, Any]:
        strategy = load_strategy(strategy_name, self.symbol, self.timeframe, config)
        df = self._filter_lookback(self.data)
        df['signal'] = strategy.generate_signals(df)
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['signal'].shift() * df['returns']

        total_return = df['strategy_returns'].sum()
        avg_daily_pnl = df.groupby(df['timestamp'].dt.date)['strategy_returns'].sum().mean()
        sharpe_ratio = df['strategy_returns'].mean() / (df['strategy_returns'].std() + 1e-10) * (252 ** 0.5)
        win_rate = (df['strategy_returns'] > 0).sum() / (df['strategy_returns'] != 0).sum()
        trades = (df['signal'].diff().abs() > 0).sum()

        result = {
            "strategy": strategy.name(),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "config": config,
            "return": total_return,
            "avg_daily_pnl": avg_daily_pnl,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate,
            "trades": trades
        }

        result["score"] = self._compute_score(result)
        return result

    def optimize_strategy(self, strategy_class, param_grid: dict, max_tests: int = 50) -> Dict[str, Any]:
        best_result = None
        best_score = float('-inf')
        tested = 0

        keys, values = zip(*param_grid.items())
        combinations = list(itertools.product(*values))

        for combo in combinations:
            config = dict(zip(keys, combo))
            result = self.run_backtest(strategy_class.__name__, config)
            score = result["score"]
            if score > best_score:
                best_result = result
                best_score = score
            tested += 1
            if tested >= max_tests:
                break

        logger.info(f"✅ Best for {strategy_class.__name__} @ {self.symbol} [{self.timeframe}]: score={best_score:.4f}")
        return best_result

    @staticmethod
    def _compute_score(result): #, return_w=1.0, sharpe_w=1.5, winrate_w=0.5):
        return (result["avg_daily_pnl"]*result["sharpe_ratio"]*result["win_rate"])

def run_batch_optimization(
    symbols: List[str],
    timeframes: List[str],
    max_tests_per_strategy: int = 20
) -> List[Dict[str, Any]]:
    """
    Run sequential optimization over all strategy/symbol/timeframe combinations.
    Returns the best result for each (symbol, timeframe) pair.
    """
    strategy_names = list_available_strategies()   
    strategy_classes = [get_strategy_class_by_name(strategy_name) for strategy_name in strategy_names]
    all_results = []

    for symbol in symbols:
        for tf in timeframes:
            logger.info(f"\n🔍 Optimizing for {symbol} [{tf}]...")
            best_result = None

            tester = Backtester(symbol=symbol, timeframe=tf)

            for strategy_class in strategy_classes:
                logger.info(f" - Trying {strategy_class.__name__}")
                try:
                    result = tester.optimize_strategy(
                        strategy_class=strategy_class,
                        param_grid=strategy_class.hyperparameter_space(),
                        max_tests=max_tests_per_strategy
                    )
                    if not best_result or result["score"] > best_result["score"]:
                        best_result = result
                except Exception as e:
                    logger.error(f"❌ Error optimizing {strategy_class.__name__} @ {symbol} [{tf}]: {e}")

            if best_result:
                all_results.append(best_result)

    return all_results

def get_strategy_class_by_name(name: str):
    strategy_dir = os.path.join(os.path.dirname(__file__), "../strategy/strategies")
    for file in os.listdir(strategy_dir):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            module_path = f"strategy.strategies.{module_name}"
            try:
                mod = importlib.import_module(module_path)
                for _, cls in inspect.getmembers(mod, inspect.isclass):
                    if cls.__name__ == name and issubclass(cls, BaseStrategy):
                        return cls
            except Exception as e:
                logger.error(f"Error loading {name} from {module_path}: {e}")
    raise ValueError(f"Strategy class {name} not found.")

def run_batch_optimization_parallel(
    symbols: List[str],
    timeframes: List[str],
    max_tests_per_strategy: int = 20,
    max_workers: int = 4
) -> List[Dict[str, Any]]:
    strategy_names = list_available_strategies()
    tasks = []

    for symbol in symbols:
        for tf in timeframes:
            for strategy_name in strategy_names:
                tasks.append((strategy_name, symbol, tf))

    logger.info(f"🚀 Launching {len(tasks)} optimization jobs across {max_workers} threads...")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_optimize_worker, strategy_name, symbol, tf, max_tests_per_strategy)
            for strategy_name, symbol, tf in tasks
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return results


def _optimize_worker(strategy_name: str, symbol: str, timeframe: str, max_tests: int) -> Dict[str, Any]:
    try:
        logger.info(f"🔍 {strategy_name} | {symbol} [{timeframe}]")
        strategy_cls = get_strategy_class_by_name(strategy_name)
        bt = Backtester(symbol=symbol, timeframe=timeframe)
        return bt.optimize_strategy(strategy_cls, strategy_cls.hyperparameter_space(), max_tests)
    except Exception as e:
        logger.error(f"❌ Failed {strategy_name} @ {symbol} [{timeframe}]: {e}")
        return None
