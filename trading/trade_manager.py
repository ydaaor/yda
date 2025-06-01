import json
from data.positions import Positions

class TradeManager:
    def __init__(self):
        self.positions = Positions("data/positions.json")
        # ניתן להוסיף טעינת הגדרות מ-settings.json

    def buy_stocks(self, candidates):
        for ticker in candidates:
            if self.positions.can_buy(ticker):
                # בדיקת סכום פנוי, בדיקת מניעה מכפילות, הגבלת קנייה ל-1 ביום
                # שליחת פקודת קנייה (API)
                # עדכון positions.json
                # עדכון לוג
                pass