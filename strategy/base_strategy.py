# strategy/base_strategy.py

from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """

    def __init__(self, symbol: str, timeframe: str, config: dict = None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = config or {}
        self.hyperparameters = self._resolve_hyperparameters()

    @abstractmethod
    def name(self) -> str:
        """
        Unique name of the strategy.
        """
        pass

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals: 1 = Buy, -1 = Sell, 0 = Hold.
        """
        pass

    @classmethod
    def default_hyperparameters(cls) -> dict:
        """
        Override in child to return default hyperparameter values.
        """
        return {}

    @classmethod
    def hyperparameter_space(cls) -> dict:
        """
        Override in child to return search space for optimization.
        """
        return {}

    def _resolve_hyperparameters(self) -> dict:
        """
        Merges user config with strategy defaults.
        """
        defaults = self.default_hyperparameters()
        return {key: self.config.get(key, defaults.get(key)) for key in defaults}

    def get_hyperparameters(self) -> dict:
        return self.hyperparameters

    def set_hyperparameters(self, params: dict):
        self.hyperparameters.update(params)

    def describe(self) -> dict:
        return {
            "strategy": self.name(),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "hyperparameters": self.hyperparameters
        }

    def __repr__(self):
        return f"<{self.name()} Strategy | {self.symbol} [{self.timeframe}]>"
