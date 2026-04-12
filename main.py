import ssl
import asyncio
import logging
import aiohttp
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes

# ============================================================
# PROTOTIPE DEFINITIONS (INLINE)
# ============================================================
# استيراد مكتبة protobuf الأساسية
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
from google.protobuf import runtime_version as _runtime_version

_sym_db = _symbol_database.Default()

# --- MajorLoginReq ---
DESCRIPTOR_MajorLoginReq = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13MajorLoginReq.proto\"\xfa\n\n\nMajorLogin\x12\x12\n\nevent_time\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x13\n\x0bplatform_id\x18\x05 \x01(\x05\x12\x16\n\x0e\x63lient_version\x18\x07 \x01(\t\x12\x17\n\x0fsystem_software\x18\x08 \x01(\t\x12\x17\n\x0fsystem_hardware\x18\t \x01(\t\x12\x18\n\x10telecom_operator\x18\n \x01(\t\x12\x14\n\x0cnetwork_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\r\x12\x15\n\rscreen_height\x18\r \x01(\r\x12\x12\n\nscreen_dpi\x18\x0e \x01(\t\x12\x19\n\x11processor_details\x18\x0f \x01(\t\x12\x0e\n\x06memory\x18\x10 \x01(\r\x12\x14\n\x0cgpu_renderer\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x18\n\x10unique_device_id\x18\x13 \x01(\t\x12\x11\n\tclient_ip\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0b\x64\x65vice_type\x18\x18 \x01(\t\x12\'\n\x10memory_available\x18\x19 \x01(\x0b\x32\r.GameSecurity\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x1d \x01(\t\x12\x17\n\x0fplatform_sdk_id\x18\x1e \x01(\x05\x12\x1a\n\x12network_operator_a\x18) \x01(\t\x12\x16\n\x0enetwork_type_a\x18* \x01(\t\x12\x1c\n\x14\x63lient_using_version\x18\x39 \x01(\t\x12\x1e\n\x16\x65xternal_storage_total\x18< \x01(\x05\x12\"\n\x1a\x65xternal_storage_available\x18= \x01(\x05\x12\x1e\n\x16internal_storage_total\x18> \x01(\x05\x12\"\n\x1ainternal_storage_available\x18? \x01(\x05\x12#\n\x1bgame_disk_storage_available\x18@ \x01(\x05\x12\x1f\n\x17game_disk_storage_total\x18\x41 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_avail_storage\x18\x42 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_total_storage\x18\x43 \x01(\x05\x12\x10\n\x08login_by\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x12\n\nreg_avatar\x18L \x01(\x05\x12\x15\n\rlibrary_token\x18M \x01(\t\x12\x14\n\x0c\x63hannel_type\x18N \x01(\x05\x12\x10\n\x08\x63pu_type\x18O \x01(\x05\x12\x18\n\x10\x63pu_architecture\x18Q \x01(\t\x12\x1b\n\x13\x63lient_version_code\x18S \x01(\t\x12\x14\n\x0cgraphics_api\x18V \x01(\t\x12\x1d\n\x15supported_astc_bitset\x18W \x01(\r\x12\x1a\n\x12login_open_id_type\x18X \x01(\x05\x12\x18\n\x10\x61nalytics_detail\x18Y \x01(\x0c\x12\x14\n\x0cloading_time\x18\\ \x01(\r\x12\x17\n\x0frelease_channel\x18] \x01(\t\x12\x12\n\nextra_info\x18^ \x01(\t\x12 \n\x18\x61ndroid_engine_init_flag\x18_ \x01(\r\x12\x0f\n\x07if_push\x18\x61 \x01(\x05\x12\x0e\n\x06is_vpn\x18\x62 \x01(\x05\x12\x1c\n\x14origin_platform_type\x18\x63 \x01(\t\x12\x1d\n\x15primary_platform_type\x18\x64 \x01(\t\"5\n\x0cGameSecurity\x12\x0f\n\x07version\x18\x06 \x01(\x05\x12\x14\n\x0chidden_value\x18\x08 \x01(\x04\x62\x06proto3'
)
_globals_MajorLoginReq = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_MajorLoginReq, _globals_MajorLoginReq)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_MajorLoginReq, 'MajorLoginReq_pb2', _globals_MajorLoginReq)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_MajorLoginReq._options = None
    _globals_MajorLoginReq['_MAJORLOGIN']._serialized_start = 24
    _globals_MajorLoginReq['_MAJORLOGIN']._serialized_end = 1426
    _globals_MajorLoginReq['_GAMESECURITY']._serialized_start = 1428
    _globals_MajorLoginReq['_GAMESECURITY']._serialized_end = 1481

