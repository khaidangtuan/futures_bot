# main.py

import time
from datetime import datetime
from market_screening.screener import screen_top_symbols
from backtest.backtester import run_batch_optimization
from execution.executor import Executor
from strategy.strategy_loader import load_strategy
from data.data_loader import get_historical_klines
from risk.risk_manager import RiskManager
from utils.logger import get_logger
from config.settings import (
    TRADE_TIMEFRAME,
    DEFAULT_LEVERAGE,
    TRAILING_STOP_LOSS_PCT,
    STOP_LOSS_PCT,
    MAX_TESTS_PER_STRATEGY,
    PROFIT_EXPECT
)
import warnings
warnings.filterwarnings('ignore')

logger = get_logger(__name__)


def main():
    # === 1. Market Screening ===
    logger.info("🔍 Screening market...")
    symbols = screen_top_symbols()

    # === 2. Backtest & Optimize ===
    logger.info("🧠 Optimizing strategies...")
    results = run_batch_optimization(
        symbols=symbols,
        timeframes=TRADE_TIMEFRAME,
        max_tests_per_strategy=MAX_TESTS_PER_STRATEGY
    )

    # === 3. Select Best Strategy Combo ===
    best = max(results, key=lambda r: r["score"])
    logger.info(f"🏆 Selected: {best['strategy']} on {best['symbol']} [{best['timeframe']}] ")
    logger.info(f"🏆 Backtest performance: return = {best['return']*100:.2f}, daily PnL = {best['avg_daily_pnl']*100:.2f}, sharpe = {best['sharpe_ratio']:.4f}, win_rate = {best['win_rate']*100:.2f} ")

    symbol = best['symbol']
    timeframe = best['timeframe']
    strategy_name = best['strategy']
    config = best['config'] if isinstance(best['config'], dict) else eval(best['config'])

    # === 4. Initialize Core Components ===
    executor = Executor(symbol=symbol, leverage=DEFAULT_LEVERAGE)
    risk_mgr = RiskManager(symbol=symbol, leverage=DEFAULT_LEVERAGE)
    strategy = load_strategy(strategy_name+'Strategy', symbol, timeframe, config)

    # === 5. Main Loop: Signal + Execution ===
    logger.info("🚀 Starting trading loop...")
    last_trade_time = None
    position_killed = False

    while True:
        try:
            now = datetime.utcnow()
            if not last_trade_time or (now - last_trade_time).total_seconds() >= timeframe_to_seconds(timeframe):
                last_trade_time = now

                # === 5.1 Get signal ===
                df = get_historical_klines(symbol, interval=timeframe, limit=100)
                df['signal'] = strategy.generate_signals(df)
                signal = int(df['signal'].iloc[-1])

                # === 5.2 Position Management ===
                position = executor.get_open_position()

                if not position:
                    entry_price = df['close'].iloc[-1]
                    usdt_amt = risk_mgr.calculate_position_size(entry_price)
                    executor.place_order(usdt_amount=usdt_amt, signal=signal)
                    prev_current_price = None
                else:
                    pos_side = 1 if position['side'] == "LONG" else -1
                    if signal == 0 or signal == pos_side:
                        logger.info("⚪ Holding position")
                    elif signal == -pos_side:
                        executor.close_position()
                        time.sleep(1)
                        entry_price = df['close'].iloc[-1]
                        usdt_amt = risk_mgr.calculate_position_size(entry_price)
                        executor.place_order(usdt_amount=usdt_amt, signal=signal)
                        prev_current_price = None
            # === 6. Track & Risk Control Every 10 Seconds ===
            position = executor.get_open_position()
            if position:
                entry = position['entryPrice']
                #current_price = get_historical_klines(symbol, interval=timeframe, limit=1)['close'].iloc[-1]
                current_price = position['markPrice']
                side = position['side']
                unreal_pnl = position['unRealizedProfit']
                hard_sl = STOP_LOSS_PCT
                trail_sl = TRAILING_STOP_LOSS_PCT

                # Trail SL logic
                if side == "LONG":
                    change_pct = ((current_price - entry) / entry) * 100 * DEFAULT_LEVERAGE
                else:
                    change_pct = ((entry - current_price) / entry) * 100 * DEFAULT_LEVERAGE

                logger.info(f"📈 PnL: {unreal_pnl:.2f} | Change: {change_pct:.2f}%")

                if change_pct < -hard_sl * 100:
                    logger.error(f"🛑 HARD STOP LOSS hit ({change_pct:.2f}%) — terminating strategy.")
                    executor.close_position()
                    break
                
                if change_pct > PROFIT_EXPECT*100*DEFAULT_LEVERAGE:
                    if c:
                        if ((current_price - prev_current_price)/prev_current_price)*DEFAULT_LEVERAGE < -trail_sl:
                            logger.warning(f"🔻 Trailing TP hit: {change_pct:.2f}% gain — close the trade & wait for other signal.")
                            executor.close_position()
                        
                        if current_price > prev_current_price:
                            prev_current_price = current_price
                    else:
                        prev_current_price = current_price
                else:
                    if change_pct < -trail_sl*100:
                        logger.warning(f"🔻 Trailing SL hit: {change_pct:.2f}% gain — close the trade & wait for other signal.")
                        executor.close_position()
                
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info("🛑 Manual shutdown requested.")
            executor.close_position()
            break
        except Exception as e:
            logger.error(f"❌ Runtime error: {e}")
            time.sleep(5)


def timeframe_to_seconds(tf: str) -> int:
    unit = tf[-1]
    val = int(tf[:-1])
    return val * {"m": 60, "h": 3600, "d": 86400}[unit]


if __name__ == "__main__":
    main()
