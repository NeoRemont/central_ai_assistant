import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# =============================
# Config (env-first; Render-ready)
# =============================
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID") or os.getenv("SHEETS_SPREADSHEET_ID")
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")  # JSON string (preferred on Render)
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # fallback to file path

SHEET_EMPLOYEES = os.getenv("SHEET_EMPLOYEES", "Справочники_Сотрудники")
SHEET_OBJECTS = os.getenv("SHEET_OBJECTS", "Справочники_Объекты")
SHEET_ARTICLES = os.getenv("SHEET_ARTICLES", "Справочники_Статьи")
SHEET_PAYOUTS = os.getenv("SHEET_PAYOUTS", "Выплаты")
SHEET_ACCRUALS = os.getenv("SHEET_ACCRUALS", "Начисления")
SHEET_BALANCES = os.getenv("SHEET_BALANCES", "Взаиморасчёты")
SHEET_REPORTS = os.getenv("SHEET_REPORTS", "Отчёты")
SHEET_LOG = os.getenv("SHEET_LOG", "__LOG")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

# =============================
# Auth helpers
# =============================

def build_sheets_service():
    """Create Google Sheets API service using env-based creds (Render-friendly)."""
    if SERVICE_ACCOUNT_JSON:
        info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    elif GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        creds = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)
    else:
        raise RuntimeError("No Google credentials provided. Set SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS.")

    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets().values()

# =============================
# Utilities
# =============================

