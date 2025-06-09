# 📘 Strategy Summary – Algorithmic Trading System

This document describes the core trading strategies implemented in the system.  
Each strategy is modular, inherits from `BaseStrategy`, and supports backtesting, optimization, and live execution.

---

## ✅ Strategy List

| Strategy Name              | Type               | Entry Signal Logic | Key Hyperparameters |
|---------------------------|--------------------|--------------------|---------------------|
| **ATR Channel**           | Breakout / Volatility | Price crosses ATR-based channel | `atr_period`, `multiplier` |
| **Bollinger Band**        | Mean Reversion     | Price touches upper/lower band | `window`, `std_dev` |
| **Donchian Breakout**     | Trend Breakout     | Price breaks N-period high/low | `window` |
| **MACD Crossover**        | Momentum / Reversal| MACD crosses signal line | `fast_period`, `slow_period`, `signal_period` |
| **MACD Trend**            | Trend Following    | MACD rising above/below 0 | `fast_period`, `slow_period`, `signal_period` |
| **MA Crossover**          | Trend Following    | Short MA crosses long MA | `short_window`, `long_window` |
| **RSI Reversion**         | Mean Reversion     | RSI < oversold or > overbought | `rsi_period`, `overbought`, `oversold` |
| **Stochastic RSI**        | Reversion + Momentum | %K crosses %D from extremes | `rsi_period`, `stoch_period`, `signal_period`, `overbought`, `oversold` |
| **Supertrend**            | Trend Following + Volatility | Price crosses dynamic trend line | `atr_period`, `multiplier` |
| **Trend ADX**             | Trend Confirmation | +DI/-DI with ADX > threshold | `adx_period`, `adx_threshold` |
| **Trend Strength Combo**  | Multi-Indicator Filter | MACD + MA + ADX agree | `macd_*`, `ma_period`, `adx_*` |
| **VWAP Reversion**        | Mean Reversion     | Price deviates from VWAP | `window`, `std_dev` |

---

## 🧠 Strategy Interface

    Each strategy implements:

    ```python
    def generate_signals(df: pd.DataFrame) -> pd.Series
    def default_hyperparameters() -> dict
    def hyperparameter_space() -> dict
    def name() -> str
