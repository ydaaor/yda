import datetime

class Logger:
    def __init__(self, log_path="data/trades_log.txt"):
        self.log_path = log_path

    def log(self, message):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} | {message}\n")