# data/data_loader.py

import time
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET
from utils.logger import get_logger

logger = get_logger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

_CACHE = {}

def get_historical_klines(symbol: str, interval: str, limit: int = 1000, use_cache=True) -> pd.DataFrame:
    """
    Safely fetch historical kline data with caching and retry logic.
    """
    cache_key = f"{symbol}_{interval}_{limit}"
    if use_cache and cache_key in _CACHE:
        return _CACHE[cache_key]

    retries = 3
    for attempt in range(retries):
        try:
            logger.debug(f"📥 Fetching candles: {symbol} [{interval}]")
            klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'num_trades',
                'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
            ])

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({
                'open': float, 'high': float, 'low': float, 'close': float, 'volume': float
            })

            if use_cache:
                _CACHE[cache_key] = df

            # Sleep to avoid rate limit
            time.sleep(0.3)
            return df

        except BinanceAPIException as e:
            if "IP banned" in str(e):
                logger.critical(f"🛑 IP banned by Binance: {e}")
                raise
            elif attempt < retries - 1:
                logger.warning(f"⚠️ Retry {attempt + 1} for {symbol}: {e}")
                time.sleep(2)
            else:
                logger.error(f"❌ Failed to fetch data for {symbol} after {retries} attempts.")
                raise
