# strategy/strategy_loader.py

'''
- Dynamically loads any strategy class from strategy/strategies/
- Returns an instance of the strategy, ready to use
- Supports loading by string name, with symbol, timeframe, and config
- Avoids hardcoding each strategy — plug & play
'''

import os
import importlib
import inspect
from strategy.base_strategy import BaseStrategy

STRATEGY_PACKAGE = "strategy.strategies"

def list_available_strategies():
    """
    Lists all strategy class names available in strategy/strategies/.
    """
    strategy_dir = os.path.join(os.path.dirname(__file__), "strategies")
    files = [f for f in os.listdir(strategy_dir) if f.endswith(".py") and not f.startswith("__")]

    strategy_classes = []

    for file in files:
        module_name = file[:-3]
        module_path = f"{STRATEGY_PACKAGE}.{module_name}"
        try:
            module = importlib.import_module(module_path)
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, BaseStrategy) and cls != BaseStrategy:
                    strategy_classes.append(cls.__name__)
        except Exception as e:
            print(f"Failed to load {module_path}: {e}")

    return strategy_classes


def load_strategy(strategy_class_name: str, symbol: str, timeframe: str, config: dict = None) -> BaseStrategy:
    """
    Loads a strategy class by name and returns an instance.

    :param strategy_class_name: Name of the strategy class (must match class name)
    :param symbol: Trading symbol (e.g., BTCUSDT)
    :param timeframe: Timeframe string (e.g., 1h)
    :param config: Optional hyperparameter config
    :return: Instance of the strategy class
    """
    strategy_dir = os.path.join(os.path.dirname(__file__), "strategies")
    files = [f for f in os.listdir(strategy_dir) if f.endswith(".py") and not f.startswith("__")]

    for file in files:
        module_name = file[:-3]
        module_path = f"{STRATEGY_PACKAGE}.{module_name}"

        try:
            module = importlib.import_module(module_path)
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__name__ == strategy_class_name and issubclass(cls, BaseStrategy):
                    return cls(symbol=symbol, timeframe=timeframe, config=config or {})
        except Exception as e:
            print(f"Error loading strategy {strategy_class_name} from {module_path}: {e}")

    raise ValueError(f"Strategy class '{strategy_class_name}' not found.")
