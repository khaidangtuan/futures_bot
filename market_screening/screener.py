# market_screening/screener.py

import time
import pandas as pd
from binance.client import Client
from config.settings import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    TOP_N_SYMBOLS,
    MIN_VOLUME_USDT,
    VOLATILITY_LOOKBACK_DAYS,
    VOLATILITY_TIMEFRAME
)
from data.data_loader import get_historical_klines
from utils.logger import get_logger

# Configure logging
logger = get_logger(__name__)

# Initialize Binance client
client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


def get_usdt_futures_symbols():
    """Fetch all USDT-margined futures symbols from Binance"""
    exchange_info = client.futures_exchange_info()
    usdt_symbols = [
        s['symbol'] for s in exchange_info['symbols']
        if s['contractType'] == 'PERPETUAL' and s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING'
    ]
    return usdt_symbols


def get_24h_volume(symbol):
    """Fetch 24h traded volume in USDT for a symbol"""
    try:
        ticker = client.futures_ticker(symbol=symbol)
        volume = float(ticker['quoteVolume'])  # USDT volume
        return volume
    except Exception as e:
        logger.error(f"Error fetching volume for {symbol}: {e}")
        return 0.0


def calculate_volatility(symbol):
    """Calculate standard deviation of returns for given symbol"""
    try:
        # Determine number of candles from days + interval
        interval_map = {
            '1m': 1440, '3m': 480, '5m': 288, '15m': 96,
            '30m': 48, '1h': 24, '2h': 12, '4h': 6,
            '6h': 4, '8h': 3, '12h': 2, '1d': 1
        }

        candles_per_day = interval_map.get(VOLATILITY_TIMEFRAME)
        if candles_per_day is None:
            raise ValueError(f"Unsupported timeframe: {VOLATILITY_TIMEFRAME}")

        limit = candles_per_day * VOLATILITY_LOOKBACK_DAYS
        df = get_historical_klines(symbol, interval=VOLATILITY_TIMEFRAME, limit=limit)

        df['returns'] = df['close'].pct_change()
        volatility = df['returns'].std()
        return volatility if pd.notna(volatility) else 0.0
    except Exception as e:
        logger.error(f"Error calculating volatility for {symbol}: {e}")
        return 0.0


def screen_top_symbols(top_n=TOP_N_SYMBOLS, min_volume=MIN_VOLUME_USDT):
    """Return top N symbols by volume and volatility"""
    logger.info("Screening top symbols...")
    symbols = get_usdt_futures_symbols()
    symbol_stats = []

    for symbol in symbols:
        volume = get_24h_volume(symbol)
        if volume < min_volume:
            continue
        volatility = calculate_volatility(symbol)
        symbol_stats.append({
            'symbol': symbol,
            'volume': volume,
            'volatility': volatility
        })
        time.sleep(0.1)  # Rate limiting

    df = pd.DataFrame(symbol_stats)
    if df.empty:
        logger.warning("No symbols met the screening criteria.")
        return []

    df['score'] = df['volume'] * df['volatility']
    df = df.sort_values(by='score', ascending=False)
    top_symbols = df.head(top_n)['symbol'].tolist()

    logger.info(f"Top {top_n} symbols selected: {top_symbols}")
    return top_symbols
