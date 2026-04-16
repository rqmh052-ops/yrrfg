import asyncio
import html
import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================
# إعدادات عامة
# =========================

BOT_TOKEN = "8769355202:AAEJFIXicyJNdhor2HM98daIUQ9wFZd0mwY"
ADMIN_ID = 8287678319
LOG_CHANNEL_ID = "-1003886614381"
DATABASE_PATH = "bot.db"
REQUEST_TIMEOUT = 20
APP_NAME = "محوّل التضخم"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required")

# =========================
# تسجيل الأحداث المحلي
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("inflation-bot")

# =========================
# حالة المحادثة
# =========================

SELECT_AMOUNT, SELECT_COUNTRY, SELECT_START, SELECT_END, CONFIRM = range(5)

# =========================
# الدول المدعومة
# =========================

COUNTRIES = {
    "us": {"name": "الولايات المتحدة", "emoji": "🇺🇸", "provider": "bls"},
    "ca": {"name": "كندا", "emoji": "🇨🇦", "provider": "worldbank"},
    "gb": {"name": "المملكة المتحدة", "emoji": "🇬🇧", "provider": "worldbank"},
    "eg": {"name": "مصر", "emoji": "🇪🇬", "provider": "worldbank"},
}

# =========================
# أدوات تنسيق وصياغة
# =========================

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

SECRET_PATTERNS = [
    (
        re.compile(
            r"(?i)\b(bot[_-]?token|token|api[_-]?key|secret|password|passwd|cookie)\b\s*[:=]\s*([^\s]+)"
        ),
        r"\1=[مخفي]",
    ),
    (re.compile(r"(?i)\b(cf_clearance|session|bearer)\b\s*[:=]\s*([^\s]+)"), r"\1=[مخفي]"),
]


def sanitize_for_log(text: str) -> str:
    if not text:
        return text
    out = text
    for pattern, repl in SECRET_PATTERNS:
        out = pattern.sub(repl, out)
    out = re.sub(r"\b[A-Za-z0-9_\-]{32,}\b", "[مخفي]", out)
    return out[:3500]


def user_label(update: Update) -> str:
    u = update.effective_user
    if not u:
        return "مستخدم غير معروف"
    if u.username:
        return f"@{u.username}"
    name = " ".join(p for p in [u.first_name, u.last_name] if p).strip()
    return name or f"ID:{u.id}"


def display_country(code: str) -> str:
    c = COUNTRIES.get(code)
    if not c:
        return code
    return f"{c['emoji']} {c['name']}"


