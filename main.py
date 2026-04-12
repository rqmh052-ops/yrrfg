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
# PROTOTIPE DEFINITIONS (INLINE) – مصححة بالكامل
# ============================================================
from google.protobuf import descriptor_pb2
from google.protobuf import message_factory
from google.protobuf import symbol_database

_sym_db = symbol_database.Default()

# --- MajorLoginReq ---
DESCRIPTOR_MajorLoginReq = descriptor_pb2.FileDescriptorProto()
DESCRIPTOR_MajorLoginReq.name = 'MajorLoginReq.proto'
DESCRIPTOR_MajorLoginReq.package = ''
DESCRIPTOR_MajorLoginReq.syntax = 'proto3'

# Message MajorLogin
msg_major_login = DESCRIPTOR_MajorLoginReq.message_type.add()
msg_major_login.name = 'MajorLogin'
# event_time
field = msg_major_login.field.add()
field.name = 'event_time'; field.number = 3; field.type = 9; field.label = 1
# game_name
field = msg_major_login.field.add()
field.name = 'game_name'; field.number = 4; field.type = 9; field.label = 1
# platform_id
field = msg_major_login.field.add()
field.name = 'platform_id'; field.number = 5; field.type = 5; field.label = 1
# client_version
field = msg_major_login.field.add()
field.name = 'client_version'; field.number = 7; field.type = 9; field.label = 1
# system_software
field = msg_major_login.field.add()
field.name = 'system_software'; field.number = 8; field.type = 9; field.label = 1
# system_hardware
field = msg_major_login.field.add()
field.name = 'system_hardware'; field.number = 9; field.type = 9; field.label = 1
# telecom_operator
field = msg_major_login.field.add()
field.name = 'telecom_operator'; field.number = 10; field.type = 9; field.label = 1
# network_type
field = msg_major_login.field.add()
field.name = 'network_type'; field.number = 11; field.type = 9; field.label = 1
# screen_width
field = msg_major_login.field.add()
field.name = 'screen_width'; field.number = 12; field.type = 13; field.label = 1
# screen_height
field = msg_major_login.field.add()
field.name = 'screen_height'; field.number = 13; field.type = 13; field.label = 1
# screen_dpi
field = msg_major_login.field.add()
field.name = 'screen_dpi'; field.number = 14; field.type = 9; field.label = 1
# processor_details
field = msg_major_login.field.add()
field.name = 'processor_details'; field.number = 15; field.type = 9; field.label = 1
# memory
field = msg_major_login.field.add()
field.name = 'memory'; field.number = 16; field.type = 13; field.label = 1
# gpu_renderer
field = msg_major_login.field.add()
field.name = 'gpu_renderer'; field.number = 17; field.type = 9; field.label = 1
# gpu_version
field = msg_major_login.field.add()
field.name = 'gpu_version'; field.number = 18; field.type = 9; field.label = 1
# unique_device_id
field = msg_major_login.field.add()
field.name = 'unique_device_id'; field.number = 19; field.type = 9; field.label = 1
# client_ip
field = msg_major_login.field.add()
field.name = 'client_ip'; field.number = 20; field.type = 9; field.label = 1
# language
field = msg_major_login.field.add()
field.name = 'language'; field.number = 21; field.type = 9; field.label = 1
# open_id
field = msg_major_login.field.add()
field.name = 'open_id'; field.number = 22; field.type = 9; field.label = 1
# open_id_type
field = msg_major_login.field.add()
field.name = 'open_id_type'; field.number = 23; field.type = 9; field.label = 1
# device_type
field = msg_major_login.field.add()
field.name = 'device_type'; field.number = 24; field.type = 9; field.label = 1
# memory_available (nested message)
nested_msg = msg_major_login.nested_type.add()
nested_msg.name = 'GameSecurity'
field = nested_msg.field.add()
field.name = 'version'; field.number = 6; field.type = 5; field.label = 1
field = nested_msg.field.add()
field.name = 'hidden_value'; field.number = 8; field.type = 4; field.label = 1
field = msg_major_login.field.add()
field.name = 'memory_available'; field.number = 25; field.type = 11; field.label = 1; field.type_name = '.MajorLogin.GameSecurity'
# access_token
field = msg_major_login.field.add()
field.name = 'access_token'; field.number = 29; field.type = 9; field.label = 1
# platform_sdk_id
field = msg_major_login.field.add()
field.name = 'platform_sdk_id'; field.number = 30; field.type = 5; field.label = 1
# network_operator_a
field = msg_major_login.field.add()
field.name = 'network_operator_a'; field.number = 41; field.type = 9; field.label = 1
# network_type_a
field = msg_major_login.field.add()
field.name = 'network_type_a'; field.number = 42; field.type = 9; field.label = 1
# client_using_version
field = msg_major_login.field.add()
field.name = 'client_using_version'; field.number = 57; field.type = 9; field.label = 1
# external_storage_total
field = msg_major_login.field.add()
field.name = 'external_storage_total'; field.number = 60; field.type = 5; field.label = 1
# external_storage_available
field = msg_major_login.field.add()
field.name = 'external_storage_available'; field.number = 61; field.type = 5; field.label = 1
# internal_storage_total
field = msg_major_login.field.add()
field.name = 'internal_storage_total'; field.number = 62; field.type = 5; field.label = 1
# internal_storage_available
field = msg_major_login.field.add()
field.name = 'internal_storage_available'; field.number = 63; field.type = 5; field.label = 1
# game_disk_storage_available
field = msg_major_login.field.add()
field.name = 'game_disk_storage_available'; field.number = 64; field.type = 5; field.label = 1
# game_disk_storage_total
field = msg_major_login.field.add()
field.name = 'game_disk_storage_total'; field.number = 65; field.type = 5; field.label = 1
# external_sdcard_avail_storage
field = msg_major_login.field.add()
field.name = 'external_sdcard_avail_storage'; field.number = 66; field.type = 5; field.label = 1
# external_sdcard_total_storage
field = msg_major_login.field.add()
field.name = 'external_sdcard_total_storage'; field.number = 67; field.type = 5; field.label = 1
# login_by
field = msg_major_login.field.add()
field.name = 'login_by'; field.number = 73; field.type = 5; field.label = 1
# library_path
field = msg_major_login.field.add()
field.name = 'library_path'; field.number = 74; field.type = 9; field.label = 1
# reg_avatar
field = msg_major_login.field.add()
field.name = 'reg_avatar'; field.number = 76; field.type = 5; field.label = 1
# library_token
field = msg_major_login.field.add()
field.name = 'library_token'; field.number = 77; field.type = 9; field.label = 1
# channel_type
field = msg_major_login.field.add()
field.name = 'channel_type'; field.number = 78; field.type = 5; field.label = 1
# cpu_type
field = msg_major_login.field.add()
field.name = 'cpu_type'; field.number = 79; field.type = 5; field.label = 1
# cpu_architecture
field = msg_major_login.field.add()
field.name = 'cpu_architecture'; field.number = 81; field.type = 9; field.label = 1
# client_version_code
field = msg_major_login.field.add()
field.name = 'client_version_code'; field.number = 83; field.type = 9; field.label = 1
# graphics_api
field = msg_major_login.field.add()
field.name = 'graphics_api'; field.number = 86; field.type = 9; field.label = 1
# supported_astc_bitset
field = msg_major_login.field.add()
field.name = 'supported_astc_bitset'; field.number = 87; field.type = 13; field.label = 1
# login_open_id_type
field = msg_major_login.field.add()
field.name = 'login_open_id_type'; field.number = 88; field.type = 5; field.label = 1
# analytics_detail
field = msg_major_login.field.add()
field.name = 'analytics_detail'; field.number = 89; field.type = 12; field.label = 1
# loading_time
field = msg_major_login.field.add()
field.name = 'loading_time'; field.number = 92; field.type = 13; field.label = 1
# release_channel
field = msg_major_login.field.add()
field.name = 'release_channel'; field.number = 93; field.type = 9; field.label = 1
# extra_info
field = msg_major_login.field.add()
field.name = 'extra_info'; field.number = 94; field.type = 9; field.label = 1
# android_engine_init_flag
field = msg_major_login.field.add()
field.name = 'android_engine_init_flag'; field.number = 95; field.type = 13; field.label = 1
# if_push
field = msg_major_login.field.add()
field.name = 'if_push'; field.number = 97; field.type = 5; field.label = 1
# is_vpn
field = msg_major_login.field.add()
field.name = 'is_vpn'; field.number = 98; field.type = 5; field.label = 1
# origin_platform_type
field = msg_major_login.field.add()
field.name = 'origin_platform_type'; field.number = 99; field.type = 9; field.label = 1
# primary_platform_type
field = msg_major_login.field.add()
field.name = 'primary_platform_type'; field.number = 100; field.type = 9; field.label = 1

