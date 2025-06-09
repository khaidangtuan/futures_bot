# strategy/strategies/supertrend.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class SuperTrendStrategy(BaseStrategy):
    """
    SuperTrend-based strategy.
    Buy when price crosses above SuperTrend line;
    Sell when price crosses below SuperTrend line.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "atr_period": 10,
            "multiplier": 3.0
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "atr_period": [7, 10, 14],
            "multiplier": [2.0, 3.0, 4.0]
        }

    def name(self) -> str:
        return "SuperTrend"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        period = self.hyperparameters["atr_period"]
        multiplier = self.hyperparameters["multiplier"]

        # === ATR Calculation ===
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['close'].shift()).abs()
        df['tr3'] = (df['low'] - df['close'].shift()).abs()
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=period).mean()

        # === SuperTrend Calculation ===
        hl2 = (df['high'] + df['low']) / 2
        df['upper_band'] = hl2 + (multiplier * df['atr'])
        df['lower_band'] = hl2 - (multiplier * df['atr'])

        df['supertrend'] = 0.0
        in_uptrend = True

        for i in range(1, len(df)):
            if df['close'][i] > df['upper_band'][i - 1]:
                in_uptrend = True
            elif df['close'][i] < df['lower_band'][i - 1]:
                in_uptrend = False

            if in_uptrend:
                df.at[i, 'supertrend'] = df['lower_band'][i]
            else:
                df.at[i, 'supertrend'] = df['upper_band'][i]

        # === Signal Generation ===
        df['signal'] = 0
        df.loc[df['close'] > df['supertrend'], 'signal'] = 1   # Buy
        df.loc[df['close'] < df['supertrend'], 'signal'] = -1  # Sell

        return df['signal']