def now_local_iso() -> str:
    tz = ZoneInfo(TIMEZONE) if ZoneInfo else None
    dt = datetime.now(tz) if tz else datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def read_sheet(values_service, sheet_name: str) -> List[List[str]]:
    resp = values_service.get(spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!").execute()
    return resp.get("values", [])

def append_row(values_service, sheet_name: str, row: List[Any]):
    return values_service.append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A:Z",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

def ensure_id(values: List[List[str]], id_prefix: str, name: str, id_col: int, name_col: int) -> Optional[str]:
    """Return ID by name or pass through if already an ID."""
    if not name:
        return None
    name = str(name).strip()
    if name.upper().startswith(id_prefix):
        return name
    # find by name exact match (case-insensitive)
    lower = name.lower()
    for row in values[1:]:  # skip header
        if len(row) > max(id_col, name_col) and row[name_col].strip().lower() == lower:
            return row[id_col].strip()
    return None

# =============================
# Core API
# =============================

def add_payout(
    employee: str,
    amount: float,
    obj: Optional[str] = None,
    article: str = "Выплата по акту",
    method: str = "Наличные",
    when: Optional[str] = None,  # ISO date (YYYY-MM-DD) or None=now
    comment: str = "",
    doc_link: str = "",
) -> Dict[str, Any]:
    values = build_sheets_service()
    employees = read_sheet(values, SHEET_EMPLOYEES)
    objects = read_sheet(values, SHEET_OBJECTS)

    emp_id = ensure_id(employees, "EMP-", employee, id_col=0, name_col=1)
    if not emp_id:
        raise ValueError(f"Сотрудник не найден: {employee}")

    obj_id = ensure_id(objects, "OBJ-", obj, id_col=0, name_col=1) if obj else ""

    # date
    if when:
        d = when
    else:
        d = now_local_iso().split(" ")[0]

    row = [
        d,             # Дата
        emp_id,        # Сотрудник_ID
        obj_id,        # Объект_ID
        article,       # Статья
        float(amount), # Сумма
        method,        # Метод
        comment,       # Комментарий
        doc_link,      # Документ/ссылка
    ]

    try:
        append_row(values, SHEET_PAYOUTS, row)
        # log
        append_row(values, SHEET_LOG, [now_local_iso(), "payouts_module", "ADD_PAYOUT", json.dumps({"emp": employee, "obj": obj, "amount": amount})])
        return {"ok": True, "written": row}
    except HttpError as e:
        return {"ok": False, "error": str(e)}

def add_accrual(
    employee: str,
    amount: float,
    obj: str,
    act: str = "",
    article: str = "Начисление по акту",
    when: Optional[str] = None,  # ISO date
    comment: str = "",
) -> Dict[str, Any]:
    values = build_sheets_service()
    employees = read_sheet(values, SHEET_EMPLOYEES)
    objects = read_sheet(values, SHEET_OBJECTS)

    emp_id = ensure_id(employees, "EMP-", employee, id_col=0, name_col=1)
    if not emp_id:
        raise ValueError(f"Сотрудник не найден: {employee}")

    obj_id = ensure_id(objects, "OBJ-", obj, id_col=0, name_col=1)
    if not obj_id:
        raise ValueError(f"Объект не найден: {obj}")

    d = when if when else now_local_iso().split(" ")[0]

    row = [
        d,             # Дата
        emp_id,        # Сотрудник_ID
        obj_id,        # Объект_ID
        act,           # Основание (№ акта)
        article,       # Статья
        float(amount), # Сумма
        comment,       # Комментарий
    ]

    try:
        append_row(values, SHEET_ACCRUALS, row)
        append_row(values, SHEET_LOG, [now_local_iso(), "payouts_module", "ADD_ACCRUAL", json.dumps({"emp": employee, "obj": obj, "amount": amount})])
        return {"ok": True, "written": row}
    except HttpError as e:
        return {"ok": False, "error": str(e)}

def _collect_pairs(values_service) -> Tuple[Dict[str, str], Dict[str, str]]:
    employees = read_sheet(values_service, SHEET_EMPLOYEES)
    objects = read_sheet(values_service, SHEET_OBJECTS)
    emp_names = {r[0]: r[1] for r in employees[1:] if len(r) >= 2}
    obj_names = {r[0]: r[1] for r in objects[1:] if len(r) >= 2}
    return emp_names, obj_names

def get_balance(target: Optional[str] = None, period_from: Optional[str] = None, period_to: Optional[str] = None) -> Dict[str, Any]:
    """Return aggregated balances. target can be employee name/ID or object name/ID."""
    values = build_sheets_service()
    accr = read_sheet(values, SHEET_ACCRUALS)
    pay = read_sheet(values, SHEET_PAYOUTS)
    emp_names, obj_names = _collect_pairs(values)

    def in_period(dstr: str) -> bool:
        if not dstr:
            return True
        d = dstr[:10]
        if period_from and d < period_from:
            return False
        if period_to and d > period_to:
            return False
        return True

    def match_target(emp_id: str, obj_id: str) -> bool:
        if not target:
            return True
        t = target.strip()
        # direct IDs
        if t.upper().startswith("EMP-"):
            return emp_id == t
        if t.upper().startswith("OBJ-"):
            return obj_id == t
        # by names
        return (emp_names.get(emp_id, "").lower() == t.lower()) or (obj_names.get(obj_id, "").lower() == t.lower())

    totals: Dict[Tuple[str, str], Dict[str, float]] = {}

    # Accruals rows: [Дата, EMP_ID, OBJ_ID, Акт, Статья, Сумма, Коммент]
    for r in accr[1:]:
        if len(r) < 6:
            continue
        d, emp_id, obj_id, *_rest = r[:7]
        sum_str = r[5] if len(r) > 5 else ""
        if not in_period(d):
            continue
        if not match_target(emp_id, obj_id):
            continue
        key = (emp_id, obj_id)
        totals.setdefault(key, {"Начислено": 0.0, "Выплачено": 0.0})
        try:
            totals[key]["Начислено"] += float(str(sum_str).replace(" ", "").replace(",", "."))
        except ValueError:
            pass

    # Payouts rows: [Дата, EMP_ID, OBJ_ID, Статья, Сумма, Метод, Коммент, Док]
    for r in pay[1:]:
        if len(r) < 5:
            continue
        d, emp_id, obj_id, *_rest = r[:8]
        sum_str = r[4] if len(r) > 4 else ""
        if not in_period(d):
            continue
        if not match_target(emp_id, obj_id):
            continue
        key = (emp_id, obj_id)
        totals.setdefault(key, {"Начислено": 0.0, "Выплачено": 0.0})
        try:
            totals[key]["Выплачено"] += float(str(sum_str).replace(" ", "").replace(",", "."))
        except ValueError:
            pass

    # Build results
    result_rows = []
    summary = {"Начислено": 0.0, "Выплачено": 0.0, "Остаток": 0.0}
    for (emp_id, obj_id), vals in totals.items():
        ost = vals["Начислено"] - vals["Выплачено"]
        result_rows.append({
            "Сотрудник_ID": emp_id,
            "Сотрудник": emp_names.get(emp_id, ""),
            "Объект_ID": obj_id,
            "Объект": obj_names.get(obj_id, ""),
            "Начислено": round(vals["Начислено"], 2),
            "Выплачено": round(vals["Выплачено"], 2),
            "Остаток": round(ost, 2),
        })
        summary["Начислено"] += vals["Начислено"]
        summary["Выплачено"] += vals["Выплачено"]
        summary["Остаток"] += ost

    # Log
    append_row(values, SHEET_LOG, [now_local_iso(), "payouts_module", "GET_BALANCE", json.dumps({"target": target, "from": period_from, "to": period_to})])

    return {"ok": True, "summary": {k: round(v, 2) for k, v in summary.items()}, "rows": result_rows}

def get_report(period: Optional[str] = None, employee: Optional[str] = None, obj: Optional[str] = None) -> Dict[str, Any]:
    """Report by YYYY-MM or YYYY-MM-DD:YYYY-MM-DD; optional filters by employee or object (name or ID)."""
    period_from = period_to = None
    if period:
        if ":" in period:
            period_from, period_to = period.split(":", 1)
        elif len(period) == 7:  # YYYY-MM
            period_from = period + "-01"
            # naive month end calc
            y, m = map(int, period.split("-"))
            if m == 12:
                period_to = f"{y}-12-31"
            else:
                period_to = f"{y}-{m+1:02d}-01"
        else:
            # single day
            period_from = period
            period_to = period

    target = employee or obj
    res = get_balance(target=target, period_from=period_from, period_to=period_to)

    # Log
    values = build_sheets_service()
    append_row(values, SHEET_LOG, [now_local_iso(), "payouts_module", "GET_REPORT", json.dumps({"period": period, "employee": employee, "obj": obj})])
    return res

# Convenience CLI-like runner for quick checks
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["add_payout", "add_accrual", "get_balance", "get_report"]) 
    parser.add_argument("--employee")
    parser.add_argument("--amount", type=float)
    parser.add_argument("--obj")
    parser.add_argument("--article")
    parser.add_argument("--method")
    parser.add_argument("--when")
    parser.add_argument("--comment")
    parser.add_argument("--doc")
    parser.add_argument("--period")
    args = parser.parse_args()

    if args.action == "add_payout":
        print(add_payout(employee=args.employee, amount=args.amount, obj=args.obj, article=args.article or "Выплата по акту", method=args.method or "Наличные", when=args.when, comment=args.comment or "", doc_link=args.doc or ""))
    elif args.action == "add_accrual":
        print(add_accrual(employee=args.employee, amount=args.amount, obj=args.obj, act=args.comment or "", article=args.article or "Начисление по акту", when=args.when, comment=""))
    elif args.action == "get_balance":
        print(get_balance(target=args.employee or args.obj))
    elif args.action == "get_report":
        print(get_report(period=args.period, employee=args.employee, obj=args.obj))
