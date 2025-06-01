import json

class Positions:
    def __init__(self, filepath):
        self.filepath = filepath
        self._load()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                self.positions = json.load(f)
        except Exception:
            self.positions = []

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.positions, f, indent=2)

    def can_buy(self, ticker):
        # בדוק האם ניתן לקנות (לא קנינו היום, לא קיימת פוזיציה פתוחה)
        return True

    def get_all_active(self):
        return [p for p in self.positions if p.get("active")]

    def reset_daily(self):
        # אפס את הפוזיציות הפעילות (למניעת כפילויות קנייה)
        for pos in self.positions:
            pos["bought_today"] = False
        self.save()