MajorLogin = _globals_MajorLoginReq.get('MajorLogin')
GameSecurity = _globals_MajorLoginReq.get('GameSecurity')

# --- MajorLoginRes ---
DESCRIPTOR_MajorLoginRes = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13MajorLoginRes.proto\"\x99\x02\n\rMajorLoginRes\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\r\n\x05token\x18\x02 \x01(\t\x12\x13\n\x0b\x61\x63\x63ount_uid\x18\x03 \x01(\x04\x12\x0b\n\x03key\x18\x04 \x01(\x0c\x12\n\n\x02iv\x18\x05 \x01(\x0c\x12\x11\n\ttimestamp\x18\x06 \x01(\x03\x12\x14\n\x0c\x63ountry_code\x18\x07 \x01(\t\x12\x13\n\x0b\x61sset_bundle\x18\x08 \x01(\t\x12\x18\n\x10\x61nnouncement_url\x18\t \x01(\t\x12\x1a\n\x12maintenance_state\x18\n \x01(\x05\x12\x1a\n\x12\x63lient_kick_reason\x18\x0b \x01(\x05\x12\x14\n\x0c\x61nonymous_key\x18\x0c \x01(\t\x12\x12\n\ndebug_mode\x18\r \x01(\x08\x62\x06proto3'
)
_globals_MajorLoginRes = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_MajorLoginRes, _globals_MajorLoginRes)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_MajorLoginRes, 'MajorLoginRes_pb2', _globals_MajorLoginRes)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_MajorLoginRes._options = None
    _globals_MajorLoginRes['_MAJORLOGINRES']._serialized_start = 24
    _globals_MajorLoginRes['_MAJORLOGINRES']._serialized_end = 305

MajorLoginRes = _globals_MajorLoginRes.get('MajorLoginRes')

# --- GetLoginDataRes ---
DESCRIPTOR_GetLoginDataRes = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x15GetLoginDataRes.proto\"\xa4\x01\n\x0cGetLoginData\x12\x12\n\nAccountUID\x18\x01 \x01(\x04\x12\x0e\n\x06Region\x18\x03 \x01(\t\x12\x13\n\x0b\x41\x63\x63ountName\x18\x04 \x01(\t\x12\x16\n\x0eOnline_IP_Port\x18\x0e \x01(\t\x12\x0f\n\x07\x43lan_ID\x18\x14 \x01(\x03\x12\x16\n\x0e\x41\x63\x63ountIP_Port\x18  \x01(\t\x12\x1a\n\x12\x43lan_Compiled_Data\x18\x37 \x01(\tb\x06proto3'
)
_globals_GetLoginDataRes = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_GetLoginDataRes, _globals_GetLoginDataRes)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_GetLoginDataRes, 'GetLoginDataRes_pb2', _globals_GetLoginDataRes)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_GetLoginDataRes._loaded_options = None
    _globals_GetLoginDataRes['_GETLOGINDATA']._serialized_start = 26
    _globals_GetLoginDataRes['_GETLOGINDATA']._serialized_end = 190

GetLoginData = _globals_GetLoginDataRes.get('GetLoginData')

# ============================================================
# الثوابت والإعدادات
# ============================================================
GARENA_TOKEN_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.common.ggbluefox.com/MajorLogin"
FIXED_AES_KEY = b'Yg&tc%DEuh6%Zc^8'
FIXED_AES_IV = b'6oyZDr22E3ychjM%'

MAJOR_LOGIN_HEADERS = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB53"
}

WAIT_UID, WAIT_PASSWORD = range(2)

