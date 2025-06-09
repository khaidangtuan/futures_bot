binance_trading_bot/
│
├── config/
│   └── settings.py                # Centralized configuration
│
├── data/
│   └── data_loader.py            # Handles all data fetching
│
├── market_screening/
│   └── screener.py               # Top-N symbol selection based on volume & volatility
│
├── strategy/
│   ├── base_strategy.py          # Abstract strategy template
│   ├── strategies/               # Folder to store pre-defined strategies
│   └── strategy_loader.py        # Dynamically loads strategies
│
├── backtest/
│   └── backtester.py             # Optimizes and backtests strategies
│
├── execution/
│   └── executor.py               # Executes trades based on signals
│
├── risk/
│   └── risk_manager.py           # Manages position sizing, SL, strategy SL
│
├── logs/
│   └── bot.log                   # Output log file
│
├── main.py                       # Entry point
└── requirements.txt              # Dependencies
