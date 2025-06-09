from risk.risk_manager import RiskManager

rm = RiskManager(symbol="BTCUSDT", leverage=20)

# Example: simulate entry at $28,000
usdt_amount = rm.calculate_position_size(entry_price=28000)
