import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()

from scanner.stock_scanner import StockScanner
from trading.trade_manager import TradeManager
from trading.risk_controller import RiskController
from logger.logger import Logger
from interface import web_interface

def main():
    scanner = StockScanner()
    trade_manager = TradeManager()
    risk_controller = RiskController()
    logger = Logger()

    scanner_interval = 300  # 5 דקות
    risk_check_interval = 60  # דקה

    last_scan = 0
    last_risk_check = 0

    while True:
        current_time = time.time()
        if current_time - last_scan >= scanner_interval:
            candidates = scanner.scan()
            trade_manager.buy_stocks(candidates)
            last_scan = current_time

        if current_time - last_risk_check >= risk_check_interval:
            risk_controller.check_positions()
            last_risk_check = current_time

        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(
        target=lambda: web_interface.app.run(host='0.0.0.0', port=8080, use_reloader=False),
        daemon=True
    ).start()
    main()