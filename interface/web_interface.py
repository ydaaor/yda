from flask import Flask, jsonify, render_template_string, request
import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

ALPACA_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_API_SECRET")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
FINNHUB_TOKEN = os.getenv("FINNHUB_API_KEY")  # ודא שמפתח זה קיים בקובץ .env

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>לוח בקרה למסחר רובוטי</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background: #fff9f3;
            color: #ff9100;
            font-family: 'Heebo', Arial, sans-serif;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .container {
            max-width: 1100px;
            margin: 40px auto;
            background: #fff;
            padding: 32px 28px 28px 28px;
            border-radius: 20px;
            box-shadow: 0 4px 32px #ff910033;
        }
        h1 {
            text-align: center;
            margin-bottom: 24px;
            color: #ff9100;
            letter-spacing: 1px;
        }
        .actions {
            text-align: center;
            margin-bottom: 32px;
            margin-top: 0;
        }
        .actions h2 {
            color: #ff9100;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .actions button {
            margin: 10px 8px;
            padding: 12px 32px;
            font-size: 1.08em;
            border-radius: 8px;
            border: none;
            background: linear-gradient(90deg, #ffb300 10%, #ff9100 90%);
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 8px #ff910022;
            transition: background 0.15s, transform 0.13s;
        }
        .actions button.sos {
            background: linear-gradient(90deg, #ff1744 10%, #ff9100 90%);
            color: #fff;
            font-weight: bold;
            border: 2px solid #fff;
            box-shadow: 0 0 12px #ff174466;
        }
        .actions button.sos:hover {
            background: linear-gradient(90deg, #ff5252 10%, #ff6f00 90%);
        }
        .actions button:hover {
            background: linear-gradient(90deg, #ffa726 10%, #ff6f00 90%);
            transform: translateY(-2px) scale(1.04);
        }
        #action-result {
            display:none;
            color: #ff6f00;
            font-weight: bold;
            margin-top: 20px;
            font-size: 1.08em;
            text-align: center;
            letter-spacing: 0.5px;
        }
        .account-data, .positions-data, .charts-section {
            background: #fff3e0;
            border-radius: 12px;
            padding: 20px 18px 10px 18px;
            margin-bottom: 32px;
            box-shadow: 0 2px 16px #ff910011;
        }
        .account-data table, .positions-data table {
            width: 100%;
            border-collapse: collapse;
            font-size: 1.08em;
        }
        .account-data th, .account-data td, .positions-data th, .positions-data td {
            text-align: right;
            padding: 8px 10px;
        }
        .account-data th, .positions-data th {
            background: #ffb74d;
            color: #fff;
            font-weight: 600;
        }
        .account-data tr:nth-child(even), .positions-data tr:nth-child(even) {
            background: #ffecb3;
        }
        .positions-data h2, .charts-section h2 {
            color: #ff9100;
            text-align: center;
        }
        .chart-container {
            width: 400px;
            height: 260px;
            margin: 24px auto;
            display: inline-block;
            vertical-align: top;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 1px 8px #ff910011;
            padding: 8px 8px 8px 8px;
        }
        .chart-symbol {
            text-align: center;
            font-weight: bold;
            color: #ff9100;
            margin-bottom: 0;
            margin-top: 0;
            font-size: 1.12em;
            letter-spacing: 1px;
        }
        @media (max-width: 900px) {
            .chart-container { width: 98vw; }
            .container { max-width: 100vw; }
        }
        .positions-summary-row {
            text-align: left;
            margin-top: 10px;
            font-size: 1.13em;
            font-weight: bold;
        }
    </style>
    <script>
        function formatHebrewDate(isoDate) {
            if (!isoDate) return '';
            const date = new Date(isoDate);
            const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
            return date.toLocaleDateString('he-IL', options);
        }

        async function loadAccountData() {
            const res = await fetch('/api/alpaca_account');
            const data = await res.json();
            const table = document.getElementById('account-table');
            if (res.status !== 200) {
                table.innerHTML = `<tr><td colspan="2" style="color:red;">${data.error || 'שגיאה'}</td></tr>`;
                return;
            }
            let html = '';
            for (const [k, v] of Object.entries(data)) {
                let value = v;
                if (k === "created_at") value = formatHebrewDate(v);
                html += `<tr><th>${translateField(k)}</th><td>${value}</td></tr>`;
            }
            table.innerHTML = html;
        }

        async function loadPositionsData() {
            const res = await fetch('/api/alpaca_positions');
            const data = await res.json();
            const table = document.getElementById('positions-table');
            let summaryRow = document.getElementById('positions-summary-row');
            if (!summaryRow) {
                summaryRow = document.createElement('div');
                summaryRow.id = 'positions-summary-row';
                table.parentNode.appendChild(summaryRow);
            }
            if (res.status !== 200) {
                table.innerHTML = `<tr><td colspan="9" style="color:red;">${data.error || 'שגיאה'}</td></tr>`;
                summaryRow.innerHTML = "";
                return;
            }
            if (!data.length) {
                table.innerHTML = `<tr><td colspan="9" style="color:#888;">אין פוזיציות פעילות</td></tr>`;
                summaryRow.innerHTML = "";
                document.getElementById('charts-section').innerHTML = '';
                return;
            }
            let html = `<tr>
                <th>סמל</th>
                <th>שם מניה</th>
                <th>כמות</th>
                <th>מחיר קניה ממוצע</th>
                <th>מחיר שוק נוכחי</th>
                <th>שינוי יומי (%)</th>
                <th>רווח/הפסד יומי</th>
                <th>רווח/הפסד כולל</th>
            </tr>`;
            let symbols = [];
            let total_pl = 0;
            for (const pos of data) {
                html += `<tr>
                    <td>${pos.symbol}</td>
                    <td>${pos.name || '-'}</td>
                    <td>${parseFloat(pos.qty).toLocaleString()}</td>
                    <td>${parseFloat(pos.avg_entry_price).toFixed(2)}</td>
                    <td>${parseFloat(pos.current_price).toFixed(2)}</td>
                    <td style="color:${pos.change_today >= 0 ? '#388e3c':'#d32f2f'}">${(pos.change_today*100).toFixed(2)}%</td>
                    <td style="color:${pos.unrealized_intraday_pl >= 0 ? '#388e3c':'#d32f2f'}">${parseFloat(pos.unrealized_intraday_pl).toFixed(2)}</td>
                    <td style="color:${pos.unrealized_pl >= 0 ? '#388e3c':'#d32f2f'}">${parseFloat(pos.unrealized_pl).toFixed(2)}</td>
                </tr>`;
                symbols.push(pos.symbol);
                total_pl += parseFloat(pos.unrealized_pl);
            }
            table.innerHTML = html;
            // שורת סיכום
            let totalColor = total_pl >= 0 ? '#388e3c' : '#d32f2f';
            const summaryHtml = `<div class="positions-summary-row" style="color:${totalColor}">
                סה"כ רווח/הפסד מתיק ההשקעות: ${total_pl.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}
            </div>`;
            summaryRow.innerHTML = summaryHtml;

            loadCharts(symbols);
        }

        function translateField(field) {
            const fields = {
                'account_number': 'מספר חשבון',
                'status': 'סטטוס',
                'currency': 'מטבע',
                'buying_power': 'כח קניה',
                'cash': 'מזומן',
                'portfolio_value': 'שווי תיקים',
                'pattern_day_trader': 'סוחר יומי?',
                'trading_blocked': 'מסחר חסום?',
                'transfers_blocked': 'העברות חסומות?',
                'trade_suspended_by_user': 'המסחר הושהה ע״י המשתמש?',
                'created_at': 'נוצר בתאריך',
                'shorting_enabled': 'שורטינג פעיל?',
                'long_market_value': 'שווי פוזיציות לונג',
            };
            return fields[field] || field;
        }

        function showResult(msg) {
            const elem = document.getElementById('action-result');
            elem.innerText = msg;
            elem.style.display = 'block';
            setTimeout(() => { elem.style.display = 'none'; }, 3100);
        }

        async function robotAction(action) {
            if (action === 'sos_sell_all') {
                if (!confirm('האם אתה בטוח שברצונך למכור את כל הפוזיציות במחיר השוק? פעולה זו אינה הפיכה!')) {
                    return;
                }
            }
            const res = await fetch('/api/robot_action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action})
            });
            const data = await res.json();
            showResult(data.message || data.error || 'בוצע');
            if(action === "sos_sell_all"){
                loadPositionsData();
            }
        }

        async function loadCharts(symbols) {
            const chartsDiv = document.getElementById('charts-section');
            if (!symbols || !symbols.length) {
                chartsDiv.innerHTML = '';
                return;
            }
            let chartHtml = '<h2>גרפי מניות לפוזיציות פתוחות</h2>';
            for (const symbol of symbols) {
                chartHtml += `
                <div class="chart-container">
                    <div class="chart-symbol">${symbol}</div>
                    <canvas id="chart-${symbol}" width="370" height="220"></canvas>
                </div>
                `;
            }
            chartsDiv.innerHTML = chartHtml;

            // נטען נתוני גרף לכל מניה
            for (const symbol of symbols) {
                fetch(`/api/stock_chart/${symbol}`)
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        const ctx = document.getElementById(`chart-${symbol}`).getContext('2d');
                        ctx.font = '18px Arial';
                        ctx.fillStyle = '#ff1744';
                        ctx.fillText("אין נתוני גרף זמינים", 80, 110);
                        return;
                    }
                    const ctx = document.getElementById(`chart-${symbol}`).getContext('2d');
                    new window.Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.times,
                            datasets: [{
                                label: 'מחיר',
                                data: data.prices,
                                borderColor: '#ff9100',
                                backgroundColor: 'rgba(255,145,0,0.10)',
                                fill: true,
                                pointRadius: 0
                            }]
                        },
                        options: {
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                x: {
                                    ticks: { display: false }
                                },
                                y: {
                                    ticks: { color: '#ff9100' }
                                }
                            }
                        }
                    });
                });
            }
        }

        window.onload = () => {
            loadAccountData();
            loadPositionsData();
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>לוח בקרה למסחר רובוטי</h1>
        <div class="actions">
            <h2>שליטה ברובוט</h2>
            <button onclick="robotAction('start_scan')">התחל סריקה</button>
            <button onclick="robotAction('stop_scan')">עצור סריקה</button>
            <button onclick="robotAction('pause_trading')">השהה מסחר</button>
            <button onclick="robotAction('resume_trading')">חדש מסחר</button>
            <button onclick="robotAction('risk_check')">בדיקת סיכונים</button>
            <button class="sos" onclick="robotAction('sos_sell_all')">🚨 SOS מכור הכל</button>
            <div id="action-result"></div>
        </div>
        <div class="account-data">
            <h2 style="text-align:center; color:#ff9100;">נתוני חשבון Alpaca</h2>
            <table id="account-table"></table>
        </div>
        <div class="positions-data">
            <h2>פירוט תיק - כל הפוזיציות</h2>
            <table id="positions-table"></table>
            <div id="positions-summary-row"></div>
        </div>
        <div class="charts-section" id="charts-section">
            <!-- Chart.js charts will be injected here -->
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/alpaca_account")
def alpaca_account():
    if not ALPACA_KEY or not ALPACA_SECRET:
        return jsonify({"error": "חסר ALPACA_API_KEY או ALPACA_API_SECRET ב-ENV"}), 400
    url = f"{ALPACA_BASE_URL}/v2/account"
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            return jsonify(r.json())
        else:
            return jsonify({"error": "נכשל בקבלת נתוני החשבון", "status": r.status_code, "details": r.text}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alpaca_positions")
def alpaca_positions():
    if not ALPACA_KEY or not ALPACA_SECRET:
        return jsonify({"error": "חסר ALPACA_API_KEY או ALPACA_API_SECRET ב-ENV"}), 400
    url = f"{ALPACA_BASE_URL}/v2/positions"
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            positions = r.json()
            for pos in positions:
                if "name" not in pos:
                    pos["name"] = None
            return jsonify(positions)
        else:
            return jsonify({"error": "נכשל בקבלת פוזיציות", "status": r.status_code, "details": r.text}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/robot_action", methods=["POST"])
def robot_action():
    data = request.get_json()
    action = data.get("action")
    if action == "start_scan":
        print("סריקה התחילה!")
        return jsonify({"message": "הסריקה החלה"})
    elif action == "stop_scan":
        print("סריקה נעצרה!")
        return jsonify({"message": "הסריקה נעצרה"})
    elif action == "pause_trading":
        print("המסחר הושהה!")
        return jsonify({"message": "המסחר הושהה"})
    elif action == "resume_trading":
        print("המסחר חודש!")
        return jsonify({"message": "המסחר חודש"})
    elif action == "risk_check":
        print("בוצעה בדיקת סיכונים!")
        return jsonify({"message": "בוצעה בדיקת סיכונים"})
    elif action == "sos_sell_all":
        url_positions = f"{ALPACA_BASE_URL}/v2/positions"
        try:
            r = requests.get(url_positions, headers=HEADERS)
            if r.status_code != 200:
                return jsonify({"error": "נכשל בקבלת פוזיציות", "details": r.text}), 400
            positions = r.json()
            if not positions:
                return jsonify({"message": "אין פוזיציות למכור"}), 200
            errors = []
            for pos in positions:
                symbol = pos["symbol"]
                qty = pos["qty"]
                side = "sell"
                order_url = f"{ALPACA_BASE_URL}/v2/orders"
                order_data = {
                    "symbol": symbol,
                    "qty": qty,
                    "side": side,
                    "type": "market",
                    "time_in_force": "gtc"
                }
                order_resp = requests.post(order_url, headers=HEADERS, json=order_data)
                if order_resp.status_code not in (200,201):
                    errors.append(f"{symbol}: {order_resp.text}")
            if errors:
                return jsonify({"error": "חלק מהפוזיציות לא נמכרו", "details": errors}), 500
            return jsonify({"message": "כל הפוזיציות נשלחו למכירה במחיר שוק!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "פעולה לא מוכרת"}), 400

@app.route("/api/stock_chart/<symbol>")
def stock_chart(symbol):
    # נסה קודם Alpaca (אם יש לך data subscription)
    try:
        url = f"{ALPACA_BASE_URL}/v2/stocks/{symbol}/bars"
        params = {
            "timeframe": "5Min",
            "limit": 60
        }
        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code == 200:
            bars = r.json().get("bars", [])
            prices = [b["c"] for b in bars]
            times = [b["t"][11:16] for b in bars]
            if prices and times:
                return jsonify({"prices": prices, "times": times})
    except Exception:
        pass

    # נסה Finnhub
    try:
        if not FINNHUB_TOKEN:
            return jsonify({"error": "לא הוגדר מפתח Finnhub"}), 400
        now = int(datetime.datetime.now().timestamp())
        start = now - 3*24*60*60  # 3 ימים אחורה
        finnhub_url = (
            f"https://finnhub.io/api/v1/stock/candle"
            f"?symbol={symbol}&resolution=5&from={start}&to={now}&token={FINNHUB_TOKEN}"
        )
        resp = requests.get(finnhub_url)
        if resp.status_code == 200:
            js = resp.json()
            if js.get("s") == "ok" and js.get("c") and js.get("t"):
                prices = js["c"]
                times = [
                    datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
                    for ts in js["t"]
                ]
                return jsonify({"prices": prices, "times": times})
            else:
                return jsonify({"error": "אין נתוני גרף זמינים (Finnhub)"}), 400
        return jsonify({"error": "אין נתוני גרף זמינים (Finnhub)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)