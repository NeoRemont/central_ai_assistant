import re
from datetime import datetime, timedelta
import payouts_module as payouts

# =============================
# Helpers
# =============================

def is_payouts_intent(text: str) -> bool:
    text = text.lower()
    return text.startswith("выплат") or text.startswith("начисл") or text.startswith("остаток") or text.startswith("отчёт")

def parse_date(word: str) -> str:
    word = word.strip().lower()
    today = datetime.now()
    if word in ["сегодня", "today"]:
        return today.strftime("%Y-%m-%d")
    if word in ["вчера", "yesterday"]:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if word in ["завтра", "tomorrow"]:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    # Форматы DD.MM.YYYY или YYYY-MM-DD
    try:
        if "." in word:
            return datetime.strptime(word, "%d.%m.%Y").strftime("%Y-%m-%d")
        if "-" in word:
            return datetime.strptime(word, "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        return word
    return word

def route_command(text: str) -> str:
    txt = text.strip()
    low = txt.lower()

    if low.startswith("выплат"):
        # Формат: выплати Димону 200000 по Загорянка-Лайф сегодня
        m = re.match(r"выплат[аи]\s+(\S+)\s+(\d+)\s*(?:по\s+([^\s]+))?\s*(.*)", txt, re.IGNORECASE)
        if not m:
            return "❌ Не понял команду выплаты"
        emp, amt, obj, rest = m.groups()
        date = parse_date(rest) if rest else None
        res = payouts.add_payout(employee=emp, amount=float(amt), obj=obj, when=date)
        return f"✅ Выплата добавлена: {res}"

    if low.startswith("начисл"):
        # Формат: начисли Ризо 150000 по Титова, акт №3
        m = re.match(r"начисл[и]\s+(\S+)\s+(\d+)\s*по\s+([^,]+)(?:,\s*акт\s*(.*))?", txt, re.IGNORECASE)
        if not m:
            return "❌ Не понял команду начисления"
        emp, amt, obj, act = m.groups()
        res = payouts.add_accrual(employee=emp, amount=float(amt), obj=obj, act=act or "")
        return f"✅ Начисление добавлено: {res}"

    if low.startswith("остаток"):
        # Формат: остаток по Димону
        m = re.match(r"остаток\s+по\s+(.+)", txt, re.IGNORECASE)
        if not m:
            return "❌ Не понял команду остатка"
        target = m.group(1)
        res = payouts.get_balance(target=target)
        return f"📊 Остатки: {res}"

    if low.startswith("отчёт"):
        # Формат: отчёт за 2025-08
        m = re.match(r"отч[её]т\s+(?:за\s+)?(.+)", txt, re.IGNORECASE)
        if not m:
            return "❌ Не понял команду отчёта"
        period = m.group(1)
        res = payouts.get_report(period=period)
        return f"📄 Отчёт: {res}"

    return "❌ Неизвестная команда"