# --- MajorLoginRes ---
DESCRIPTOR_MajorLoginRes = descriptor_pb2.FileDescriptorProto()
DESCRIPTOR_MajorLoginRes.name = 'MajorLoginRes.proto'
DESCRIPTOR_MajorLoginRes.package = ''
DESCRIPTOR_MajorLoginRes.syntax = 'proto3'

msg_major_login_res = DESCRIPTOR_MajorLoginRes.message_type.add()
msg_major_login_res.name = 'MajorLoginRes'
field = msg_major_login_res.field.add()
field.name = 'url'; field.number = 1; field.type = 9; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'token'; field.number = 2; field.type = 9; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'account_uid'; field.number = 3; field.type = 4; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'key'; field.number = 4; field.type = 12; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'iv'; field.number = 5; field.type = 12; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'timestamp'; field.number = 6; field.type = 3; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'country_code'; field.number = 7; field.type = 9; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'asset_bundle'; field.number = 8; field.type = 9; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'announcement_url'; field.number = 9; field.type = 9; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'maintenance_state'; field.number = 10; field.type = 5; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'client_kick_reason'; field.number = 11; field.type = 5; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'anonymous_key'; field.number = 12; field.type = 9; field.label = 1
field = msg_major_login_res.field.add()
field.name = 'debug_mode'; field.number = 13; field.type = 8; field.label = 1

