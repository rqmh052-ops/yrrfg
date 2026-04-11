#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Free Fire - Login Script Only (No Spam, No Bot)
يستخدم نفس بروتوكولات MajorLogin و GetLoginData من الملف الأصلي.
"""

import asyncio
import ssl
import base64
import time
import random
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from google.protobuf import descriptor_pool
from google.protobuf import symbol_database
from google.protobuf.internal import builder

# ====================== ثوابت التشفير الثابتة (مستخدمة في MajorLogin) ======================
STATIC_KEY = b'Yg&tc%DEuh6%Zc^8'
STATIC_IV  = b'6oyZDr22E3ychjM%'

# ====================== تعريفات Protobuf (من الملف الأصلي) ======================
# تم استخراجها من نهاية main.py
# MajorLoginReq.proto
_REQ_DESCRIPTOR = descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginReq.proto\"\xfa\n\n\nMajorLogin\x12\x12\n\nevent_time\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x13\n\x0bplatform_id\x18\x05 \x01(\x05\x12\x16\n\x0e\x63lient_version\x18\x07 \x01(\t\x12\x17\n\x0fsystem_software\x18\x08 \x01(\t\x12\x17\n\x0fsystem_hardware\x18\t \x01(\t\x12\x18\n\x10telecom_operator\x18\n \x01(\t\x12\x14\n\x0cnetwork_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\r\x12\x15\n\rscreen_height\x18\r \x01(\r\x12\x12\n\nscreen_dpi\x18\x0e \x01(\t\x12\x19\n\x11processor_details\x18\x0f \x01(\t\x12\x0e\n\x06memory\x18\x10 \x01(\r\x12\x14\n\x0cgpu_renderer\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x18\n\x10unique_device_id\x18\x13 \x01(\t\x12\x11\n\tclient_ip\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0b\x64\x65vice_type\x18\x18 \x01(\t\x12\'\n\x10memory_available\x18\x19 \x01(\x0b\x32\r.GameSecurity\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x1d \x01(\t\x12\x17\n\x0fplatform_sdk_id\x18\x1e \x01(\x05\x12\x1a\n\x12network_operator_a\x18) \x01(\t\x12\x16\n\x0enetwork_type_a\x18* \x01(\t\x12\x1c\n\x14\x63lient_using_version\x18\x39 \x01(\t\x12\x1e\n\x16\x65xternal_storage_total\x18< \x01(\x05\x12\"\n\x1a\x65xternal_storage_available\x18= \x01(\x05\x12\x1e\n\x16internal_storage_total\x18> \x01(\x05\x12\"\n\x1ainternal_storage_available\x18? \x01(\x05\x12#\n\x1bgame_disk_storage_available\x18@ \x01(\x05\x12\x1f\n\x17game_disk_storage_total\x18\x41 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_avail_storage\x18\x42 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_total_storage\x18\x43 \x01(\x05\x12\x10\n\x08login_by\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x12\n\nreg_avatar\x18L \x01(\x05\x12\x15\n\rlibrary_token\x18M \x01(\t\x12\x14\n\x0c\x63hannel_type\x18N \x01(\x05\x12\x10\n\x08\x63pu_type\x18O \x01(\x05\x12\x18\n\x10\x63pu_architecture\x18Q \x01(\t\x12\x1b\n\x13\x63lient_version_code\x18S \x01(\t\x12\x14\n\x0cgraphics_api\x18V \x01(\t\x12\x1d\n\x15supported_astc_bitset\x18W \x01(\r\x12\x1a\n\x12login_open_id_type\x18X \x01(\x05\x12\x18\n\x10\x61nalytics_detail\x18Y \x01(\x0c\x12\x14\n\x0cloading_time\x18\\ \x01(\r\x12\x17\n\x0frelease_channel\x18] \x01(\t\x12\x12\n\nextra_info\x18^ \x01(\t\x12 \n\x18\x61ndroid_engine_init_flag\x18_ \x01(\r\x12\x0f\n\x07if_push\x18\x61 \x01(\x05\x12\x0e\n\x06is_vpn\x18\x62 \x01(\x05\x12\x1c\n\x14origin_platform_type\x18\x63 \x01(\t\x12\x1d\n\x15primary_platform_type\x18\x64 \x01(\t\"5\n\x0cGameSecurity\x12\x0f\n\x07version\x18\x06 \x01(\x05\x12\x14\n\x0chidden_value\x18\x08 \x01(\x04\x62\x06proto3')
# MajorLoginRes.proto (من الملف الأصلي، ولكن لم يكن موجوداً كنص، سأستخدم ما هو مستخدم في الكود)
# في الكود الأصلي: MajorLoginRes_pb2 تم استيراده، لكنه غير موجود في الملف المرفق كنص protobuf.
# بالبحث في الملف، لم أجد تعريف MajorLoginRes.proto. سأقوم بإنشائه من بنية الكود المستخدمة.
# بدلاً من ذلك، سأستخدم دالة MajorLogin_Decode الموجودة في الكود الأصلي والتي تستخدم مكتبة protobuf مع رسالة مفترضة.
# لتجنب التعقيد، سأقوم بتضمين تعريف MajorLoginRes يدوياً بناءً على الحقول المستخدمة في الكود:
# fields: url, token, account_uid, key, iv, timestamp
_RES_DESCRIPTOR = descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"Y\n\x0cMajorLoginRes\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\r\n\x05token\x18\x02 \x01(\t\x12\x13\n\x0b\x61\x63\x63ount_uid\x18\x03 \x01(\x04\x12\x0b\n\x03key\x18\x04 \x01(\x0c\x12\n\n\x02iv\x18\x05 \x01(\x0c\x12\x11\n\ttimestamp\x18\x06 \x01(\x03')
# GetLoginDataRes.proto (موجود في الملف)
_RES_DATA_DESCRIPTOR = descriptor_pool.Default().AddSerializedFile(b'\n\x15GetLoginDataRes.proto\"\xa4\x01\n\x0cGetLoginData\x12\x12\n\nAccountUID\x18\x01 \x01(\x04\x12\x0e\n\x06Region\x18\x03 \x01(\t\x12\x13\n\x0b\x41\x63\x63ountName\x18\x04 \x01(\t\x12\x16\n\x0eOnline_IP_Port\x18\x0e \x01(\t\x12\x0f\n\x07\x43lan_ID\x18\x14 \x01(\x03\x12\x16\n\x0e\x41\x63\x63ountIP_Port\x18  \x01(\t\x12\x1a\n\x12\x43lan_Compiled_Data\x18\x37 \x01(\t')

# بناء الرسائل
from google.protobuf import message
_sym_db = symbol_database.Default()
builder.BuildMessageAndEnumDescriptors(_REQ_DESCRIPTOR, globals())
builder.BuildTopDescriptorsAndMessages(_REQ_DESCRIPTOR, 'MajorLoginReq_pb2', globals())
builder.BuildMessageAndEnumDescriptors(_RES_DESCRIPTOR, globals())
builder.BuildTopDescriptorsAndMessages(_RES_DESCRIPTOR, 'MajorLoginRes_pb2', globals())
builder.BuildMessageAndEnumDescriptors(_RES_DATA_DESCRIPTOR, globals())
builder.BuildTopDescriptorsAndMessages(_RES_DATA_DESCRIPTOR, 'GetLoginDataRes_pb2', globals())

# استيراد الفئات بعد بنائها
MajorLoginReq = globals()['MajorLogin']
MajorLoginRes = globals()['MajorLoginRes']
GetLoginDataRes = globals()['GetLoginData']

# ====================== دوال مساعدة ======================
async def get_random_user_agent():
    versions = ['4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8', '4.2.3P1', '5.0.1B2']
    models = ['SM-A125F', 'SM-A225F', 'SM-A325M', 'Redmi 9A', 'POCO M3', 'RMX2185', 'moto g(9) play']
    android_versions = ['9', '10', '11', '12']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID']
    countries = ['USA', 'MEX', 'BRA', 'IDN']
    version = random.choice(versions)
    model = random.choice(models)
    android = random.choice(android_versions)
    lang = random.choice(languages)
    country = random.choice(countries)
    return f"GarenaMSDK/{version}({model};Android {android};{lang};{country};)"

async def encrypted_proto(encoded_hex):
    """تشفير البيانات باستخدام AES-CBC مع المفاتيح الثابتة"""
    cipher = AES.new(STATIC_KEY, AES.MODE_CBC, STATIC_IV)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

async def base_to_hex(timestamp):
    result = hex(timestamp)[2:]
    if len(result) == 1:
        result = "0" + result
    return result

# ====================== دوال تسجيل الدخول الأساسية ======================
async def get_access_token(uid, password):
    """الحصول على open_id و access_token من OAuth"""
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
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
        async with session.post(url, headers=headers, data=data) as resp:
            if resp.status != 200:
                return None, None
            data = await resp.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return open_id, access_token

async def MajorLoginProto_Encode(open_id, access_token):
    """بناء وتشفير رسالة MajorLogin"""
    major_login = MajorLoginReq()
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

async def MajorLogin(payload):
    url = "https://loginbp.common.ggbluefox.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None

async def MajorLogin_Decode(data):
    proto = MajorLoginRes()
    proto.ParseFromString(data)
    return proto

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53",
        'Authorization': f"Bearer {token}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None

async def GetLoginData_Decode(data):
    proto = GetLoginDataRes()
    proto.ParseFromString(data)
    return proto

async def get_encrypted_startup(account_uid, token, timestamp, key, iv):
    """بناء حزمة startup المشفرة (غير مستخدمة في تسجيل الدخول الأساسي ولكنها تعرض المعلومات)"""
    uid_hex = hex(account_uid)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await base_to_hex(timestamp)
    # التشفير باستخدام key و iv المستلمين (مختلفين عن STATIC)
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_token = cipher.encrypt(pad(token.encode(), AES.block_size))
    encrypted_token_hex = encrypted_token.hex()
    encrypted_packet_length = hex(len(encrypted_token_hex)//2)[2:]
    if uid_length == 7:
        headers = '000000000'
    elif uid_length == 8:
        headers = '00000000'
    elif uid_length == 9:
        headers = '0000000'
    elif uid_length == 10:
        headers = '000000'
    elif uid_length == 11:
        headers = '00000'
    else:
        headers = '0000000'
    packet = f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_token_hex}"
    return packet

# ====================== الدالة الرئيسية لتسجيل الدخول ======================
async def login(uid: str, password: str):
    """
    تقوم بتسجيل الدخول إلى Free Fire وتعيد معلومات الجلسة.
    """
    print("[1] الحصول على access_token...")
    open_id, access_token = await get_access_token(uid, password)
    if not open_id or not access_token:
        print("❌ فشل في الحصول على access_token. تحقق من بيانات الحساب.")
        return None

    print("[2] بناء MajorLogin payload...")
    payload = await MajorLoginProto_Encode(open_id, access_token)

    print("[3] إرسال MajorLogin...")
    response = await MajorLogin(payload)
    if not response:
        print("❌ الحساب محظور أو غير مسجل.")
        return None

    print("[4] فك تشفير الرد...")
    decoded = await MajorLogin_Decode(response)
    base_url = decoded.url
    token = decoded.token
    account_uid = decoded.account_uid
    key = decoded.key
    iv = decoded.iv
    timestamp = decoded.timestamp

    print(f"✅ تم تسجيل الدخول بنجاح! UID: {account_uid}")
    print(f"   Base URL: {base_url}")
    print(f"   Token: {token[:30]}...")
    print(f"   Key: {key.hex()}")
    print(f"   IV: {iv.hex()}")

    print("[5] الحصول على بيانات GetLoginData...")
    get_data_resp = await GetLoginData(base_url, payload, token)
    if get_data_resp:
        decoded_data = await GetLoginData_Decode(get_data_resp)
        online_ip_port = decoded_data.Online_IP_Port
        account_ip_port = decoded_data.AccountIP_Port
        print(f"   Online IP:Port = {online_ip_port}")
        print(f"   Account IP:Port = {account_ip_port}")
        # يمكن بناء حزمة startup إذا أردت (للاتصال بالدردشة)
        # startup = await get_encrypted_startup(account_uid, token, timestamp, key, iv)
        # print(f"   Startup packet (hex): {startup[:100]}...")
    else:
        print("⚠️ لم يتم الحصول على GetLoginData (قد يكون غير ضروري)")

    return {
        "account_uid": account_uid,
        "token": token,
        "base_url": base_url,
        "key": key,
        "iv": iv,
        "timestamp": timestamp,
        "online_ip_port": online_ip_port if get_data_resp else None,
        "account_ip_port": account_ip_port if get_data_resp else None,
    }

async def main():
    # استخدم بيانات الاعتماد الخاصة بك
    UID = "4481906989"
    PASSWORD = "C415F8D7DCB735D2B2BC52302526B939B3CACEAE2BAB21390050DD0B91789F89"

    result = await login(UID, PASSWORD)
    if result:
        print("\n🎉 تمت عملية تسجيل الدخول بنجاح! يمكنك استخدام هذه المعلومات لاحقاً.")
    else:
        print("\n💥 فشل تسجيل الدخول.")

if __name__ == "__main__":
    asyncio.run(main())