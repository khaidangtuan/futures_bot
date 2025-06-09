# strategy/strategies/stochastic_rsi.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class StochasticRSIStrategy(BaseStrategy):
    """
    Combines RSI and Stochastic Oscillator for signal generation.
    Buy when %K crosses above %D from oversold; 
    Sell when %K crosses below %D from overbought.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "rsi_period": 14,
            "stoch_period": 14,
            "signal_period": 3,
            "overbought": 80,
            "oversold": 20
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "rsi_period": [10, 14, 21],
            "stoch_period": [10, 14, 21],
            "signal_period": [3, 5],
            "overbought": [70, 80, 85],
            "oversold": [15, 20, 30]
        }

    def name(self) -> str:
        return "StochasticRSI"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        rsi_period = self.hyperparameters["rsi_period"]
        stoch_period = self.hyperparameters["stoch_period"]
        signal_period = self.hyperparameters["signal_period"]
        overbought = self.hyperparameters["overbought"]
        oversold = self.hyperparameters["oversold"]

        # === RSI Calculation ===
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=rsi_period).mean()
        avg_loss = loss.rolling(window=rsi_period).mean()

        rs = avg_gain / (avg_loss + 1e-10)
        df['rsi'] = 100 - (100 / (1 + rs))

        # === Stochastic RSI Calculation ===
        lowest_rsi = df['rsi'].rolling(window=stoch_period).min()
        highest_rsi = df['rsi'].rolling(window=stoch_period).max()

        df['stoch_rsi'] = (df['rsi'] - lowest_rsi) / (highest_rsi - lowest_rsi + 1e-10)
        df['%K'] = df['stoch_rsi'] * 100
        df['%D'] = df['%K'].rolling(window=signal_period).mean()

        # === Signal Generation ===
        df['signal'] = 0
        buy_condition = (df['%K'] > df['%D']) & (df['%K'] < oversold)
        sell_condition = (df['%K'] < df['%D']) & (df['%K'] > overbought)

        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1

        return df['signal']
