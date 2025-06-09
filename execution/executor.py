# execution/executor.py

from binance.client import Client
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET
from utils.logger import get_logger

logger = get_logger(__name__)
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

class Executor:
    def __init__(self, symbol: str, leverage: int = 10):
        self.symbol = symbol.upper()
        self.leverage = leverage

        # Set leverage (Binance USDT Futures)
        try:
            client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)
            logger.info(f"⚙️ Set leverage to {self.leverage}x on {self.symbol}")
        except Exception as e:
            logger.warning(f"Could not set leverage: {e}")
    
    def get_quantity_precision(self, symbol: str) -> int:
        """
        Fetch lot size precision (number of decimal places allowed for quantity).
        """
        exchange_info = client.futures_exchange_info()
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol.upper():
                for f in s['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        step_size = float(f['stepSize'])
                        precision = abs(round(-1 * (step_size).as_integer_ratio()[1].bit_length() - 1))
                        return max(0, precision)
        return 3  # fallback
    
    def get_futures_quantity_precision(self, symbol: str) -> tuple:
        """
        Returns (precision, min_qty) for a futures symbol.
        """
        try:
            info = client.futures_exchange_info()
            for s in info['symbols']:
                if s['symbol'] == symbol.upper():
                    for f in s['filters']:
                        if f['filterType'] == "LOT_SIZE":
                            step_size = float(f['stepSize'])  # e.g. 0.001
                            precision = abs(int(round(-1 * (step_size).as_integer_ratio()[1].bit_length() - 1)))
                            return precision, step_size
        except Exception as e:
            logger.error(f"❌ Failed to get precision for {symbol}: {e}")
        return 3, 0.001  # safe fallback
    
    def round_down(self, value: float, step: float) -> float:
        return (value // step) * step

    def place_order(self, usdt_amount: float, signal: int) -> dict:
        """
        Places a market order in the signal direction.
        :param usdt_amount: Position size in USDT
        :param signal: 1 = BUY, -1 = SELL
        :return: Order dict
        """
        if signal not in [1, -1]:
            logger.info("⚪ No action on HOLD signal")
            return {}

        try:
            ticker = client.futures_symbol_ticker(symbol=self.symbol)
            price = float(ticker['price'])
            raw_qty = usdt_amount / price

            precision, step = self.get_futures_quantity_precision(self.symbol)
            raw_qty = usdt_amount / price
            quantity = self.round_down(raw_qty, step)
            #precision = self.get_quantity_precision(self.symbol)
            #print(precision)
            #quantity = round(raw_qty, precision)
            
            if quantity < step:
                logger.warning("⚠️ Quantity below minimum step size. Order skipped.")
                return {}
                
            if quantity <= 0:
                logger.warning("⚠️ Computed quantity too small, skipping order.")
                return {}

            side = "BUY" if signal == 1 else "SELL"
            logger.info(f"🛒 Placing {side} | Qty: {quantity} ({precision}dp)")

            order = client.futures_create_order(
                symbol=self.symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            logger.info(f"✅ Order placed: {order['orderId']}")
            return order

        except Exception as e:
            logger.error(f"❌ Order failed: {e}")
            return {}

    def get_open_position(self) -> dict:
        """
        Returns the current open position, if any.
        :return: dict with position details or empty if no position
        """
        try:
            positions = client.futures_position_information(symbol=self.symbol)
            pos = next((p for p in positions if float(p['positionAmt']) != 0), None)
            if pos:
                #logger.info(f"📈 Open position: {pos['positionSide']} | Size: {pos['positionAmt']} @ {pos['entryPrice']}")
                pos['side'] = "LONG" if float(pos['positionAmt']) > 0 else "SHORT"
                pos['markPrice'] = float(pos['markPrice'])
                pos['entryPrice'] = float(pos['entryPrice'])
                pos['positionAmt'] = float(pos['positionAmt'])
                pos['unRealizedProfit'] = float(pos['unRealizedProfit'])
                return pos
                #return {
                #    "side": "LONG" if float(pos['positionAmt']) > 0 else "SHORT",
                #    "entry_price": float(pos['entryPrice']),
                #    "amount": float(pos['positionAmt']),
                #    "unrealized_pnl": float(pos['unRealizedProfit'])
                #}
            else:
                logger.info("📉 No open position")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to get position: {e}")
            return {}

    def close_position(self) -> dict:
        """
        Closes any existing position using a MARKET order.
        :return: Order response or empty
        """
        pos = self.get_open_position()
        if not pos:
            logger.info("⚪ No position to close.")
            return {}

        quantity = abs(float(pos['positionAmt']))
        side = "SELL" if pos['side'] == "LONG" else "BUY"

        try:
            order = client.futures_create_order(
                symbol=self.symbol,
                side=side,
                type="MARKET",
                quantity=abs(quantity),
                reduceOnly=True
            )
            logger.info(f"🔻 Closed position with {side} order: {order['orderId']}")
            return order
        except Exception as e:
            logger.error(f"❌ Failed to close position: {e}")
            return {}
