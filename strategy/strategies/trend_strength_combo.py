# strategy/strategies/trend_strength_combo.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class TrendStrengthComboStrategy(BaseStrategy):
    """
    Combined trend confirmation strategy using:
    - MACD crossover
    - ADX trend strength
    - Price vs Moving Average
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "ma_period": 50,
            "adx_period": 14,
            "adx_threshold": 20
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "macd_fast": [8, 12, 15],
            "macd_slow": [21, 26, 30],
            "macd_signal": [6, 9],
            "ma_period": [20, 50, 100],
            "adx_period": [10, 14, 20],
            "adx_threshold": [20, 25, 30]
        }

    def name(self) -> str:
        return "TrendStrengthCombo"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        hp = self.hyperparameters

        # === MACD ===
        df['ema_fast'] = df['close'].ewm(span=hp['macd_fast'], adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=hp['macd_slow'], adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=hp['macd_signal'], adjust=False).mean()

        # === MA Filter ===
        df['ma'] = df['close'].rolling(window=hp['ma_period']).mean()

        # === ADX Calculation ===
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['close'].shift()).abs()
        df['tr3'] = (df['low'] - df['close'].shift()).abs()
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

        df['+dm'] = df['high'].diff()
        df['-dm'] = df['low'].diff().abs()
        df['+dm'] = df['+dm'].where((df['+dm'] > df['-dm']) & (df['+dm'] > 0), 0)
        df['-dm'] = df['-dm'].where((df['-dm'] > df['+dm']) & (df['-dm'] > 0), 0)

        tr_smooth = df['tr'].rolling(window=hp['adx_period']).mean()
        plus_di = 100 * df['+dm'].rolling(window=hp['adx_period']).mean() / (tr_smooth + 1e-10)
        minus_di = 100 * df['-dm'].rolling(window=hp['adx_period']).mean() / (tr_smooth + 1e-10)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)) * 100
        df['adx'] = dx.rolling(window=hp['adx_period']).mean()

        # === Signal Logic ===
        df['signal'] = 0
        buy_cond = (
            (df['macd'] > df['macd_signal']) &
            (df['close'] > df['ma']) &
            (df['adx'] > hp['adx_threshold'])
        )
        sell_cond = (
            (df['macd'] < df['macd_signal']) &
            (df['close'] < df['ma']) &
            (df['adx'] > hp['adx_threshold'])
        )
        df.loc[buy_cond, 'signal'] = 1
        df.loc[sell_cond, 'signal'] = -1

        return df['signal']
