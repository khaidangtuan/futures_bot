# strategy/strategies/macd_trend.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class MACDTrendStrategy(BaseStrategy):
    """
    Trend-following MACD strategy.
    Buy when MACD > 0 and rising.
    Sell when MACD < 0 and falling.
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
        return "MACDTrend"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        fast = self.hyperparameters["fast_period"]
        slow = self.hyperparameters["slow_period"]
        signal_period = self.hyperparameters["signal_period"]

        # === MACD Calculation ===
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
        df['macd_slope'] = df['macd'].diff()

        # === Signal Logic ===
        df['signal'] = 0
        df.loc[(df['macd'] > 0) & (df['macd_slope'] > 0), 'signal'] = 1   # Long trend
        df.loc[(df['macd'] < 0) & (df['macd_slope'] < 0), 'signal'] = -1  # Short trend

        return df['signal']
