# strategy/strategies/atr_channel.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class ATRChannelStrategy(BaseStrategy):
    """
    ATR channel breakout strategy.
    Buy when price > upper band (based on ATR),
    Sell when price < lower band (based on ATR).
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "atr_period": 14,
            "multiplier": 2
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "atr_period": [10, 14, 20],
            "multiplier": [1.5, 2, 2.5]
        }

    def name(self) -> str:
        return "ATRChannel"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        period = self.hyperparameters["atr_period"]
        mult = self.hyperparameters["multiplier"]

        # === ATR Calculation ===
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['close'].shift()).abs()
        df['tr3'] = (df['low'] - df['close'].shift()).abs()
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

        df['atr'] = df['tr'].rolling(window=period).mean()

        # === Channel Calculation ===
        df['upper_band'] = df['close'].rolling(window=period).mean() + (mult * df['atr'])
        df['lower_band'] = df['close'].rolling(window=period).mean() - (mult * df['atr'])

        # === Signal Generation ===
        df['signal'] = 0
        df.loc[df['close'] > df['upper_band'], 'signal'] = 1   # Buy
        df.loc[df['close'] < df['lower_band'], 'signal'] = -1  # Sell

        return df['signal']
