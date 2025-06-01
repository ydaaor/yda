import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PASS = os.getenv("EMAIL_HOST_PASSWORD")


def send_email_alert(symbols, to_addr=None):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Missing email credentials.")
        return
    if not symbols:
        return

    recipient = to_addr or EMAIL_USER
    subject = "התראת רובוט מסחר - נמצאו מניות מתאימות"
    body = "נמצאו מניות מתאימות:\n\n" + "\n".join(symbols)

    msg = MIMEText(body, _charset="utf-8")
    msg['Subject'] = Header(subject, "utf-8")
    msg['From'] = EMAIL_USER
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipient, msg.as_string())
        print("Mail alert sent!")
    except Exception as e:
        print("Error sending email:", e)


class TradeManager:
    def __init__(self):
        # כאן תוכל לטעון משתני סביבה, credentials, אובייקטים של API וכו'
        pass

    def buy_stocks(self, symbols):
        us_symbols = [s for s in symbols if self.is_us_stock(s)]
        if us_symbols:
            send_email_alert(us_symbols)
        for symbol in us_symbols:
            self.buy_stock(symbol)

    def buy_stock(self, symbol):
        # כאן תממש את הקנייה בפועל מול הברוקר/Alpaca
        print(f"קונה מניה אמריקאית: {symbol}")
        # דוגמה: שליחת פקודת קנייה ל-API
        # order = self.api.submit_order(symbol=symbol, qty=1, side='buy', type='market', time_in_force='gtc')
        # return order
        pass

    @staticmethod
    def is_us_stock(symbol):
        # סימבול אמריקאי לרוב לא מכיל נקודה (.)
        # סימבולים עם נקודה הם בדרך כלל לא אמריקאיים (למשל: 'BCE.TO', 'BHP.AX')
        return '.' not in symbol