import os
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/api/alpaca_account')
def alpaca_account():
    headers = {
        "APCA-API-KEY-ID": os.getenv("ALPACA_KEY"),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET")
    }
    url = "https://paper-api.alpaca.markets/v2/account"  # עבור חשבון LIVE החלף ל- https://api.alpaca.markets/v2/account
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return jsonify({
            "account_number": data.get("account_number"),
            "status": data.get("status"),
            "cash": data.get("cash"),
            "buying_power": data.get("buying_power"),
            "portfolio_value": data.get("portfolio_value"),
            "equity": data.get("equity"),
            "last_equity": data.get("last_equity"),
            "multiplier": data.get("multiplier"),
            "currency": data.get("currency"),
            "created_at": data.get("created_at"),
        })
    else:
        return jsonify({"error": resp.text}), resp.status_code

# שאר הראוטים של Flask שלך (פוזיציות, עסקאות וכו')

def run_app():
    app.run(host='0.0.0.0', port=8080)