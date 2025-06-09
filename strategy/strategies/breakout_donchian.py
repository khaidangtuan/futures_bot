# strategy/strategies/breakout_donchian.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class BreakoutDonchianStrategy(BaseStrategy):
    """
    Donchian Channel breakout strategy.
    Buy when price breaks above previous N-period high,
    Sell when price breaks below previous N-period low.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "window": 20
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "window": [10, 20, 50]
        }

    def name(self) -> str:
        return "BreakoutDonchian"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        window = self.hyperparameters["window"]

        df['upper'] = df['high'].rolling(window=window).max()
        df['lower'] = df['low'].rolling(window=window).min()

        df['signal'] = 0
        df.loc[df['close'] > df['upper'], 'signal'] = 1    # Breakout Buy
        df.loc[df['close'] < df['lower'], 'signal'] = -1   # Breakdown Sell

        return df['signal']