def format_number(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    return f"{value:,.2f}"


def normalize_numeric_text(text: str) -> str:
    text = text.translate(ARABIC_DIGITS)
    text = text.strip().replace(" ", "")
    return text


def parse_amount(text: str) -> Optional[int]:
    """يقبل: 9999، 9,999، 9.999، 9-999"""
    if not text:
        return None
    t = normalize_numeric_text(text)
    if re.fullmatch(r"\d{1,3}([,\.\-_]\d{3})*|\d+", t):
        digits = re.sub(r"[,\.\-_]", "", t)
        if digits.isdigit() and int(digits) > 0:
            return int(digits)
    return None


def parse_year_or_date(text: str) -> Optional[date]:
    if not text:
        return None
    t = normalize_numeric_text(text)
    if re.fullmatch(r"\d{4}", t):
        y = int(t)
        if 1900 <= y <= 2100:
            return date(y, 1, 1)
        return None
    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", t):
        try:
            y, m, d = map(int, t.split("-"))
            return date(y, m, d)
        except ValueError:
            return None
    return None


async def reply_text(target: Any, text: str, **kwargs):
    if isinstance(target, Update):
        if target.message:
            return await target.message.reply_text(text, **kwargs)
        if target.callback_query and target.callback_query.message:
            return await target.callback_query.message.reply_text(text, **kwargs)
    elif isinstance(target, CallbackQuery):
        if target.message:
            return await target.message.reply_text(text, **kwargs)
    elif isinstance(target, Message):
        return await target.reply_text(text, **kwargs)
    raise RuntimeError("Unable to reply to target")


# =========================
# قاعدة البيانات
# =========================

class Database:
    def __init__(self, path: str):
        self.path = path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    last_seen TEXT,
                    requests_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    country_code TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    source_start REAL,
                    source_end REAL,
                    adjusted_value REAL,
                    difference REAL,
                    inflation_pct REAL,
                    created_at TEXT NOT NULL,
                    raw_amount_text TEXT,
                    raw_start_text TEXT,
                    raw_end_text TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    event_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_user(self, update: Update):
        u = update.effective_user
        if not u:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name, language_code, last_seen, requests_count)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT requests_count FROM users WHERE user_id=?), 0))
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    language_code=excluded.language_code,
                    last_seen=excluded.last_seen
                """,
                (
                    u.id,
                    u.username,
                    u.first_name,
                    u.last_name,
                    u.language_code,
                    datetime.utcnow().isoformat(),
                    u.id,
                ),
            )
            conn.commit()

    def increment_requests(self, user_id: int):
        with self._connect() as conn:
            conn.execute("UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?", (user_id,))
            conn.commit()

    def save_request(self, data: Dict[str, Any]):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO requests (
                    user_id, username, country_code, amount, start_date, end_date, provider,
                    source_start, source_end, adjusted_value, difference, inflation_pct,
                    created_at, raw_amount_text, raw_start_text, raw_end_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["user_id"],
                    data.get("username"),
                    data["country_code"],
                    data["amount"],
                    data["start_date"],
                    data["end_date"],
                    data["provider"],
                    data.get("source_start"),
                    data.get("source_end"),
                    data.get("adjusted_value"),
                    data.get("difference"),
                    data.get("inflation_pct"),
                    datetime.utcnow().isoformat(),
                    data.get("raw_amount_text"),
                    data.get("raw_start_text"),
                    data.get("raw_end_text"),
                ),
            )
            conn.commit()

    def save_event(self, user_id: Optional[int], username: Optional[str], event_type: str, details: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events (user_id, username, event_type, details, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    username,
                    event_type,
                    details,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()

    def stats(self) -> Dict[str, int]:
        with self._connect() as conn:
            users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            requests_ = conn.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
            events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        return {"users": users, "requests": requests_, "events": events}

    def recent_requests(self, limit: int = 10) -> List[sqlite3.Row]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM requests ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return rows

    def all_users(self, limit: int = 20) -> List[sqlite3.Row]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY last_seen DESC LIMIT ?", (limit,)).fetchall()
        return rows

    def get_request_by_id(self, req_id: int) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM requests WHERE id = ?", (req_id,)).fetchone()
        return row


db = Database(DATABASE_PATH)


# =========================
# مزوّدات التضخم
# =========================

@dataclass
class InflationResult:
    adjusted_value: float
    source_start: float
    source_end: float
    provider: str
    measurement_note: str


class InflationError(RuntimeError):
    pass


class BLSProvider:
    SERIES_ID = "CUUR0000SA0"

    @staticmethod
    @lru_cache(maxsize=128)
    def fetch_series(start_year: int, end_year: int) -> Dict[Tuple[int, int], float]:
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        payload = {
            "seriesid": [BLSProvider.SERIES_ID],
            "startyear": str(start_year),
            "endyear": str(end_year),
        }
        r = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "REQUEST_SUCCEEDED":
            raise InflationError("تعذّر جلب بيانات BLS")
        series = data["Results"]["series"][0]["data"]
        result: Dict[Tuple[int, int], float] = {}
        for item in series:
            period = item.get("period", "")
            if not period.startswith("M"):
                continue
            month = int(period[1:])
            year = int(item["year"])
            value = float(item["value"])
            result[(year, month)] = value
        return result

    @classmethod
    def get_cpi_for_date(cls, target: date) -> float:
        data = cls.fetch_series(target.year - 1, target.year)
        candidates = [
            (y, m, v)
            for (y, m), v in data.items()
            if (y < target.year) or (y == target.year and m <= target.month)
        ]
        if not candidates:
            raise InflationError("لا توجد بيانات CPI كافية لهذا التاريخ")
        _, _, v = sorted(candidates)[-1]
        return v

    @classmethod
    def calculate(cls, amount: int, start: date, end: date) -> InflationResult:
        source_start = cls.get_cpi_for_date(start)
        source_end = cls.get_cpi_for_date(end)
        adjusted = amount * (source_end / source_start)
        note = "اعتمد على مؤشر CPI-U الشهري من BLS"
        return InflationResult(adjusted, source_start, source_end, "BLS", note)


class WorldBankProvider:
    @staticmethod
    @lru_cache(maxsize=128)
    def fetch_series(country: str) -> Dict[int, float]:
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/FP.CPI.TOTL"
        params = {"format": "json", "per_page": 2000}
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        payload = r.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise InflationError("تعذّر جلب بيانات World Bank")
        series = payload[1] or []
        result: Dict[int, float] = {}
        for item in series:
            year = item.get("date")
            value = item.get("value")
            if year is None or value is None:
                continue
            result[int(year)] = float(value)
        return result

    @classmethod
    def get_cpi_for_year(cls, country: str, year: int) -> float:
        data = cls.fetch_series(country)
        available = [y for y in data if y <= year]
        if not available:
            raise InflationError("لا توجد بيانات سنوية كافية")
        return data[max(available)]

    @classmethod
    def calculate(cls, amount: int, country: str, start: date, end: date) -> InflationResult:
        source_start = cls.get_cpi_for_year(country, start.year)
        source_end = cls.get_cpi_for_year(country, end.year)
        adjusted = amount * (source_end / source_start)
        note = "اعتمد على مؤشر CPI السنوي من World Bank"
        return InflationResult(adjusted, source_start, source_end, "World Bank", note)


def calculate_inflation(country_code: str, amount: int, start_dt: date, end_dt: date) -> InflationResult:
    if country_code == "us":
        return BLSProvider.calculate(amount, start_dt, end_dt)
    if country_code in {"ca", "gb", "eg"}:
        return WorldBankProvider.calculate(amount, country_code, start_dt, end_dt)
    raise InflationError("الدولة غير مدعومة حالياً")


# =========================
# القوائم والأزرار
# =========================


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🧮 ابدأ الحساب", callback_data="menu:start")],
            [InlineKeyboardButton("ℹ️ المساعدة", callback_data="menu:help")],
        ]
    )


def country_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{COUNTRIES['us']['emoji']} الولايات المتحدة", callback_data="country:us"),
                InlineKeyboardButton(f"{COUNTRIES['ca']['emoji']} كندا", callback_data="country:ca"),
            ],
            [
                InlineKeyboardButton(f"{COUNTRIES['gb']['emoji']} المملكة المتحدة", callback_data="country:gb"),
                InlineKeyboardButton(f"{COUNTRIES['eg']['emoji']} مصر", callback_data="country:eg"),
            ],
            [InlineKeyboardButton("↩️ رجوع", callback_data="nav:back_start")],
        ]
    )


def end_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ استخدم اليوم", callback_data="end:today"),
                InlineKeyboardButton("✍️ أدخل تاريخًا", callback_data="end:manual"),
            ],
            [InlineKeyboardButton("↩️ رجوع", callback_data="nav:back_country")],
        ]
    )


def back_to_home_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="nav:home")],
            [InlineKeyboardButton("🧮 حساب جديد", callback_data="menu:start")],
        ]
    )


# =========================
# رسائل الواجهة
# =========================

WELCOME_TEXT = (
    "مرحبًا بك 👋\n\n"
    "هذا البوت يحسب قيمة مبلغ قديم بعد التضخم حتى تاريخ اليوم، "
    "مع عرض:\n"
    "• القيمة الحالية\n"
    "• الفرق\n"
    "• نسبة التضخم\n\n"
    "اضغط زر البدء أو أرسل /start."
)

HELP_TEXT = (
    "طريقة الاستخدام:\n"
    "1) أدخل المبلغ\n"
    "2) اختر الدولة\n"
    "3) أدخل سنة البداية\n"
    "4) اختر اليوم أو أدخل تاريخًا\n\n"
    "يدعم إدخال الأرقام بهذه الصيغ:\n"
    "9999 — 9,999 — 9.999 — 9-999\n\n"
    "الدعم الأساسي والأدق للولايات المتحدة، مع دعم سنوي اختياري لبعض الدول الأخرى."
)


def format_result_text(amount: int, start_dt: date, end_dt: date, country_code: str, result: InflationResult) -> str:
    country = display_country(country_code)
    current_value = result.adjusted_value
    difference = current_value - amount
    inflation_pct = (current_value / amount - 1) * 100

    return (
        f"✅ <b>نتيجة الحساب</b>\n\n"
        f"الدولة: {country}\n"
        f"المبلغ الأصلي: {format_number(amount)}\n"
        f"سنة/تاريخ البداية: {start_dt.isoformat()}\n"
        f"سنة/تاريخ النهاية: {end_dt.isoformat()}\n\n"
        f"القيمة الحالية: <b>{format_number(current_value)}</b>\n"
        f"الفرق: <b>{format_number(difference)}</b>\n"
        f"نسبة التضخم: <b>{inflation_pct:.2f}%</b>\n\n"
        f"المصدر الحسابي: {result.provider}\n"
        f"ملاحظة: {result.measurement_note}"
    )


# =========================
# تسجيل إلى القناة
# =========================


class EventLogger:
    def __init__(self):
        self.channel_id = LOG_CHANNEL_ID

    async def log(self, bot, text: str):
        clean = sanitize_for_log(text)
        logger.info(clean)
        if self.channel_id:
            try:
                await bot.send_message(chat_id=self.channel_id, text=f"تعاملات:\n{clean}")
            except Exception as e:
                logger.warning("Failed to send channel log: %s", e)


event_logger = EventLogger()


# =========================
# جلسة المستخدم
# =========================


def reset_session(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.upsert_user(update)
    reset_session(context)
    await event_logger.log(context.bot, f"▶️ المستخدم {user_label(update)} ضغط /start.")
    if update.message:
        await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu())
    return SELECT_AMOUNT


async def menu_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    db.upsert_user(update)
    reset_session(context)
    await event_logger.log(context.bot, f"▶️ المستخدم {user_label(update)} ضغط زر بدء الحساب.")
    await reply_text(query or update, "أرسل المبلغ المراد حسابه، مثال: 9,999 أو 9999")
    return SELECT_AMOUNT


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    await reply_text(query or update, HELP_TEXT, reply_markup=main_menu())
    await event_logger.log(context.bot, f"ℹ️ المستخدم {user_label(update)} فتح المساعدة.")
    return SELECT_AMOUNT


async def amount_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.upsert_user(update)
    text = (update.message.text or "").strip()
    amount = parse_amount(text)
    await event_logger.log(context.bot, f"💬 المستخدم {user_label(update)} أدخل المبلغ: {sanitize_for_log(text)}")
    if amount is None:
        await update.message.reply_text("الرجاء إرسال مبلغ صحيح بدون كلمات، مثال: 9999 أو 9,999")
        return SELECT_AMOUNT

    context.user_data["amount"] = amount
    context.user_data["raw_amount_text"] = text
    await update.message.reply_text(
        f"تم استلام المبلغ: {format_number(amount)}\n\nاختر الدولة:",
        reply_markup=country_menu(),
    )
    return SELECT_COUNTRY


async def country_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    country_code = (query.data.split(":", 1)[1] if query and ":" in query.data else "")
    if country_code not in COUNTRIES:
        await reply_text(query or update, "الدولة غير مدعومة.")
        return SELECT_COUNTRY

    context.user_data["country_code"] = country_code
    await event_logger.log(context.bot, f"🎯 المستخدم {user_label(update)} اختار الدولة: {display_country(country_code)}")
    await reply_text(query or update, "أدخل سنة البداية، مثال: 2000")
    return SELECT_START


async def start_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.upsert_user(update)
    text = (update.message.text or "").strip()
    dt = parse_year_or_date(text)
    await event_logger.log(context.bot, f"💬 المستخدم {user_label(update)} أدخل سنة البداية: {sanitize_for_log(text)}")
    if dt is None:
        await update.message.reply_text("الرجاء إرسال سنة صحيحة مثل 2000 أو تاريخ مثل 2000-01-01")
        return SELECT_START

    context.user_data["start_dt"] = dt
    context.user_data["raw_start_text"] = text
    await update.message.reply_text(
        "الآن اختر تاريخ النهاية، أو اضغط «استخدم اليوم» ليتم الحساب حتى تاريخ اليوم الحالي.",
        reply_markup=end_menu(),
    )
    return SELECT_END


async def end_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    end_dt = date.today()
    context.user_data["end_dt"] = end_dt
    context.user_data["raw_end_text"] = "today"
    await event_logger.log(context.bot, f"🕒 المستخدم {user_label(update)} اختار تاريخ النهاية: اليوم الحالي {end_dt.isoformat()}")
    return await finalize_calculation(query or update, context)


async def end_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    await reply_text(query or update, "أرسل التاريخ بصيغة YYYY-MM-DD، مثال: 2026-04-16")
    return SELECT_END


async def end_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.upsert_user(update)
    text = (update.message.text or "").strip()
    dt = parse_year_or_date(text)
    await event_logger.log(context.bot, f"💬 المستخدم {user_label(update)} أدخل تاريخ النهاية: {sanitize_for_log(text)}")
    if dt is None:
        await update.message.reply_text("الرجاء إرسال تاريخ صحيح بصيغة YYYY-MM-DD أو سنة فقط.")
        return SELECT_END
    context.user_data["end_dt"] = dt
    context.user_data["raw_end_text"] = text
    return await finalize_calculation(update.message, context)


async def finalize_calculation(target: Any, context: ContextTypes.DEFAULT_TYPE):
    source_update = target if isinstance(target, Update) else None
    if isinstance(target, Update):
        user = target.effective_user
    elif isinstance(target, (CallbackQuery, Message)):
        user = target.from_user
    else:
        user = None

    user_name = f"@{user.username}" if user and user.username else (f"ID:{user.id}" if user else "unknown")

    amount = context.user_data.get("amount")
    country_code = context.user_data.get("country_code")
    start_dt = context.user_data.get("start_dt")
    end_dt = context.user_data.get("end_dt")

    if not all([amount, country_code, start_dt, end_dt]):
        await reply_text(target, "تعذر إكمال البيانات. ابدأ من جديد باستخدام /start.")
        return ConversationHandler.END

    try:
        result = await asyncio.to_thread(calculate_inflation, country_code, amount, start_dt, end_dt)
    except Exception as e:
        await event_logger.log(context.bot, f"⚠️ خطأ أثناء الحساب لدى المستخدم {user_name}: {sanitize_for_log(str(e))}")
        await reply_text(target, "حدث خطأ أثناء الحساب. حاول مرة أخرى بعد قليل.", reply_markup=back_to_home_menu())
        return ConversationHandler.END

    current_value = result.adjusted_value
    difference = current_value - amount
    inflation_pct = (current_value / amount - 1) * 100

    text = format_result_text(amount, start_dt, end_dt, country_code, result)
    await reply_text(target, text, parse_mode=ParseMode.HTML, reply_markup=back_to_home_menu())

    if user:
        db.increment_requests(user.id)
        db.save_request(
            {
                "user_id": user.id,
                "username": user.username,
                "country_code": country_code,
                "amount": amount,
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat(),
                "provider": result.provider,
                "source_start": result.source_start,
                "source_end": result.source_end,
                "adjusted_value": current_value,
                "difference": difference,
                "inflation_pct": inflation_pct,
                "raw_amount_text": context.user_data.get("raw_amount_text", str(amount)),
                "raw_start_text": context.user_data.get("raw_start_text", start_dt.isoformat()),
                "raw_end_text": context.user_data.get("raw_end_text", end_dt.isoformat()),
            }
        )
        db.save_event(user.id, user.username, "calculation", f"{amount} {country_code} {start_dt.isoformat()} -> {end_dt.isoformat()}")

    await event_logger.log(
        context.bot,
        (
            f"✅ المستخدم {user_name} حصل على النتيجة: "
            f"{format_number(current_value)} | الفرق: {format_number(difference)} | التضخم: {inflation_pct:.2f}%"
        ),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.upsert_user(update)
    reset_session(context)
    await event_logger.log(context.bot, f"⛔ المستخدم {user_label(update)} ألغى العملية.")
    if update.message:
        await update.message.reply_text("تم الإلغاء.", reply_markup=main_menu())
    return ConversationHandler.END


async def nav_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    reset_session(context)
    await reply_text(query or update, WELCOME_TEXT, reply_markup=main_menu())
    await event_logger.log(context.bot, f"🏠 المستخدم {user_label(update)} عاد إلى القائمة الرئيسية.")
    return SELECT_AMOUNT


async def nav_back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    context.user_data.pop("country_code", None)
    context.user_data.pop("start_dt", None)
    context.user_data.pop("end_dt", None)
    await reply_text(query or update, "أرسل المبلغ المراد حسابه، مثال: 9999 أو 9,999")
    await event_logger.log(context.bot, f"↩️ المستخدم {user_label(update)} رجع إلى خطوة المبلغ.")
    return SELECT_AMOUNT


async def nav_back_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    context.user_data.pop("country_code", None)
    context.user_data.pop("start_dt", None)
    context.user_data.pop("end_dt", None)
    await reply_text(query or update, "اختر الدولة:", reply_markup=country_menu())
    await event_logger.log(context.bot, f"↩️ المستخدم {user_label(update)} رجع إلى خطوة الدولة.")
    return SELECT_COUNTRY


# =========================
# أوامر الإدارة
# =========================


def is_admin(update: Update) -> bool:
    return bool(update.effective_user and update.effective_user.id == ADMIN_ID)


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    s = db.stats()
    text = (
        f"📊 <b>إحصاءات البوت</b>\n\n"
        f"عدد المستخدمين: {s['users']}\n"
        f"عدد الطلبات: {s['requests']}\n"
        f"عدد الأحداث: {s['events']}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    rows = db.all_users(limit=20)
    if not rows:
        await update.message.reply_text("لا يوجد مستخدمون بعد.")
        return
    lines = ["👥 <b>آخر المستخدمين</b>\n"]
    for r in rows:
        uname = f"@{html.escape(r['username'])}" if r["username"] else f"ID:{r['user_id']}"
        lines.append(
            f"• {uname} | طلبات: {r['requests_count']} | آخر ظهور: {html.escape(str(r['last_seen']))}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def admin_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    rows = db.recent_requests(limit=10)
    if not rows:
        await update.message.reply_text("لا توجد طلبات بعد.")
        return
    lines = ["🧾 <b>آخر الطلبات</b>\n"]
    for r in rows:
        uname = f"@{html.escape(r['username'])}" if r["username"] else f"ID:{r['user_id']}"
        lines.append(
            f"#{r['id']} | {uname} | {display_country(r['country_code'])} | "
            f"{r['amount']} | {r['start_date']} → {r['end_date']} | "
            f"{r['adjusted_value']:.2f}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def admin_request_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    parts = (update.message.text or "").split()
    if len(parts) != 2:
        await update.message.reply_text("استخدم: /request_details 123")
        return
    try:
        req_id = int(parts[1])
    except ValueError:
        await update.message.reply_text("رقم الطلب غير صحيح.")
        return
    row = db.get_request_by_id(req_id)
    if not row:
        await update.message.reply_text("الطلب غير موجود.")
        return
    uname = f"@{html.escape(row['username'])}" if row["username"] else f"ID:{row['user_id']}"
    text = (
        f"🔎 <b>تفاصيل الطلب #{row['id']}</b>\n\n"
        f"المستخدم: {uname}\n"
        f"الدولة: {display_country(row['country_code'])}\n"
        f"المبلغ: {row['amount']}\n"
        f"البداية: {html.escape(str(row['start_date']))}\n"
        f"النهاية: {html.escape(str(row['end_date']))}\n"
        f"القيمة الحالية: {row['adjusted_value']:.2f}\n"
        f"الفرق: {row['difference']:.2f}\n"
        f"نسبة التضخم: {row['inflation_pct']:.2f}%\n"
        f"المصدر: {html.escape(str(row['provider']))}\n"
        f"الوقت: {html.escape(str(row['created_at']))}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def admin_request_detail_arabic_alias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # يُترك كبديل إذا أرسل المستخدم النص العربي يدويًا، رغم أنه ليس أمرًا قياسيًا في تيليجرام.
    return await admin_request_detail(update, context)


# =========================
# تسجيل الأخطاء
# =========================


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled error: %s", context.error)
    if isinstance(update, Update):
        try:
            await event_logger.log(
                context.bot,
                f"⚠️ خطأ غير متوقع لدى المستخدم {user_label(update)}: {sanitize_for_log(str(context.error))}",
            )
        except Exception:
            pass


# =========================
# بناء التطبيق
# =========================


def build_app() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(menu_start, pattern=r"^menu:start$"),
        ],
        states={
            SELECT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_step),
                CallbackQueryHandler(show_help, pattern=r"^menu:help$"),
            ],
            SELECT_COUNTRY: [
                CallbackQueryHandler(country_step, pattern=r"^country:(us|ca|gb|eg)$"),
                CallbackQueryHandler(nav_back_start, pattern=r"^nav:back_start$"),
            ],
            SELECT_START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_step),
                CallbackQueryHandler(nav_back_country, pattern=r"^nav:back_country$"),
            ],
            SELECT_END: [
                CallbackQueryHandler(end_today, pattern=r"^end:today$"),
                CallbackQueryHandler(end_manual, pattern=r"^end:manual$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, end_step),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(nav_home, pattern=r"^nav:home$"),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("users", admin_users))
    app.add_handler(CommandHandler("requests", admin_requests))
    app.add_handler(CommandHandler("request_details", admin_request_detail))
    app.add_handler(MessageHandler(filters.Regex(r"^/طلب_تفاصيل(?:@\w+)?(?:\s+\d+)?$"), admin_request_detail_arabic_alias))

    app.add_error_handler(error_handler)
    return app


def main():
    logger.info("Starting %s", APP_NAME)
    app = build_app()
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
