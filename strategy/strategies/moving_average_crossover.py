# strategy/strategies/moving_average_crossover.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Buy when short MA crosses above long MA.
    Sell when short MA crosses below long MA.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "short_window": 10,
            "long_window": 50
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "short_window": [5, 10, 20],
            "long_window": [30, 50, 100]
        }

    def name(self) -> str:
        return "MovingAverageCrossover"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()

        short_window = self.hyperparameters["short_window"]
        long_window = self.hyperparameters["long_window"]

        df['short_ma'] = df['close'].rolling(window=short_window).mean()
        df['long_ma'] = df['close'].rolling(window=long_window).mean()

        df['signal'] = 0
        df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1   # Buy
        df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1  # Sell

        return df['signal']
