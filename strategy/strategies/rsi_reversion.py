# strategy/strategies/rsi_reversion.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class RSIReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy using RSI.
    Buy when RSI < oversold; Sell when RSI > overbought.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "rsi_period": 14,
            "overbought": 70,
            "oversold": 30
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "rsi_period": [10, 14, 21],
            "overbought": [65, 70, 75],
            "oversold": [25, 30, 35]
        }

    def name(self) -> str:
        return "RSIReversion"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()

        period = self.hyperparameters["rsi_period"]
        overbought = self.hyperparameters["overbought"]
        oversold = self.hyperparameters["oversold"]

        # RSI calculation
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / (avg_loss + 1e-10)
        df['rsi'] = 100 - (100 / (1 + rs))

        df['signal'] = 0
        df.loc[df['rsi'] < oversold, 'signal'] = 1    # Buy
        df.loc[df['rsi'] > overbought, 'signal'] = -1 # Sell

        return df['signal']