# ============================================================
# دوال المصادقة
# ============================================================
async def get_random_user_agent():
    versions = [
        '4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8',
        '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3',
        '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3'
    ]
    models = [
        'SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV',
        'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085',
        'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD',
    ]
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    version = random.choice(versions)
    model = random.choice(models)
    android = random.choice(android_versions)
    lang = random.choice(languages)
    country = random.choice(countries)
    return f"GarenaMSDK/{version}({model};Android {android};{lang};{country};)"

async def encrypted_proto(data_bytes):
    cipher = AES.new(FIXED_AES_KEY, AES.MODE_CBC, FIXED_AES_IV)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)

async def get_access_token(uid, password):
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": await get_random_user_agent(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(GARENA_TOKEN_URL, headers=headers, data=data) as resp:
            if resp.status != 200:
                return None, None
            data = await resp.json()
            return data.get("open_id"), data.get("access_token")

async def build_major_login_payload(open_id, access_token):
    major_login = MajorLogin()
    major_login.event_time = "2025-06-04 19:48:07"
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.123.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    major_login.memory_available.version = 55
    major_login.memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2029123000"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"

    serialized = major_login.SerializeToString()
    return await encrypted_proto(serialized)

async def send_major_login(payload):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(MAJOR_LOGIN_URL, data=payload, headers=MAJOR_LOGIN_HEADERS, ssl=ssl_context) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

def decode_major_login_response(response_bytes):
    proto = MajorLoginRes()
    proto.ParseFromString(response_bytes)
    return proto

async def fetch_login_data(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    headers = MAJOR_LOGIN_HEADERS.copy()
    headers['Authorization'] = f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

def decode_get_login_data_response(response_bytes):
    proto = GetLoginData()
    proto.ParseFromString(response_bytes)
    return proto

async def login_process(uid, password):
    open_id, access_token = await get_access_token(uid, password)
    if not open_id or not access_token:
        return "❌ فشل الحصول على رمز Garena (تأكد من UID/Password)"

    payload = await build_major_login_payload(open_id, access_token)

    major_response = await send_major_login(payload)
    if not major_response:
        return "❌ فشل طلب MajorLogin (الحساب محظور أو غير مسجل)"

    major_data = decode_major_login_response(major_response)
    base_url = major_data.url
    session_token = major_data.token
    account_uid = major_data.account_uid

    login_data_response = await fetch_login_data(base_url, payload, session_token)
    if not login_data_response:
        return "❌ فشل GetLoginData"

    login_data = decode_get_login_data_response(login_data_response)
    online_ip_port = login_data.Online_IP_Port
    account_ip_port = login_data.AccountIP_Port

    return (
        f"✅ **تم تسجيل الدخول بنجاح**\n"
        f"• UID: `{account_uid}`\n"
        f"• Online Server: `{online_ip_port}`\n"
        f"• Account Server: `{account_ip_port}`\n"
        f"• Encryption Key: `{major_data.key.hex()}`\n"
        f"• Encryption IV: `{major_data.iv.hex()}`"
    )

# ============================================================
# بوت تيليجرام
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت تسجيل الدخول لـ Free Fire\n\n"
        "🔐 للبدء، أرسل UID الخاص بك (مثال: 4481906989)\n"
        "أو أرسل /cancel للإلغاء."
    )
    return WAIT_UID

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 تم إلغاء العملية.")
    return ConversationHandler.END

async def receive_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit() or len(uid) < 8:
        await update.message.reply_text("❌ UID غير صالح (يجب أن يكون 8 أرقام على الأقل). حاول مرة أخرى.")
        return WAIT_UID
    context.user_data['uid'] = uid
    await update.message.reply_text("✅ تم استلام UID.\n🔑 الآن أرسل كلمة المرور (Password):")
    return WAIT_PASSWORD

async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    uid = context.user_data['uid']

    await update.message.delete()

    status_msg = await update.message.reply_text("⏳ جاري تسجيل الدخول... يرجى الانتظار.")

    result = await login_process(uid, password)

    await status_msg.edit_text(result, parse_mode="Markdown")
    return ConversationHandler.END

def main():
    logging.basicConfig(level=logging.INFO)
    # استبدل بالتوكن الصحيح
    application = Application.builder().token("8769355202:AAEJFIXicyJNdhor2HM98daIUQ9wFZd0mwY").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_uid)],
            WAIT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    print("🤖 البوت يعمل...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()