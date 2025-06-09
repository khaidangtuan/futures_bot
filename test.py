#from data.data_loader import get_historical_klines
#df = get_historical_klines('BTCUSDT', interval='1h', limit=72)
#print(df.head())

# test.py

from market_screening.screener import screen_top_symbols
from config.settings import TOP_N_SYMBOLS

def main():
    print(f"\nRunning Market Screener for Top {TOP_N_SYMBOLS} Symbols...\n")
    top_symbols = screen_top_symbols()

    if not top_symbols:
        print("No symbols were selected based on the criteria.")
    else:
        print("Top Symbols Selected:")
        for symbol in top_symbols:
            print(f"- {symbol}")

if __name__ == "__main__":
    main()
