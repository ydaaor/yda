import time
from data.positions import Positions

class RiskController:
    def __init__(self):
        self.positions = Positions("data/positions.json")

    def check_positions(self):
        for pos in self.positions.get_all_active():
            # בדוק רווח/הפסד
            # אם רווח >= 10% - למכור (take profit)
            # אם הפסד >= 5% - למכור (stop loss)
            pass

    def nightly_reset(self):
        # אתחול אוטומטי של positions.json בכל לילה
        self.positions.reset_daily()