# --- GetLoginDataRes ---
DESCRIPTOR_GetLoginDataRes = descriptor_pb2.FileDescriptorProto()
DESCRIPTOR_GetLoginDataRes.name = 'GetLoginDataRes.proto'
DESCRIPTOR_GetLoginDataRes.package = ''
DESCRIPTOR_GetLoginDataRes.syntax = 'proto3'

msg_get_login_data = DESCRIPTOR_GetLoginDataRes.message_type.add()
msg_get_login_data.name = 'GetLoginData'
field = msg_get_login_data.field.add()
field.name = 'AccountUID'; field.number = 1; field.type = 4; field.label = 1
field = msg_get_login_data.field.add()
field.name = 'Region'; field.number = 3; field.type = 9; field.label = 1
field = msg_get_login_data.field.add()
field.name = 'AccountName'; field.number = 4; field.type = 9; field.label = 1
field = msg_get_login_data.field.add()
field.name = 'Online_IP_Port'; field.number = 14; field.type = 9; field.label = 1
field = msg_get_login_data.field.add()
field.name = 'Clan_ID'; field.number = 20; field.type = 3; field.label = 1
field = msg_get_login_data.field.add()
field.name = 'AccountIP_Port'; field.number = 32; field.type = 9; field.label = 1
field = msg_get_login_data.field.add()
field.name = 'Clan_Compiled_Data'; field.number = 55; field.type = 9; field.label = 1

# بناء الـ descriptors
from google.protobuf import descriptor_pool as _descriptor_pool
_pool = _descriptor_pool.Default()
_pool.AddSerializedFile(DESCRIPTOR_MajorLoginReq.SerializeToString())
_pool.AddSerializedFile(DESCRIPTOR_MajorLoginRes.SerializeToString())
_pool.AddSerializedFile(DESCRIPTOR_GetLoginDataRes.SerializeToString())

MajorLogin = _pool.FindMessageTypeByName('MajorLogin')
MajorLoginRes = _pool.FindMessageTypeByName('MajorLoginRes')
GetLoginData = _pool.FindMessageTypeByName('GetLoginData')

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
    major_login = _sym_db.GetMessageClass(MajorLogin)()
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
    proto = _sym_db.GetMessageClass(MajorLoginRes)()
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
    proto = _sym_db.GetMessageClass(GetLoginData)()
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

#============================================================
#بوت تيليجرام
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