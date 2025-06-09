# strategy/strategies/trend_adx.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class TrendADXStrategy(BaseStrategy):
    """
    Trend-following strategy using ADX.
    Buy when +DI > -DI and ADX > threshold.
    Sell when -DI > +DI and ADX > threshold.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "adx_period": 14,
            "adx_threshold": 20
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "adx_period": [10, 14, 20],
            "adx_threshold": [20, 25, 30]
        }

    def name(self) -> str:
        return "TrendADX"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        period = self.hyperparameters["adx_period"]
        threshold = self.hyperparameters["adx_threshold"]

        # True Range calculations
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['close'].shift()).abs()
        df['tr3'] = (df['low'] - df['close'].shift()).abs()
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

        # Directional Movements
        df['plus_dm'] = df['high'].diff()
        df['minus_dm'] = df['low'].diff().abs()

        df['plus_dm'] = df['plus_dm'].where((df['plus_dm'] > df['minus_dm']) & (df['plus_dm'] > 0), 0)
        df['minus_dm'] = df['minus_dm'].where((df['minus_dm'] > df['plus_dm']) & (df['minus_dm'] > 0), 0)

        # Smooth moving averages (Wilder’s smoothing)
        tr_smooth = df['tr'].rolling(window=period).mean()
        plus_di = 100 * (df['plus_dm'].rolling(window=period).mean() / (tr_smooth + 1e-10))
        minus_di = 100 * (df['minus_dm'].rolling(window=period).mean() / (tr_smooth + 1e-10))

        dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)) * 100
        adx = dx.rolling(window=period).mean()

        df['signal'] = 0
        df.loc[(plus_di > minus_di) & (adx > threshold), 'signal'] = 1   # Buy
        df.loc[(minus_di > plus_di) & (adx > threshold), 'signal'] = -1  # Sell

        return df['signal']
