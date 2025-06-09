# risk/risk_manager.py

'''
- Calculate USDT position size
- Based on account balance
- Leverage
- Acceptable risk per trade (%)
- Stop loss distance (in %) from entry
'''

from binance.client import Client
from config.settings import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    RISK_PER_TRADE,
    DEFAULT_LEVERAGE,
    STOP_LOSS_PCT
)
from utils.logger import get_logger

logger = get_logger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

class RiskManager:
    def __init__(self, symbol: str, leverage: int = DEFAULT_LEVERAGE):
        self.symbol = symbol.upper()
        self.leverage = leverage

    def get_account_balance(self) -> float:
        try:
            balance_info = client.futures_account_balance()
            usdt_balance = next(b for b in balance_info if b['asset'] == 'USDT')
            return float(usdt_balance['balance'])
        except Exception as e:
            logger.error(f"❌ Failed to fetch account balance: {e}")
            return 0.0

    def calculate_position_size(self, entry_price: float) -> float:
        """
        Calculates the position size in USDT for the given entry price,
        based on risk % and stop loss % from config.
        """
        balance = self.get_account_balance()
        if balance == 0:
            logger.warning("⚠️ Balance is zero, position size = 0")
            return 0.0

        risk_usdt = balance * RISK_PER_TRADE
        sl_distance_pct = STOP_LOSS_PCT
        
        # Leverage allows us to trade more with less
        #position_usdt = min((risk_usdt / (sl_distance_pct)), balance) * self.leverage
        position_usdt = risk_usdt * self.leverage
    
        logger.info(f"💰 Position size: {position_usdt:.2f} USDT based on {RISK_PER_TRADE*100:.1f}% risk")

        return round(position_usdt, 2)
