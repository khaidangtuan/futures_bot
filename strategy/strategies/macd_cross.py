# strategy/strategies/macd_cross.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class MACDCrossStrategy(BaseStrategy):
    """
    MACD cross strategy:
    Buy when MACD crosses above Signal line,
    Sell when MACD crosses below Signal line.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "fast_period": [8, 12, 15],
            "slow_period": [21, 26, 30],
            "signal_period": [6, 9, 12]
        }

    def name(self) -> str:
        return "MACDCross"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        fast = self.hyperparameters["fast_period"]
        slow = self.hyperparameters["slow_period"]
        signal_period = self.hyperparameters["signal_period"]

        # MACD components
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['signal_line'] = df['macd'].ewm(span=signal_period, adjust=False).mean()

        # Signal logic
        df['signal'] = 0
        df.loc[df['macd'] > df['signal_line'], 'signal'] = 1
        df.loc[df['macd'] < df['signal_line'], 'signal'] = -1

        return df['signal']
