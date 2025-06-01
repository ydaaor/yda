import os
import requests
import datetime
from dotenv import load_dotenv

class StockScanner:
    def __init__(self):
        load_dotenv()
        self.alpaca_key = os.getenv("ALPACA_KEY")
        self.finnhub_key = os.getenv("FINNHUB_KEY")
        # add other keys as needed

    def scan(self):
        # 1. קבלת רשימת מניות לפי שווי שוק מה-API
        # 2. סינון טכני: מגמה, ממוצעים נעים, higher highs, פריצות ודפוסים
        # 3. בדיקת נפח מסחר
        # 4. בדיקת חדשות שליליות
        # 5. מגבלות זמן מסחר ותנאי שוק כללי (S&P500, VIX)
        # מחזיר רשימת tickers מתאימים

        # DEMO: מחזיר רשימה ריקה, יש להחליף למימוש אמיתי
        return []

    # ניתן להוסיף כאן פונקציות עזר: בדיקת ממוצעים, חדשות וכו'