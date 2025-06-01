import pandas as pd
import os

def export_monthly_report(log_path="data/trades_log.txt", output_dir="reports"):
    # קורא את הלוג, בונה דוח חודשי ושומר לקובץ Excel
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df = pd.read_csv(log_path, sep="|", header=None, names=["datetime", "msg"])
    month = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m').iloc[0]
    report_path = os.path.join(output_dir, f"monthly_report_{month}.xlsx")
    df.to_excel(report_path, index=False)
    return report_path