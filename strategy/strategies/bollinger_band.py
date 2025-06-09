# strategy/strategies/bollinger_band.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class BollingerBandStrategy(BaseStrategy):
    """
    Mean reversion using Bollinger Bands.
    Buy when price < lower band; Sell when price > upper band.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "window": 20,
            "std_dev": 2
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "window": [14, 20, 30],
            "std_dev": [1.5, 2, 2.5]
        }

    def name(self) -> str:
        return "BollingerBand"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        window = self.hyperparameters["window"]
        std_dev = self.hyperparameters["std_dev"]

        df['ma'] = df['close'].rolling(window=window).mean()
        df['std'] = df['close'].rolling(window=window).std()

        df['upper'] = df['ma'] + (std_dev * df['std'])
        df['lower'] = df['ma'] - (std_dev * df['std'])

        df['signal'] = 0
        df.loc[df['close'] < df['lower'], 'signal'] = 1   # Buy
        df.loc[df['close'] > df['upper'], 'signal'] = -1  # Sell

        return df['signal']
