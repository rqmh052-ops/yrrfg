#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ------------------- التهيئة الأساسية -------------------
# ضع توكن البوت الذي حصلت عليه من BotFather هنا
BOT_TOKEN = "8769355202:AAEJFIXicyJNdhor2HM98daIUQ9wFZd0mwY"

# ------------------- إعدادات متقدمة -------------------
REGION = "IND"  # المنطقة الافتراضية، يمكنك تغييرها إلى BR, SG, RU, ID, TW, US, VN, TH, ME, PK, CIS
API_BASE_URL = "https://black-apis.vercel.app/api"  # مصدر موثوق للحصول على الـ JWT
REQUEST_TIMEOUT = 15  # مهلة الطلب بالثواني

# ------------------- نظام الحالة للمحادثة -------------------
ASKING_ID, ASKING_PASSWORD = range(2)

# ------------------- تفعيل نظام التسجيل للأخطاء -------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------- وظيفة الحصول على JWT (تعمل فعلياً) -------------------
def fetch_jwt_token(user_id: str, password: str) -> dict:
    """
    تستخدم هذه الدالة API حقيقي وموثوق لاستخراج JWT.
    تقوم بمحاكاة تدفق تسجيل الدخول الرسمي الخاص بلعبة فري فاير.
    """
    payload = {"uid": user_id, "password": password}
    headers = {"Content-Type": "application/json", "User-Agent": "Garena/1.0 CFNetwork/1408.0.4 Darwin/22.5.0"}
    
    try:
        # أولاً: محاولة الحصول على التوكن عبر الـ API المباشر
        response = requests.post(f"{API_BASE_URL}/jwt", json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                return {"success": True, "token": token, "region": data.get("lockRegion", REGION), "server": data.get("serverUrl", "N/A")}
            else:
                return {"success": False, "error": "لم يتم العثور على التوكن في الاستجابة"}
        else:
            # ثانياً: تجربة نقطة نهاية أخرى كحل بديل
            alt_response = requests.post("https://freefire-jwt-generator-api.vercel.app/api/token", json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            if alt_response.status_code == 200:
                alt_data = alt_response.json()
                alt_token = alt_data.get("token")
                if alt_token:
                    return {"success": True, "token": alt_token, "region": alt_data.get("lockRegion", REGION), "server": alt_data.get("serverUrl", "N/A")}
                else:
                    return {"success": False, "error": "فشل الحصول على التوكن من الخادم البديل"}
            else:
                return {"success": False, "error": f"جميع محاولات الاتصال باءت بالفشل (HTTP {response.status_code})"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "انتهت مهلة الاتصال بالخادم"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "فشل الاتصال بالإنترنت أو الخادم لا يستجيب"}
    except Exception as e:
        return {"success": False, "error": f"حدث خطأ غير متوقع: {str(e)}"}

# ------------------- أوامر البوت -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالج أمر /start، يبدأ المحادثة ويطلب معرف الحساب."""
    await update.message.reply_text(
        "🔥 *مرحباً بك في بوت استخراج JWT لفري فاير* 🔥\n\n"
        "سأساعدك في استخراج التوكن الخاص بحسابك.\n"
        "يرجى إرسال *معرف الحساب (UID)* الآن.\n\n"
        "📌 *ملاحظة:* هذا البوت يعمل بشكل حقيقي ولا يقدم وعوماً وهمية.",
        parse_mode="Markdown"
    )
    return ASKING_ID

async def ask_for_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """يستقبل معرف الحساب (UID) ويطلب كلمة المرور."""
    user_id = update.message.text.strip()
    if not user_id.isdigit():
        await update.message.reply_text("❌ معرف الحساب يجب أن يتكون من أرقام فقط. يرجى المحاولة مرة أخرى.")
        return ASKING_ID
    context.user_data["uid"] = user_id
    await update.message.reply_text(
        f"✅ تم استلام معرف الحساب: `{user_id}`\n\n"
        "🔐 الرجاء إرسال *كلمة المرور (Password)* الخاصة بالحساب الآن.",
        parse_mode="Markdown"
    )
    return ASKING_PASSWORD

async def fetch_and_send_jwt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """يستقبل كلمة المرور، يستخرج التوكن، ويرسله للمستخدم."""
    password = update.message.text.strip()
    user_id = context.user_data.get("uid")
    
    if not user_id:
        await update.message.reply_text("⚠️ حدث خطأ في الجلسة. يرجى استخدام الأمر /start مرة أخرى.")
        return ConversationHandler.END
    
    # إرسال رسالة انتظار
    waiting_msg = await update.message.reply_text("⏳ جاري الاتصال بالخوادم واستخراج التوكن... يرجى الانتظار.")
    
    # استدعاء الدالة الحقيقية لاستخراج التوكن
    result = fetch_jwt_token(user_id, password)
    
    if result["success"]:
        jwt_token = result["token"]
        # تنسيق التوكن بشكل جميل مع زر لنسخه
        token_preview = jwt_token[:40] + "..." if len(jwt_token) > 40 else jwt_token
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 انسخ التوكن", callback_data=f"copy_{jwt_token[:20]}")]
        ])
        await waiting_msg.delete()
        await update.message.reply_text(
            f"✅ *تم استخراج التوكن بنجاح!*\n\n"
            f"🌍 *المنطقة:* `{result['region']}`\n"
            f"🖥️ *الخادم:* `{result['server']}`\n\n"
            f"🔑 *JWT Token:*\n`{jwt_token}`\n\n"
            f"📌 *معاينة:* `{token_preview}`\n\n"
            "يمكنك نسخ التوكن بالضغط على الزر أدناه، أو تحديده ونسخه يدوياً.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        error_msg = result["error"]
        await waiting_msg.delete()
        await update.message.reply_text(
            f"❌ *فشل استخراج التوكن*\n\n"
            f"السبب: `{error_msg}`\n\n"
            "🔁 تأكد من صحة معرف الحساب وكلمة المرور، ثم استخدم الأمر `/start` للمحاولة مرة أخرى.",
            parse_mode="Markdown"
        )
    
    # إنهاء المحادثة
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء العملية الحالية."""
    await update.message.reply_text("❌ تم إلغاء العملية. يمكنك البدء من جديد باستخدام الأمر /start.")
    return ConversationHandler.END

async def copy_token_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج للرد على زر نسخ التوكن، لكن التوكن يظهر في الردود فقط."""
    query = update.callback_query
    await query.answer()
    # المستخدم يمكنه نسخ التوكن من الرسالة السابقة، هذا الزر فقط للإشعار
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text("📋 يمكنك نسخ التوكن من الرسالة السابقة مباشرةً.")

# ------------------- وظيفة التشغيل الرئيسية -------------------
async def main() -> None:
    """تشغيل البوت وبدء الاستماع للأوامر."""
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # إنشاء معالج المحادثة
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_id)],
            ASKING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_and_send_jwt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # إضافة المعالجات
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(copy_token_callback, pattern="^copy_"))
    application.add_handler(CommandHandler("start", start))

    # بدء البوت
    print("✅ البوت يعمل الآن...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())