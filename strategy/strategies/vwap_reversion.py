# strategy/strategies/vwap_reversion.py

import pandas as pd
from strategy.base_strategy import BaseStrategy

class VWAPReversionStrategy(BaseStrategy):
    """
    VWAP mean reversion strategy.
    Buy when price < VWAP - threshold;
    Sell when price > VWAP + threshold.
    """

    @classmethod
    def default_hyperparameters(cls) -> dict:
        return {
            "window": 20,
            "std_dev": 1.5
        }

    @classmethod
    def hyperparameter_space(cls) -> dict:
        return {
            "window": [14, 20, 30],
            "std_dev": [1, 1.5, 2]
        }

    def name(self) -> str:
        return "VWAPReversion"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        window = self.hyperparameters["window"]
        std_dev = self.hyperparameters["std_dev"]

        # === VWAP Calculation ===
        df['cum_volume'] = df['volume'].cumsum()
        df['cum_vwap'] = (df['close'] * df['volume']).cumsum()
        df['vwap'] = df['cum_vwap'] / (df['cum_volume'] + 1e-10)

        # Rolling VWAP (optional smoothing)
        df['rolling_mean'] = df['close'].rolling(window=window).mean()
        df['rolling_std'] = df['close'].rolling(window=window).std()
        df['upper_band'] = df['vwap'] + (std_dev * df['rolling_std'])
        df['lower_band'] = df['vwap'] - (std_dev * df['rolling_std'])

        # === Signal Logic ===
        df['signal'] = 0
        df.loc[df['close'] < df['lower_band'], 'signal'] = 1   # Buy
        df.loc[df['close'] > df['upper_band'], 'signal'] = -1  # Sell

        return df['signal']
